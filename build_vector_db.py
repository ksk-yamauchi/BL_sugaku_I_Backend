import os
import json
import requests
from dotenv import load_dotenv

# =========================================================
# ⚙️ 設定・初期化
# =========================================================
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ .env ファイルに GEMINI_API_KEY が設定されていません。")

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
GLOBAL_DB_PATH = os.path.join(PARENT_DIR, "global_vector_db_cache.json")
MEXT_DICT_PATH = os.path.join(PARENT_DIR, "mext_master_dict.json")

# =========================================================
# 🧠 ベクトル化 (API通信)
# =========================================================
def discover_embed_model(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    res = requests.get(url, proxies={"http": None, "https": None}, timeout=10)
    embed_models = [m["name"] for m in res.json().get("models", []) if "embedContent" in m.get("supportedGenerationMethods", [])]
    if not embed_models: 
        raise RuntimeError("❌ 利用可能な埋め込みモデルが見つかりません。")
    target_model = embed_models[-1]
    for m in embed_models:
        if "text-embedding" in m: 
            target_model = m
            break
    return target_model

def get_embedding(text, model_name, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:embedContent?key={api_key}"
    payload = {"model": model_name, "content": {"parts": [{"text": text}]}}
    try:
        res = requests.post(url, json=payload, proxies={"http": None, "https": None}, timeout=15)
        res.raise_for_status()
        return res.json()["embedding"]["values"]
    except Exception as e:
        print(f"❌ ベクトル化通信エラー: {e}")
        return None

# =========================================================
# 🏗️ グローバルDBの構築
# =========================================================
def build_global_vector_db():
    print("\n📦 【グローバルDB構築】デュアル・ベクトル空間（概念 ＆ 問題）を構築中...")
    
    selected_model = discover_embed_model(API_KEY)
    print(f"   ✅ 使用ベクトルモデル: {selected_model}")
    
    if not os.path.exists(MEXT_DICT_PATH):
        raise FileNotFoundError("❌ mext_master_dict.json が見つかりません。先に生成してください。")
    with open(MEXT_DICT_PATH, "r", encoding="utf-8") as f:
        mext_dict_list = json.load(f).get("mext_dictionary", [])
        mext_dict = {item["mext_code"]: item for item in mext_dict_list}

    sub_dirs = [os.path.join(PARENT_DIR, d) for d in os.listdir(PARENT_DIR) if os.path.isdir(os.path.join(PARENT_DIR, d)) and "BL_sugaku" in d]
    sub_dirs.sort()

    global_concept_nodes = {}
    global_question_nodes = {}
    global_mext_index = {}
    global_timeline_counter = 0

    for s_dir in sub_dirs:
        kg_path = os.path.join(s_dir, "output_result", "final_knowledge_graph_complete.json")
        if not os.path.exists(kg_path):
            kg_path = os.path.join(s_dir, "output_result", "final_knowledge_graph.json")
            if not os.path.exists(kg_path): 
                continue
            
        print(f"   📂 読み込み中: {os.path.basename(s_dir)}")
        with open(kg_path, "r", encoding="utf-8") as f: 
            kg_data = json.load(f)

        bundle_name = kg_data.get("metadata", {}).get("bundle_name", os.path.basename(s_dir))
        concepts_map = {c["concept_name"]: c for c in kg_data.get("extracted_concepts", [])}
        
        for c in kg_data.get("extracted_concepts", []):
            c_name = c["concept_name"]
            global_c_id = f"{bundle_name}_Concept_{c_name}"
            mext_code = c.get("mext_code", "")
            branch_code = c.get("branch_code", "")
            mext_info = mext_dict.get(mext_code, {})

            c_composite = f"【単元】{bundle_name}\n【数理概念】{c_name}\n【要約・公式】{c.get('summary', '')}\n"
            if mext_info:
                c_composite += f"【指導要領階層】{mext_info.get('hierarchy', '')}\n"
                c_composite += f"【指導要領テキスト】{mext_info.get('official_text', '')}\n"
                c_composite += f"【解説要約】{mext_info.get('explanation_summary', '')}\n"

            if global_c_id not in global_concept_nodes:
                print(f"      🧠 [概念ベクトル化] {c_name}")
                c_vector = get_embedding(c_composite, selected_model, API_KEY)
                if c_vector:
                    if mext_code:
                        global_mext_index.setdefault(mext_code, []).append(global_c_id)

                    global_concept_nodes[global_c_id] = {
                        "global_c_id": global_c_id,
                        "bundle_name": bundle_name,
                        "concept_name": c_name,
                        "summary": c.get("summary", ""),
                        "concept_vector": c_vector,
                        "mext_code": mext_code,
                        "branch_code": branch_code,
                        "mext_hierarchy": mext_info.get("hierarchy", "不明な階層"),
                        "mext_official_text": mext_info.get("official_text", ""),
                        "mext_explanation": mext_info.get("explanation_summary", "解説なし"),
                        "aligned_videos": c.get("aligned_videos", []),
                        "global_timeline_index": global_timeline_counter
                    }
                    global_timeline_counter += 1  

        alignments = {str(a["question_number"]): a for a in kg_data.get("alignments", [])}
        questions = kg_data.get("questions_with_video_alignment", kg_data.get("questions", []))

        for q in questions:
            q_num = str(q.get("question_number", ""))
            global_q_id = f"{bundle_name}_Q{q_num}"
            q_text = q.get("question_text", q.get("question_text_snippet", ""))
            
            align_info = alignments.get(q_num, {})
            matched_c_name = align_info.get("matched_concept", "")
            
            concept_info = concepts_map.get(matched_c_name, {})
            mext_code = concept_info.get("mext_code", "")
            branch_code = concept_info.get("branch_code", "")
            mext_info = mext_dict.get(mext_code, {})

            q_composite = f"【単元】{bundle_name}\n【問題文】{q_text}\n【対象概念】{matched_c_name}\n"
            
            print(f"      📝 [問題ベクトル化] {global_q_id}")
            q_vector = get_embedding(q_composite, selected_model, API_KEY)
            if q_vector:
                global_question_nodes[global_q_id] = {
                    "global_q_id": global_q_id,
                    "bundle_name": bundle_name,
                    "local_q_num": q_num,
                    "question_text": q_text,
                    "question_vector": q_vector,
                    "matched_concept": matched_c_name,
                    "mext_code": mext_code,
                    "branch_code": branch_code,
                    "mext_hierarchy": mext_info.get("hierarchy", "不明な階層"),
                    "mext_official_text": mext_info.get("official_text", ""),
                    "mext_explanation": mext_info.get("explanation_summary", "解説なし"),
                    "aligned_videos": q.get("aligned_videos", []),
                    "global_timeline_index": global_timeline_counter
                }
                global_timeline_counter += 1  

    db_payload = {
        "embed_model": selected_model,
        "global_concept_nodes": global_concept_nodes,
        "global_question_nodes": global_question_nodes,
        "global_mext_index": global_mext_index
    }
    with open(GLOBAL_DB_PATH, "w", encoding="utf-8") as f: 
        json.dump(db_payload, f, ensure_ascii=False, indent=2)
    print(f"\n✅ デュアル・ベクトル空間DBの構築完了！ 💾 {GLOBAL_DB_PATH}")

# =========================================================
# 🏃‍♂️ メイン実行
# =========================================================
def main():
    print("🚀 [スタサプRAG] バックエンドDB構築ツール起動...")
    build_global_vector_db()
    print("🎉 すべての処理が完了しました。フロントエンド (app.py) を起動して検索をお試しください。")

if __name__ == "__main__":
    main()