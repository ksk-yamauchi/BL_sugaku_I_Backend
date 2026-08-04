import os
import re
import json
import sys
import time
from glob import glob
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

# =========================================================
# ⚙️ 設定・初期化 (.env 複数APIキー対応 ＆ 強制上書き)
# =========================================================
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

load_dotenv(dotenv_path=ENV_PATH, override=True)

def clean_key(k_str):
    if not k_str:
        return ""
    return k_str.strip().strip("'\"").replace('\ufeff', '')

raw_keys = os.environ.get("GEMINI_API_KEYS", "") or os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [clean_key(k) for k in raw_keys.split(",") if clean_key(k)]

if not API_KEYS:
    raise ValueError("❌ .env ファイルに GEMINI_API_KEYS または GEMINI_API_KEY が設定されていません。")

current_key_index = 0
MODEL_NAME = "gemini-3.6-flash"

def get_client():
    global current_key_index
    key = API_KEYS[current_key_index]
    return genai.Client(api_key=key)

def rotate_key():
    global current_key_index
    if len(API_KEYS) <= 1:
        print("   ⚠️ 登録されているAPIキーが1つのため、キー切り替えができません。")
        return False
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    masked_key = f"{API_KEYS[current_key_index][:6]}...{API_KEYS[current_key_index][-4:]}" if len(API_KEYS[current_key_index]) > 10 else "INVALID"
    print(f"   🔄 APIキーを切り替えました (Key {current_key_index + 1}/{len(API_KEYS)}: {masked_key})")
    return True

# 🌟 通信エラーだけでなく、JSONパースエラー(LaTeXエスケープ等)も検知・修復してリトライする最強関数
def generate_content_and_parse_json(prompt, max_retries=None):
    if max_retries is None:
        # 登録されているAPIキーの2倍の回数までリトライを許可する
        max_retries = max(5, len(API_KEYS) * 2)
        
    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
    
    for attempt in range(1, max_retries + 1):
        try:
            client = get_client()
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config
            )
            
            # Markdownブロックの除去
            text = response.text
            text = re.sub(r'^```json\s*', '', text.strip(), flags=re.IGNORECASE)
            text = re.sub(r'\s*```$', '', text)
            
            # JSONのパースと自動修復
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # ありがちな「LaTeXの \ をエスケープし忘れた」エラーに対する自動修復
                fixed_text = text.replace('\\', '\\\\').replace('\\\\"', '\\"').replace('\\\\n', '\\n')
                try:
                    return json.loads(fixed_text)
                except json.JSONDecodeError as je:
                    print(f"   ⚠️ AI出力のJSON形式エラー(LaTeXエスケープ起因等)。安全に再生成します... (試行 {attempt}/{max_retries})")
                    if attempt == max_retries:
                        raise RuntimeError(f"❌ JSONパースが{max_retries}回失敗しました: {je}")
                    time.sleep(3)
                    continue

        except errors.APIError as e:
            err_str = str(e).lower()
            if any(k in err_str for k in ["429", "quota", "resource_exhausted", "api_key_invalid", "invalid_argument"]):
                curr_k = API_KEYS[current_key_index]
                masked_k = f"{curr_k[:6]}...{curr_k[-4:]}" if len(curr_k) > 10 else "INVALID"
                print(f"   ⚠️ API制限/無効キーを検知しました (Key: {masked_k}, 試行 {attempt}/{max_retries})")
                if rotate_key():
                    print("   ⏩ 次のAPIキーへ切り替えて即座にリトライします...")
                    continue
                else:
                    print("   ⏳ 40秒待機後に再トライします...")
                    time.sleep(40)
            elif "503" in err_str or "unavailable" in err_str:
                print(f"   ⚠️ 503サーバーエラー (試行 {attempt}/{max_retries}): 30秒待機後に再トライ...")
                time.sleep(30)
            else:
                if attempt == max_retries: raise e
                print(f"   ⚠️ APIエラー ({e}) (試行 {attempt}/{max_retries}): 15秒待機後に再トライ...")
                time.sleep(15)
        except Exception as e:
            if attempt == max_retries: raise e
            print(f"   ⚠️ 通信エラー ({e}) (試行 {attempt}/{max_retries}): 15秒待機後に再トライ...")
            time.sleep(15)
            
    raise RuntimeError("❌ リトライ上限超過")


md_files = glob("*_clean.md")
if not md_files:
    raise FileNotFoundError("❌ 教材Markdown(*_clean.md)が見つかりません。")
TEXTBOOK_MD_PATH = md_files[0]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

MEXT_DICT_PATH = os.path.join(PARENT_DIR, "mext_master_dict.json")
BRANCH_MASTER_PATH = os.path.join(PARENT_DIR, "concept_branch_master.json")
INDEX_MASTER_PATH = os.path.join(PARENT_DIR, "lecture_index_master.json")

OUTPUT_DIR = os.path.join(CURRENT_DIR, "output_result")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_bundle_name_from_master(folder_name):
    if not os.path.exists(INDEX_MASTER_PATH):
        print("\n❌ 【エラー】 目次マスターが見つかりません。")
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


def load_branch_master_examples():
    if not os.path.exists(BRANCH_MASTER_PATH):
        return "（既存マスターデータなし）"
    try:
        with open(BRANCH_MASTER_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        examples = []
        count = 0
        for mext_code, items in data.items():
            for item in items:
                c_name = item.get("concept_name", "")
                snippet = item.get("summary_snippet", "")
                if c_name:
                    examples.append(f"- {c_name} (要約: {snippet})")
                    count += 1
                if count >= 15:
                    break
            if count >= 15:
                break
        return "\n".join(examples) if examples else "（既存マスターデータなし）"
    except Exception:
        return "（既存マスターデータなし）"


def assign_or_get_branch_code(mext_code, concept_name, summary="", bundle_name=""):
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
        "concept_name": concept_name,
        "summary_snippet": summary[:100] if summary else "",
        "first_appeared_in": bundle_name
    })

    with open(BRANCH_MASTER_PATH, "w", encoding="utf-8") as f:
        json.dump(branch_master, f, ensure_ascii=False, indent=2)

    return new_branch_code


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


