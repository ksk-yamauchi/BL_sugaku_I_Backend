import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==========================================
# ⚙️ 設定
# ==========================================
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ .env に GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-3.6-flash" # 高速かつ指示追従力の高い3.6を使用

DB_FILE = 'global_vector_db_cache.json'
SYLLABUS_FILE = '進度表（数学Ⅰ）.xlsx'

def get_available_parent_concepts():
    """DBから存在する親概念(Level 3)のユニークなリストを取得"""
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    nodes = db_data.get("global_concept_nodes", {})
    parents = set(node.get("parent_concept") for node in nodes.values() if node.get("parent_concept"))
    return sorted(list(parents))

def map_syllabus_row(syllabus_text, parent_concepts, max_retries=3):
    """Gemini APIを使ってシラバスの1行を親概念にマッピング（リトライ機能付き）"""
    print(f"\n📝 ユーザー入力: 「{syllabus_text}」")
    
    concepts_str = "\n".join([f"- {c}" for c in parent_concepts])
    
    sys_instruction = f"""あなたは「高校数学のカリキュラム編成エキスパート」です。
提供された「学校のシラバス（年間授業計画）のテキスト」を読み解き、【スタサプDBの親概念リスト】のどれに該当するかを推論し、指定された厳格なJSON形式で出力してください。

【マッピングの絶対ルール】
1. 省略表現の正確な展開 (Text Expansion)【重要】
   - シラバス特有の並列表記（例：「３次式の展開と因数分解」）は、修飾語を正しく分配し、「３次式の展開」「３次式の因数分解」のように正確なトピックに補完・分解してからマッピングを行ってください。
2. 閉世界での選択 (Strict Matching)
   - 抽出する `parent_concept` は、必ず以下のリストに存在する文字列と完全に一致させること。
3. ノイズの除外 (Noise Filtering)
   - 「演習」「テスト」などの数学概念以外のノイズは無視すること。

【スタサプDBの親概念リスト】
{concepts_str}

【出力JSONフォーマット】
{{
  "expanded_topics": ["補完・展開した正確なトピックのリスト（例: ３次式の展開, ３次式の因数分解, 実数）"],
  "mapped_concepts": [
    {{
      "parent_concept": "リストから選んだ完全一致の文字列",
      "reasoning": "expanded_topics のどのトピックにどう対応するかの理由"
    }}
  ]
}}
"""
    prompt = f"【シラバステキスト】: {syllabus_text}"
    
    # エラー時のリトライ処理
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME, 
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction,
                    response_mime_type="application/json", 
                    temperature=0.1
                )
            )
            return json.loads(response.text)
        except Exception as e:
            wait_time = (attempt + 1) * 5
            print(f"    ⏳ API通信エラー。{wait_time}秒待機して再試行します... ({attempt+1}/{max_retries}) | エラー内容: {e}")
            time.sleep(wait_time)
            
    return {"expanded_topics": [], "mapped_concepts": []}

def main():
    print("🚀 シラバス・マッチング（Level 3 推論）テスト起動...")
    
    # 1. DBから親概念リストの抽出
    parent_concepts = get_available_parent_concepts()
    if not parent_concepts:
        print("⚠️ DBから親概念を取得できませんでした。")
        return
    print(f"✅ スタサプDBから {len(parent_concepts)} 個の親概念(Level 3)を読み込みました。")

    # 2. テスト用シラバスデータの抽出
    try:
        df = pd.read_excel(SYLLABUS_FILE, sheet_name='１Ｖ（数Ⅰ） ', header=None)
        data_rows = df.iloc[5:].copy()
        test_syllabus_texts = data_rows[7].dropna().astype(str).tolist()
    except Exception as e:
        print(f"⚠️ シラバスExcelの読み込みに失敗しました ({e})。モックデータを使用します。")
        test_syllabus_texts = [
            "多項式、多項式の加法と減法および乗法",
            "因数分解",
            "３次式の展開と因数分解、実数",
            "根号を含む式の計算、対称式",
            "２重根号、１次不等式"
        ]

    # 3. 頭の5件だけでテスト実行
    print("🧠 Geminiによるマッピング推論を開始します...")
    for text in test_syllabus_texts[:5]:
        result = map_syllabus_row(text, parent_concepts)
        
        expanded = result.get("expanded_topics", [])
        if expanded:
            print(f"  🔍 展開トピック: {expanded}")
            
        mapped = result.get("mapped_concepts", [])
        if not mapped:
            print("  ➔ 🎯 マッチなし (演習・テスト等のため)")
        else:
            for m in mapped:
                print(f"  ➔ 🎯 【{m.get('parent_concept', 'UNKNOWN')}】 (理由: {m.get('reasoning', '')})")
                
        # API制限(RPM)対策のインターバル
        time.sleep(4)

if __name__ == "__main__":
    main()