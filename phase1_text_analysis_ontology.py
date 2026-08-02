import os
import re
import json
import sys
from glob import glob
from dotenv import load_dotenv
from google import genai
from google.genai import types

# =========================================================
# ⚙️ 設定・初期化 (.env 対応)
# =========================================================
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ .env ファイルに GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-3.6-flash"

md_files = glob("*_clean.md")
if not md_files:
    raise FileNotFoundError("❌ 教材Markdown(*_clean.md)が見つかりません。")
TEXTBOOK_MD_PATH = md_files[0]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

# 🌟 親フォルダで管理する共通マスターファイル群
MEXT_DICT_PATH = os.path.join(PARENT_DIR, "mext_master_dict.json")
BRANCH_MASTER_PATH = os.path.join(PARENT_DIR, "concept_branch_master.json")
INDEX_MASTER_PATH = os.path.join(PARENT_DIR, "lecture_index_master.json")

OUTPUT_DIR = os.path.join(CURRENT_DIR, "output_result")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================
# 📂 単元名（Bundle Name）のマスター参照ロジック
# =========================================================
def get_bundle_name_from_master(folder_name):
    """フォルダ名（例: BL_sugaku_I_03-2）からマスターを参照して正確な単元名を取得"""
    if not os.path.exists(INDEX_MASTER_PATH):
        print("\n❌ 【エラー】 目次マスターが見つかりません。")
        print(f"   先に親フォルダで build_index_master.py を実行して {INDEX_MASTER_PATH} を作成してください。")
        sys.exit(1)
        
    with open(INDEX_MASTER_PATH, "r", encoding="utf-8") as f:
        index_master = json.load(f)

    match = re.search(r"(\d{2}-\d+)", folder_name)
    if not match:
        print(f"\n❌ 【エラー】 フォルダ名 ({folder_name}) から単元番号(XX-Y)を抽出できませんでした。")
        sys.exit(1)
        
    key = match.group(1)
    
    if key not in index_master:
        print(f"\n❌ 【エラー】 マスターファイルに単元 [{key}] の情報が登録されていません。")
        sys.exit(1)
        
    return index_master[key]["bundle_name"]

# =========================================================
# 📂 枝番マスターの一元管理（自動採番ロジック）
# =========================================================
def assign_or_get_branch_code(mext_code, concept_name):
    """グローバルマスターを参照・更新し、一意な枝番(_001等)を決定する"""
    branch_master = {}
    if os.path.exists(BRANCH_MASTER_PATH):
        try:
            with open(BRANCH_MASTER_PATH, "r", encoding="utf-8") as f:
                branch_master = json.load(f)
        except Exception:
            branch_master = {}

    mext_code = str(mext_code).strip()
    if mext_code not in branch_master:
        branch_master[mext_code] = []

    for item in branch_master[mext_code]:
        if item["concept_name"] == concept_name:
            return item["branch_code"]

    existing_nums = []
    for item in branch_master[mext_code]:
        b_code = item.get("branch_code", "_000")
        match = re.search(r"_(\d+)", b_code)
        if match:
            existing_nums.append(int(match.group(1)))
    
    next_num = max(existing_nums) + 1 if existing_nums else 1
    new_branch_code = f"_{next_num:03d}"

    branch_master[mext_code].append({
        "branch_code": new_branch_code,
        "concept_name": concept_name
    })

    with open(BRANCH_MASTER_PATH, "w", encoding="utf-8") as f:
        json.dump(branch_master, f, ensure_ascii=False, indent=2)

    return new_branch_code

# =========================================================
# 📂 Step 0: ファイル読込
# =========================================================
def load_and_prepare_inputs():
    with open(TEXTBOOK_MD_PATH, "r", encoding="utf-8") as f:
        textbook_content = f.read()
        
    folder_name = os.path.basename(CURRENT_DIR)
    bundle_name = get_bundle_name_from_master(folder_name)
    
    if not os.path.exists(MEXT_DICT_PATH):
        raise FileNotFoundError(f"❌ マスター辞書が見つかりません: {MEXT_DICT_PATH}")
        
    with open(MEXT_DICT_PATH, "r", encoding="utf-8") as f:
        mext_master_dict = f.read()
        
    return textbook_content, mext_master_dict, bundle_name