def execute_step1_integrated_analysis(textbook_content, mext_master_dict, bundle_name):
    print(f"\n🚀 [Step 1] 統合分析プロンプトを実行中（GNN-KT対応版: {bundle_name}）...")

    master_examples_str = load_branch_master_examples()

    prompt = f"""あなたは高等学校数学科の教材分析・学習オントロジー構築のエキスパートです。
以下の「教材データ」と「指導要領マスター辞書」を解析し、GNN-KT（学習状態推論）およびGraph RAGに最適化されたナレッジグラフを構築してください。

【対象単元】: {bundle_name}

【★概念（concepts）抽出ルール★】
1. `concept_name` (Level 4: 極小項目・学習アクション):
   - 教材テキストで解説・演習されている「生徒の具体的な計算手順や操作アクション」を抽出してください。
   - 【命名フォーマット】: [対象となる数式・用語] + [行う具体的処理] (例: 「単項式の係数と次数を特定する」)
2. 【既存の登録マスター例】: {master_examples_str}
3. `parent_concept` (Level 3: 親項目ハブ):
   - 属する一般的な高校数学の標準用語を1つ指定。
4. `prerequisite_concepts` (前提知識・エッジ):
   - 必要な前提知識を親概念レベル(Level 3)でリストアップ。
   - `dependency_type` (`mandatory` | `supplementary`) を指定。
5. `competency` (学習観点タグ):
   - `"knowledge_skill"` | `"thinking_judgment"`
6. `mext_code` (Level 1,2: 大・中項目):
   - 辞書から最適な16桁コードを割り当て。

【★最重要: LaTeXとJSONエスケープの絶対ルール★】
`summary`や`reasoning`、`question_text`等のテキスト内にLaTeX数式（$...$）を含める場合、**必ずバックスラッシュを二重にエスケープ（例: \\\\frac, \\\\subset）** してください。JSONフォーマットとしてInvalidにならないよう細心の注意を払ってください。

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
      "concept_name": "具体的計算アクション",
      "summary": "要点・公式の説明",
      "parent_concept": "親概念",
      "competency": "knowledge_skill | thinking_judgment",
      "prerequisite_concepts": [
        {{
          "concept_name": "前提となる一般数学用語",
          "dependency_type": "mandatory | supplementary",
          "reasoning": "理由"
        }}
      ],
      "mext_code": "16桁のコード"
    }}
  ],
  "questions": [
    {{
      "question_number": "問題番号",
      "question_text": "問題文（LaTeXエスケープ厳守）",
      "answer_text": "[正解] ... \\n[解説] ..."
    }}
  ]
}}
"""
    # ★ APIを叩いてパースまで完結する関数を使用
    step1_json = generate_content_and_parse_json(prompt)

    print("   🌐 親フォルダの枝番マスターと照合・採番（メタデータ連携）中...")
    for c in step1_json.get("concepts", []):
        m_code = c.get("mext_code", "")
        c_name = c.get("concept_name", "")
        summary = c.get("summary", "")
        if m_code and c_name:
            c["branch_code"] = assign_or_get_branch_code(m_code, c_name, summary, bundle_name)
        else:
            c["branch_code"] = "_000"

    return step1_json


def execute_step2_alignment(step1_data):
    print("\n🧠 [Step 2] 精密アライメントを実行中...")
    prompt = f"""以下の整理済みデータから、確認問題と学習概念のアライメント構造を構築してください。

【★最重要: LaTeXとJSONエスケープの絶対ルール★】
出力するJSON内のテキストにLaTeXを含める場合、**必ずバックスラッシュを二重にエスケープ（例: \\\\frac, \\\\subset）** してください。

【整理済みデータ】:
{json.dumps(step1_data, ensure_ascii=False, indent=2)}

【出力JSONフォーマット】:
{{
  "alignments": [
    {{
      "question_number": "問題番号",
      "matched_concept": "対応する細かい概念名(concept_name)",
      "reasoning": "なぜこの概念と合致するかの理由説明",
      "formula_used": "使用する公式や解法の要点（LaTeXエスケープ厳守）"
    }}
  ]
}}
"""
    # ★ こちらも自動パース関数を使用
    return generate_content_and_parse_json(prompt)


def main():
    print("=== 🏁 【Ver 12.1 GNN-KT & メタデータ拡張オントロジー対応】Phase 1 起動 ===")
    print(f"   🔑 読み込み済み有効APIキー数: {len(API_KEYS)} 個")
    first_key_masked = f"{API_KEYS[0][:6]}...{API_KEYS[0][-4:]}" if len(API_KEYS[0]) > 10 else "INVALID"
    print(f"   👉 現在使用中のキー: {first_key_masked}")

    textbook_content, mext_master_dict, bundle_name = load_and_prepare_inputs()
    
    step1_output = execute_step1_integrated_analysis(textbook_content, mext_master_dict, bundle_name)
    step2_output = execute_step2_alignment(step1_output)

    final_knowledge_graph = {
        "metadata": {"bundle_name": bundle_name, "engine_version": "12.0_gnn_kt_ontology", "model_used": MODEL_NAME},
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