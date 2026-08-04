import os
import json
import time
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
MODEL_NAME = "gemini-3.6-flash"

DB_FILE = 'global_vector_db_cache.json'

# ==========================================
# 🔍 データベースの読み込みとインデックス作成 (Ver 12.0 対応版)
# ==========================================
def load_db_indices():
    if not os.path.exists(DB_FILE):
        raise FileNotFoundError(f"{DB_FILE} が見つかりません。")
        
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)

    # 1. 親概念(Level 3) -> Level 4ノード群 のインデックス
    parent_to_l4 = {}
    for c_id, node in db.get('global_concept_nodes', {}).items():
        pc = node.get('parent_concept')
        if pc:
            if pc not in parent_to_l4:
                parent_to_l4[pc] = []
            parent_to_l4[pc].append(node)

    # 2. Level 4 (concept_name) -> 確認問題 のインデックス
    l4_to_qs = {}
    for q_id, q_node in db.get('global_question_nodes', {}).items():
        matched_c = q_node.get('matched_concept')
        if matched_c:
            if matched_c not in l4_to_qs:
                l4_to_qs[matched_c] = []
            l4_to_qs[matched_c].append(q_node)

    return list(parent_to_l4.keys()), parent_to_l4, l4_to_qs

# ==========================================
# 🧠 Geminiによるシラバスマッチング
# ==========================================
def map_syllabus_row(syllabus_text, parent_concepts, max_retries=3):
    concepts_str = "\n".join([f"- {c}" for c in sorted(parent_concepts)])
    sys_instruction = f"""あなたは「高校数学のカリキュラム編成エキスパート」です。
提供された「学校のシラバス（年間授業計画）のテキスト」を読み解き、【スタサプDBの親概念リスト】のどれに該当するかを推論し、指定された厳格なJSON形式で出力してください。

【マッピングの絶対ルール】
1. 省略表現の正確な展開 (Text Expansion)
   - 並列表記は修飾語を分配し正確に補完・分解してからマッピングしてください。
2. 閉世界での選択 (Strict Matching)
   - 抽出する `parent_concept` は、必ず以下のリストに存在する文字列と完全に一致させること。
3. ノイズの除外 (Noise Filtering)
   - 「演習」「テスト」などの数学概念以外のノイズは無視すること。

【スタサプDBの親概念リスト】
{concepts_str}

【出力JSONフォーマット】
{{
  "expanded_topics": ["補完・展開した正確なトピックのリスト"],
  "mapped_concepts": [
    {{
      "parent_concept": "リストから選んだ完全一致の文字列",
      "reasoning": "理由"
    }}
  ]
}}
"""
    prompt = f"【シラバステキスト】: {syllabus_text}"
    
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
            print(f"    ⏳ API通信エラー。{wait_time}秒待機して再試行します... | エラー: {e}")
            time.sleep(wait_time)
            
    return {"expanded_topics": [], "mapped_concepts": []}

# ==========================================
# 🚀 メイン処理 (対話型CLI)
# ==========================================
def main():
    print("🚀 シラバス ➔ コンテンツ可視化テスト (対話型CLI) 起動...\n")
    
    # DBからインデックスをロード
    try:
        parent_list, parent_to_l4, l4_to_qs = load_db_indices()
        print(f"✅ DBロード完了: {len(parent_list)}個の親概念を認識\n")
    except Exception as e:
        print(f"❌ DB読み込みエラー: {e}")
        return

    # 無限ループで入力を待機
    while True:
        print("="*60)
        # ユーザー入力を受け付け
        text = input("📝 シラバスのテキストを入力してください (Enterのみで終了): ")
        
        # Enterのみ（空文字）ならループを抜けて終了
        if not text.strip():
            print("👋 終了します。お疲れ様でした！")
            break
            
        print("="*60)
        
        result = map_syllabus_row(text, parent_list)
        mapped = result.get("mapped_concepts", [])
        
        if not mapped:
            print("  ➔ 該当するコンテンツはありませんでした。")
            continue

        for m in mapped:
            pc = m.get('parent_concept')
            print(f"\n🎯 【親概念(Level 3): {pc}】 (理由: {m.get('reasoning')})")
            
            # 親概念に紐づくLevel 4の取得
            l4_nodes = parent_to_l4.get(pc, [])
            if not l4_nodes:
                print("   ➔ ⚠️ 紐づく学習アクション(Level 4)が見つかりません。")
                continue
                
            print("   🔽 紐づくスタサプコンテンツ (Level 4 / 動画 / 問題)")
            for l4 in l4_nodes:
                c_name = l4.get('concept_name', '')
                branch = l4.get('branch_code', '')
                comp = l4.get('competency', 'unknown')
                
                print(f"   ├─ 🔹 [Level 4: {branch}] {c_name} ({comp})")
                
                # 紐づく動画 (Ver 12.0はLevel 4ノードの中に直接格納されている)
                vids = l4.get('aligned_videos', [])
                if vids:
                    for v in vids:
                        v_file = v.get('video_file', '')
                        start = v.get('start_time', '')
                        end = v.get('end_time', '')
                        role = v.get('alignment_type', 'unknown')
                        print(f"   │    🎥 動画: {v_file} ({start} - {end}) [{role}]")
                else:
                    print("   │    🎥 動画: なし")
                
                # 紐づく問題 (concept_name でマッチング)
                qs = l4_to_qs.get(c_name, [])
                print(f"   │    📝 問題: {len(qs)} 問")
                print("   │")
        
        print("\n") # 見やすさのための改行

if __name__ == "__main__":
    main()