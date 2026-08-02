import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

# =========================================================
# ⚙️ 設定・パス定義
# =========================================================
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ .env ファイルに GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=API_KEY)
# 長文の文脈を処理するため、Proモデルを使用（エラーが出る場合は flash に変更してください）
MODEL_NAME = "gemini-3.6-flash" 

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 🌟 CSVではなくExcelファイルを指定
EXCEL_PATH = os.path.join(PARENT_DIR, "mext_code_math_high.xlsx")
MD_PATH = os.path.join(PARENT_DIR, "mext_math_high.md")
OUTPUT_JSON_PATH = os.path.join(PARENT_DIR, "mext_master_dict.json")

# =========================================================
# 📂 データ読み込み ＆ 前処理
# =========================================================
def load_excel_data():
    """Excelから数学Iに関するコードとテキストを抽出"""
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"❌ Excelファイルが見つかりません: {EXCEL_PATH}")
    
    print("📊 Excelファイルを読み込んでいます...")
    # 旧コードの知見を活かし、最初の2行（ヘッダー上部）をスキップして読み込み
    df = pd.read_excel(EXCEL_PATH, skiprows=2, dtype={'学習指導要領コード': str}, engine='openpyxl')
    
    math_items = []
    for _, row in df.iterrows():
        code = str(row.get('学習指導要領コード', '')).strip()
        text = str(row.get('学習指導要領テキスト', '')).strip().replace('\n', ' ')
        
        # 8451... は数学Iのコード（※必要に応じて他のコードも追加可能）
        if code.startswith("8451"):
            math_items.append({
                "code": code,
                "text": text
            })
    return math_items

def load_md_data():
    if not os.path.exists(MD_PATH):
        raise FileNotFoundError(f"❌ Markdownが見つかりません: {MD_PATH}")
    with open(MD_PATH, "r", encoding="utf-8") as f:
        return f.read()

# =========================================================
# 🧠 AIによる辞書統合処理
# =========================================================
def build_master_dictionary(excel_items, md_content):
    print("🧠 Gemini APIを使って、Excelのコード表とMarkdownの解説文を高度に融合しています...")
    print("   (※この処理には数分かかる場合があります)")

    # Excelデータをテキスト化してプロンプトに渡す
    excel_context = "\n".join([f"コード: {item['code']} | テキスト: {item['text']}" for item in excel_items])

    prompt = f"""あなたは文部科学省の学習指導要領を熟知した教育カリキュラムのエキスパートです。
以下の「学習指導要領コード表（抽出データ）」と、「学習指導要領解説（Markdownデータ）」を紐付け、
検索システムやAIが扱いやすい**完全統合版のJSON辞書**を作成してください。

【指示】
抽出データに存在するすべての16桁コードについて、Markdownの解説文からそのコードが意図する「指導のねらい」や「解説」を読み取り、結合してください。

【入力データ1：コード表（数学I）】
{excel_context}

【入力データ2：指導要領解説Markdown】
{md_content[:30000]}

【出力フォーマット】
以下の構造を持つJSONを出力してください。
{{
  "mext_dictionary": [
    {{
      "mext_code": "16桁のコード (例: 8451503110000000)",
      "hierarchy": "階層構造 (例: 高校数学I > 数と式 > 知識・技能)",
      "official_text": "入力データ1に記載されている公式のテキスト",
      "explanation_summary": "Markdownから抽出・要約した、この項目を指導する上でのねらいや詳細な解説"
    }}
  ]
}}
"""
    
    schema = {
        "type": "OBJECT",
        "properties": {
            "mext_dictionary": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "mext_code": {"type": "STRING"},
                        "hierarchy": {"type": "STRING"},
                        "official_text": {"type": "STRING"},
                        "explanation_summary": {"type": "STRING"}
                    },
                    "required": ["mext_code", "hierarchy", "official_text", "explanation_summary"]
                }
            }
        },
        "required": ["mext_dictionary"]
    }

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1,
        ),
    )
    return json.loads(response.text)

# =========================================================
# 🏃‍♂️ メイン処理
# =========================================================
def main():
    print("🚀 指導要領マスター辞書の自動生成を開始します...")
    
    excel_items = load_excel_data()
    print(f"📊 Excelから数学Iの項目を {len(excel_items)} 件抽出しました。")
    
    md_content = load_md_data()
    print(f"📄 Markdown解説データを読み込みました。 (文字数: {len(md_content)})")

    master_dict = build_master_dictionary(excel_items, md_content)

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(master_dict, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 🎉 【成功】マスター辞書の生成が完了しました！")
    print(f"💾 保存先: {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()