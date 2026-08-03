import os
import re
import json
import zipfile
import shutil

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_DIR_NAME = "Global_Obsidian_Vault_MEXT"
VAULT_PATH = os.path.join(PARENT_DIR, VAULT_DIR_NAME)
MEXT_DICT_PATH = os.path.join(PARENT_DIR, "mext_master_dict.json")

def clean_filename(name):
    cleaned = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    return cleaned if cleaned else "untitled"

def clean_tag_name(name):
    cleaned = re.sub(r'[\s\\/*?:"<>|()\[\]{}.#,\'`$=+~!@%^&-]', "_", name)
    cleaned = re.sub(r'_+', '_', cleaned).strip('_')
    return cleaned if cleaned else "untitled"

def detect_competency(mext_code):
    if not mext_code or len(mext_code) < 9:
        return None
    competency_digit = mext_code[8]
    if competency_digit == '1': return "知識・技能"
    elif competency_digit == '2': return "思考力・判断力等"
    elif competency_digit == '3': return "主体性等"
    return "大項目・その他"

def main():
    print("🚀 [Ver 12.0 GNN-KT & 階層オントロジー完全対応] Obsidian Vault パッケージ化を開始します...")

    if os.path.exists(VAULT_PATH): 
        shutil.rmtree(VAULT_PATH)
    os.makedirs(VAULT_PATH, exist_ok=True)

    mext_dict = {}
    if os.path.exists(MEXT_DICT_PATH):
        print("   📖 指導要領マスター辞書をロードしています...")
        with open(MEXT_DICT_PATH, "r", encoding="utf-8") as f:
            mext_list = json.load(f).get("mext_dictionary", [])
            mext_dict = {item["mext_code"]: item for item in mext_list}

    sub_dirs = [d for d in os.listdir(PARENT_DIR) if os.path.isdir(os.path.join(PARENT_DIR, d)) and "BL_sugaku" in d]
    sub_dirs.sort()

    global_concepts = {} 
    global_parent_concepts = {} 
    global_videos = {} 
    
    for s_dir in sub_dirs:
        kg_path = os.path.join(PARENT_DIR, s_dir, "output_result", "final_knowledge_graph_complete.json")
        if not os.path.exists(kg_path):
            kg_path = os.path.join(PARENT_DIR, s_dir, "output_result", "final_knowledge_graph.json")
        if not os.path.exists(kg_path): 
            continue
            
        print(f"   📂 解析中: {os.path.basename(s_dir)}")
        with open(kg_path, "r", encoding="utf-8") as f:
            kg_data = json.load(f)

        bundle_name = kg_data.get("metadata", {}).get("bundle_name", os.path.basename(s_dir))
        clean_bundle = clean_filename(bundle_name)
        bundle_tag = clean_tag_name(bundle_name)

        bundle_videos = set()

        for c in kg_data.get("extracted_concepts", []):
            c_name = c["concept_name"]
            parent_name = c.get("parent_concept", "未分類")
            videos = c.get("aligned_videos", [])
            
            if parent_name not in global_parent_concepts:
                global_parent_concepts[parent_name] = {"children": set()}
            global_parent_concepts[parent_name]["children"].add(c_name)

            for v in videos:
                v_file = v.get("video_file")
                if v_file:
                    bundle_videos.add(v_file)
                    if v_file not in global_videos:
                        global_videos[v_file] = {
                            "bundle_tags": set(),
                            "bundle_names": set(),
                            "concepts": set(),
                            "questions_direct": set(),
                            "questions_prereq": set()
                        }
                    global_videos[v_file]["bundle_tags"].add(bundle_tag)
                    global_videos[v_file]["bundle_names"].add(bundle_name)
                    global_videos[v_file]["concepts"].add(f"[[概念_{clean_filename(c_name)}]]")

            if c_name not in global_concepts:
                global_concepts[c_name] = {
                    "summary": c.get("summary", ""),
                    "parent_concept": parent_name,
                    "competency": c.get("competency", ""),
                    "prerequisite_concepts": c.get("prerequisite_concepts", []),
                    "mext_code": c.get("mext_code", ""),
                    "branch_code": c.get("branch_code", ""),
                    "aligned_videos": videos,
                    "linked_questions": set(),
                    "related_concepts": set(c.get("related_concepts", []))
                }
            else:
                global_concepts[c_name]["related_concepts"].update(c.get("related_concepts", []))
                if not global_concepts[c_name]["aligned_videos"] and videos:
                    global_concepts[c_name]["aligned_videos"] = videos

        questions = kg_data.get("questions_with_video_alignment", kg_data.get("questions", []))
        alignments = {str(a["question_number"]): a for a in kg_data.get("alignments", [])}
        raw_aligns = {str(a["question_number"]): a for a in kg_data.get("raw_alignments", [])}

        bundle_q_links = []
        for q in questions:
            q_num = str(q.get("question_number", ""))
            q_text = q.get("question_text", q.get("question_text_snippet", ""))
            q_filename = clean_filename(f"{bundle_name}_Q{q_num}")
            bundle_q_links.append(f"[[{q_filename}]]")

            align_info = raw_aligns.get(q_num, alignments.get(q_num, {}))
            matched_c_name = align_info.get("matched_concept", "")

            if matched_c_name and matched_c_name in global_concepts:
                global_concepts[matched_c_name]["linked_questions"].add(f"[[{q_filename}]]")

            q_content = f"---\ntags:\n  - format/question_item\n  - bundle/{bundle_tag}\n---\n# {bundle_name} Q{q_num}\n\n"
            q_content += f"> **問題概要:** {q_text}\n\n"
            
            if matched_c_name:
                q_content += f"## 🔗 対象の数理概念（Level 4）\n- [[概念_{clean_filename(matched_c_name)}]]\n\n"
            
            q_content += "## 🎬 紐付けられた解説セグメント\n"
            edges = q.get("aligned_videos", [])
            
            direct_edges = []
            prereq_edges = []
            
            if edges:
                for edge in edges:
                    v_file = edge.get('video_file', '')
                    align_type = edge.get("alignment_type", "")
                    
                    if v_file:
                        bundle_videos.add(v_file)
                        if v_file not in global_videos:
                            global_videos[v_file] = {
                                "bundle_tags": set(),
                                "bundle_names": set(),
                                "concepts": set(),
                                "questions_direct": set(),
                                "questions_prereq": set()
                            }
                        global_videos[v_file]["bundle_tags"].add(bundle_tag)
                        global_videos[v_file]["bundle_names"].add(bundle_name)
                        
                        if align_type == "direct_explanation":
                            global_videos[v_file]["questions_direct"].add(f"[[{q_filename}]]")
                            direct_edges.append(edge)
                        else:
                            global_videos[v_file]["questions_prereq"].add(f"[[{q_filename}]]")
                            prereq_edges.append(edge)

                q_content += "### 📘 概念理解（前提となる基礎・解説講義）\n"
                if prereq_edges:
                    for edge in prereq_edges:
                        v_file = edge.get('video_file', '')
                        e_time = edge.get('end_time', '')
                        time_str = f"`{edge.get('start_time', '')}`〜`{e_time}`" if e_time else f"`{edge.get('start_time', '')}`〜"
                        q_content += f"- **🔵 パターンB** [[{clean_filename(v_file)}]] ({time_str})\n"
                        if edge.get("blackboard_ocr"):
                            q_content += f"  - 📝 板書OCR: {edge['blackboard_ocr']}\n"
                        q_content += f"  - 💡 理由: {edge.get('reasoning', '')}\n"
                else:
                    q_content += "- (特記なし)\n"

                q_content += "\n### 📗 例題演習（本問題の解法直接解説）\n"
                if direct_edges:
                    for edge in direct_edges:
                        v_file = edge.get('video_file', '')
                        e_time = edge.get('end_time', '')
                        time_str = f"`{edge.get('start_time', '')}`〜`{e_time}`" if e_time else f"`{edge.get('start_time', '')}`〜"
                        q_content += f"- **🟢 パターンA** [[{clean_filename(v_file)}]] ({time_str})\n"
                        if edge.get("blackboard_ocr"):
                            q_content += f"  - 📝 板書OCR: {edge['blackboard_ocr']}\n"
                        q_content += f"  - 💡 理由: {edge.get('reasoning', '')}\n"
                else:
                    q_content += "- (特記なし)\n"
            else:
                q_content += "- (動画紐付けデータなし)\n"
            
            q_content += f"\n---\n[🔙 {bundle_name} ハブに戻る]: [[{clean_bundle}]]\n"
            with open(os.path.join(VAULT_PATH, f"{q_filename}.md"), "w", encoding="utf-8") as f:
                f.write(q_content)

        b_content = f"---\ntags:\n  - format/hub\n  - bundle/{bundle_tag}\n---\n# {bundle_name}\n\n"
        b_content += "## 📝 収録確認問題\n"
        b_content += "\n".join([f"- {link}" for link in bundle_q_links]) + "\n\n"
        
        b_content += "## 🎬 収録講義動画\n"
        if bundle_videos:
            for v_file in sorted(list(bundle_videos)):
                b_content += f"- [[{clean_filename(v_file)}]]\n"
        else:
            b_content += "- (紐付け動画なし)\n"
            
        with open(os.path.join(VAULT_PATH, f"{clean_bundle}.md"), "w", encoding="utf-8") as f:
            f.write(b_content)

    print("   🧠 Level 3 (親概念ハブ) ノード群を生成中...")
    all_parent_names = set(global_parent_concepts.keys())
    for p_name, p_data in global_parent_concepts.items():
        if p_name == "未分類": continue
        p_filename = clean_filename(f"親概念_{p_name}")
        p_content = f"---\ntags:\n  - format/concept_level3\n  - Role/Stasap_ParentConcept\n---\n# 親概念: {p_name}\n\n## 🔽 含まれる学習アクション（Level 4）\n"
        for child in sorted(list(p_data["children"])):
            p_content += f"- [[概念_{clean_filename(child)}]]\n"
        with open(os.path.join(VAULT_PATH, f"{p_filename}.md"), "w", encoding="utf-8") as f:
            f.write(p_content)

    print("   🧠 Level 4 (学習アクション) ノード群を生成中...")
    all_existing_concept_names = set(global_concepts.keys())

    for c_name, c_data in global_concepts.items():
        c_filename = clean_filename(f"概念_{c_name}")
        
        mext_code = c_data["mext_code"]
        branch_code = c_data["branch_code"]
        m_info = mext_dict.get(mext_code, {})
        
        raw_comp = c_data.get("competency", "")
        if raw_comp == "knowledge_skill": competency_type = "知識・技能"
        elif raw_comp == "thinking_judgment": competency_type = "思考力・判断力等"
        else: competency_type = detect_competency(mext_code)

        c_content = f"---\ntags:\n  - format/concept\n  - format/concept_level4\n  - Role/Stasap_Concept_Action\n"
        if competency_type:
            c_content += f"  - Competency/{clean_tag_name(competency_type)}\n"
        if mext_code:
            c_content += f"  - MEXT/{mext_code}\n"
        c_content += f"---\n# 概念(アクション): {c_name}\n\n"

        parent = c_data.get("parent_concept", "")
        if parent and parent in all_parent_names:
            c_content += f"## 🔼 親概念 (Level 3)\n- [[親概念_{clean_filename(parent)}]]\n\n"

        c_content += "## 🏛️ 指導要領アライメント\n"
        if mext_code and m_info:
            c_content += f"- **観点分類**: `{competency_type if competency_type else '未定義'}`\n"
            c_content += f"- **階層**: {m_info.get('hierarchy', '')}\n"
            c_content += f"- **指導要領コード**: `{mext_code}`\n"
            c_content += f"- **スタサプ枝番**: `{branch_code}`\n"
            c_content += f"\n> **【公式テキスト】**\n> {m_info.get('official_text', '')}\n\n"
            c_content += f"> **【💡 解説要約】**\n> {m_info.get('explanation_summary', '')}\n\n"
        else:
            c_content += "- (指導要領コードの紐付けなし)\n\n"

        c_content += f"## 📌 スタサプ独自概要\n{c_data['summary']}\n\n"
        
        prereqs = c_data.get("prerequisite_concepts", [])
        c_content += "## ➡️ 前提知識 (重み付きネットワーク)\n"
        if prereqs:
            for req in prereqs:
                if isinstance(req, dict):
                    r_name = req.get("concept_name", "")
                    r_type = "🔵 必須" if req.get("dependency_type") == "mandatory" else "🟡 補足"
                    r_reason = req.get("reasoning", "")
                    
                    if r_name in all_parent_names:
                        c_content += f"- **{r_type}**: [[親概念_{clean_filename(r_name)}]]\n"
                    elif r_name in all_existing_concept_names:
                        c_content += f"- **{r_type}**: [[概念_{clean_filename(r_name)}]]\n"
                    else:
                        c_content += f"- **{r_type}**: `{r_name}` (※外部概念)\n"
                        
                    if r_reason:
                        c_content += f"  - 💡 理由: {r_reason}\n"
                else:
                    if req in all_parent_names:
                        c_content += f"- [[親概念_{clean_filename(req)}]]\n"
                    else:
                        c_content += f"- `{req}`\n"
            c_content += "\n"
        else:
            c_content += "- 特記なし\n\n"

        aligned_videos = c_data.get("aligned_videos", [])
        if aligned_videos:
            c_content += "## 🎬 📘 概念理解インプット講義動画\n"
            for v in aligned_videos:
                v_file = v.get("video_file", "")
                s_time = v.get("start_time", "00:00")
                e_time = v.get("end_time", "")
                time_str = f"`{s_time}`〜`{e_time}`" if e_time else f"`{s_time}`〜"
                reason = v.get("reasoning", "")
                c_content += f"- **動画**: [[{clean_filename(v_file)}]] ({time_str})\n"
                if v.get("blackboard_ocr"):
                    c_content += f"  - 📝 板書OCR: {v['blackboard_ocr']}\n"
                if reason:
                    c_content += f"  - 💡 理由: {reason}\n"
            c_content += "\n"

        c_content += "## 🔗 この概念を使用する確認問題\n"
        c_content += "\n".join(sorted(list(c_data["linked_questions"]))) if c_data["linked_questions"] else "- なし"
        
        c_content += "\n\n## 🤝 関連する他の概念（オントロジー・ネットワーク）\n"
        valid_related_links = []
        for rc in c_data.get("related_concepts", set()):
            if rc in all_existing_concept_names and rc != c_name:
                valid_related_links.append(f"- [[概念_{clean_filename(rc)}]]")
            else:
                rc_base = re.sub(r'\(.*?\)', '', rc).strip()
                matched = [name for name in all_existing_concept_names if rc_base in name and name != c_name]
                if matched:
                    valid_related_links.append(f"- [[概念_{clean_filename(matched[0])}]]")

        if valid_related_links:
            c_content += "\n".join(sorted(list(set(valid_related_links)))) + "\n"
        else:
            c_content += "- 特記なし\n"

        with open(os.path.join(VAULT_PATH, f"{c_filename}.md"), "w", encoding="utf-8") as f:
            f.write(c_content)

    print("   🎬 動画ノード群を生成中 (概念理解/例題演習のバックリンク分類)...")
    for v_file, v_data in global_videos.items():
        v_filename = clean_filename(v_file)
        
        tags_str = "  - format/video\n  - Role/Stasap_Video\n"
        for b_tag in sorted(list(v_data["bundle_tags"])):
            tags_str += f"  - bundle/{b_tag}\n"
            
        v_content = f"---\ntags:\n{tags_str}---\n# 🎬 動画: {v_file}\n\n"
        
        if v_data["bundle_names"]:
            v_content += "## 🏛️ 所属単元\n"
            v_content += "\n".join([f"- [[{clean_filename(b_name)}]]" for b_name in sorted(list(v_data["bundle_names"]))]) + "\n\n"
            
        if v_data["concepts"]:
            v_content += "## 🧠 📘 関連する概念理解（インプット講義）\n"
            v_content += "\n".join(sorted(list(v_data["concepts"]))) + "\n\n"
            
        if v_data["questions_direct"] or v_data["questions_prereq"]:
            v_content += "## 📝 紐付けられた確認問題\n"
            if v_data["questions_direct"]:
                v_content += "### 📗 【例題演習】（直接解説している問題）\n"
                v_content += "\n".join(sorted(list(v_data["questions_direct"]))) + "\n\n"
            if v_data["questions_prereq"]:
                v_content += "### 📘 【概念理解】（前提概念として紐づく問題）\n"
                v_content += "\n".join(sorted(list(v_data["questions_prereq"]))) + "\n\n"

        with open(os.path.join(VAULT_PATH, f"{v_filename}.md"), "w", encoding="utf-8") as f:
            f.write(v_content)

    zip_path = os.path.join(PARENT_DIR, f"{VAULT_DIR_NAME}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(VAULT_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, PARENT_DIR)
                zipf.write(file_path, arcname)

    print(f"🎉 🎉 【成功】Obsidian Vault（Ver 12.0 GNN-KT & 階層オントロジー完全対応）の生成完了！\n💾 保存先: {zip_path}")

if __name__ == "__main__":
    main()