# =========================================================
# 🚀 Step 1: 統合分析プロンプト
# =========================================================
def execute_step1_integrated_analysis(textbook_content, mext_master_dict, bundle_name):
    print(f"\n🚀 [Step 1] 統合分析プロンプトを実行中 ({bundle_name})...")

    prompt = f"""あなたは高等学校数学科の教材分析・アライメントのエキスパートです。
以下の「教材データ」と「指導要領マスター辞書」を解析してください。

【対象単元】: {bundle_name}

【★ルール★】
1. `questions` には、教材内の『確認問題』（および解答）のすべてを抽出してください。
2. `concepts` には、教材で実際に教えられている「独自の細かい概念」を抽出してください。
   ※ 🌟【重要：方向性の明確化】
     「分数を小数で表す」「小数を分数で表す」のように、相互に変換するような類似概念が存在する場合、
     AIのベクトル検索が混同しないように、単なるタイトルだけでなく「割り算（筆算）を実行する」「xとおいて方程式を作る・差をとる」といった【具体的な計算アクション（動作）や処理手順】を `summary` の中に必ず含めて、両者の違いを明確に強調してください。
3. 各 `concept_name` について、【指導要領マスター辞書】の中から最も適切な上位項目を探し、その `mext_code`（16桁）を割り当ててください。
4. `related_concepts` には、一緒に抽出された他の概念の中で関連性の強いものを含めてください。
5. 【重要：内容の取り扱いからの翻り・マージルール】
   『3. 内容の取り扱い』に属する記述（指導要領コードの第9桁が 0 のもの）は、単元の指導上の留意点・指示事項です。
   教材概念が「内容の取り扱い」の文章（例: 分数を小数で表すこと等）に一致した場合でも、その取り扱いテキストが言及している元となる『内容』の本体項目（例: 「内容の(1)のアの(ｱ)については…」とあれば、第9桁が 1:知識・技能 または 2:思考力・判断力等 の本体コード）へ遡り、最も適切な本則コード（第9桁が 1 または 2）を優先して割り当ててください。

---
■ 教材Markdownデータ:
{textbook_content}

---
■ 指導要領マスター辞書 (JSON):
{mext_master_dict}

---
【出力JSONフォーマット】:
{{
  "bundle_name": "{bundle_name}",
  "concepts": [
    {{
      "concept_name": "教材独自の細かい概念名称",
      "summary": "要点・公式の説明（※具体的な計算アクションを強調すること）",
      "mext_code": "辞書から見つけた最も適切な16桁のコード",
      "related_concepts": ["関連する他の概念名称1", "関連概念2"] 
    }}
  ],
  "questions": [
    {{
      "question_number": "問題番号",
      "question_text": "問題文（LaTeX含む）",
      "answer_text": "[正解] ... \\n[解説] ..."
    }}
  ]
}}
"""
    response = client.models.generate_content(
        model=MODEL_NAME, contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
    )
    step1_json = json.loads(response.text)

    print("   🌐 親フォルダの枝番マスターと照合・採番中...")
    for c in step1_json.get("concepts", []):
        m_code = c.get("mext_code", "")
        c_name = c.get("concept_name", "")
        if m_code and c_name:
            c["branch_code"] = assign_or_get_branch_code(m_code, c_name)
        else:
            c["branch_code"] = "_000"

    return step1_json

# =========================================================
# 🧠 Step 2: カンニング分析 & 精密アライメント生成
# =========================================================
def execute_step2_alignment(step1_data):
    print("\n🧠 [Step 2] 精密アライメントを実行中...")
    prompt = f"""以下の整理済みデータから、確認問題と学習概念のアライメント構造を構築してください。

【整理済みデータ】:
{json.dumps(step1_data, ensure_ascii=False, indent=2)}

【出力JSONフォーマット】:
{{
  "alignments": [
    {{
      "question_number": "問題番号",
      "matched_concept": "対応する概念名",
      "reasoning": "なぜこの概念と合致するかの理由説明",
      "formula_used": "使用する公式や解法の要点（LaTeX）"
    }}
  ]
}}
"""
    response = client.models.generate_content(
        model=MODEL_NAME, contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
    )
    return json.loads(response.text)

# =========================================================
# 🏁 メイン処理
# =========================================================
def main():
    print("=== 🏁 【Ver 10.1 アクション・アンカー対応】Phase 1 起動 ===")
    textbook_content, mext_master_dict, bundle_name = load_and_prepare_inputs()
    step1_output = execute_step1_integrated_analysis(textbook_content, mext_master_dict, bundle_name)
    step2_output = execute_step2_alignment(step1_output)

    final_knowledge_graph = {
        "metadata": {"bundle_name": bundle_name, "engine_version": "10.1_action_anchor", "model_used": MODEL_NAME},
        "extracted_concepts": step1_output.get("concepts", []),
        "questions": step1_output.get("questions", []),
        "alignments": step2_output.get("alignments", []),
    }
    output_filepath = os.path.join(OUTPUT_DIR, "final_knowledge_graph.json")
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(final_knowledge_graph, f, ensure_ascii=False, indent=2)
    print(f"🎉 処理完了！ 💾 保存先: {output_filepath}")

if __name__ == "__main__":
    main()