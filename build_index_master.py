import os
import re
import json
import glob

# =========================================================
# ⚙️ 設定
# =========================================================
# このスクリプトは親フォルダ（BL_sugaku_Ⅰ や BL_sugaku_A など）に配置して実行します
PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON_PATH = os.path.join(PARENT_DIR, "lecture_index_master.json")

def main():
    print("=== 📚 目次マスターJSON生成スクリプト ===")
    
    # 🌟 動的にインデックスMDファイルを検索（ファイル名やフォルダ名が変わってもOK！）
    search_pattern = os.path.join(PARENT_DIR, "*index*_clean.md")
    index_files = glob.glob(search_pattern)
    
    # もし _clean が付いていない場合のためのフォールバック（予備）
    if not index_files:
        search_pattern_fallback = os.path.join(PARENT_DIR, "*index*.md")
        index_files = glob.glob(search_pattern_fallback)
        
        if not index_files:
            print(f"❌ エラー: 親フォルダ内に目次ファイル（名前に 'index' を含む .md）が見つかりません。")
            return

    # 最初に見つかったインデックスファイルを処理対象とする
    index_md_path = index_files[0]
    print(f"📄 読み込み対象: {os.path.basename(index_md_path)}")

    with open(index_md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    index_data = {}
    current_lecture_num = ""
    current_lecture_title = ""

    print("🔍 目次(Markdown)を解析中...")
    
    for line in lines:
        line = line.strip()
        
        # 第X講 の抽出 (例: ### 第1講 式の計算と展開)
        lec_match = re.search(r"第\s*(\d+)\s*講\s+(.+)", line)
        if lec_match:
            current_lecture_num = lec_match.group(1).strip()
            current_lecture_title = re.sub(r'^[#*\s-]+', '', lec_match.group(2)).strip()
            continue

        # PART Y の抽出 (例: - **PART1** 単項式と多項式)
        part_match = re.search(r"PART\s*(\d+)\*?\*?\s+(.+)", line)
        if part_match and current_lecture_num:
            part_num = part_match.group(1).strip()
            part_title = re.sub(r'^[#*\s-]+', '', part_match.group(2)).strip()

            # キーの生成 (例: "01-1", "03-2", "15-4")
            key = f"{int(current_lecture_num):02d}-{part_num}"
            
            # 正確な単元名（Bundle Name）を組み上げ
            bundle_name = f"第{current_lecture_num}講 {current_lecture_title} PART{part_num} {part_title}"
            
            index_data[key] = {
                "lecture_num": current_lecture_num,
                "lecture_title": current_lecture_title,
                "part_num": part_num,
                "part_title": part_title,
                "bundle_name": bundle_name
            }

    # JSONファイルとして保存
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"🎉 生成完了！")
    print(f"💾 保存先: {OUTPUT_JSON_PATH}")
    print(f"📊 登録されたPART数: {len(index_data)}件")

if __name__ == "__main__":
    main()