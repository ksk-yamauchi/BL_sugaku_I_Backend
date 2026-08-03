import json
import os
import re
import time
from glob import glob
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

# =========================================================
# ⚙️ 設定・初期化 (.env 対応)
# =========================================================
# 親フォルダの .env を確実に読み込む
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ .env ファイルに GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-3.6-flash"

# フォルダ内の _clean.md を自動検知（教材テキスト連動）
md_files = glob("*_clean.md")
if not md_files:
    raise FileNotFoundError("❌ 教材Markdown(*_clean.md)が見つかりません。フォルダ内を確認してください。")
TEXTBOOK_MD_PATH = md_files[0]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(CURRENT_DIR, "output_result")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "lecture_map.json")

# =========================================================
# 🔄 汎用・自動リトライ付き API 呼び出し (429 / 503 自動復旧)
# =========================================================
def generate_content_with_retry(contents, response_schema=None, max_retries=5):
    config_kwargs = {
        "temperature": 0.1,
        "response_mime_type": "application/json"
    }
    if response_schema:
        config_kwargs["response_schema"] = response_schema
        
    config = types.GenerateContentConfig(**config_kwargs)

    for attempt in range(1, max_retries + 1):
        try:
            print(f"      [通信開始: 試行 {attempt}/{max_retries}]")
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config
            )
            print("      [通信完了]")
            return response
        except errors.APIError as e:
            err_str = str(e).lower()
            if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                print(f"      ⚠️ 429レート制限エラー (試行 {attempt}/{max_retries}): 40秒待機後リトライ...")
                time.sleep(40)
            elif "503" in err_str or "unavailable" in err_str:
                print(f"      ⚠️ 503サーバーエラー (試行 {attempt}/{max_retries}): 30秒待機後リトライ...")
                time.sleep(30)
            else:
                if attempt == max_retries: raise e
                print(f"      ⚠️ API通信エラー ({e}) (試行 {attempt}/{max_retries}): 20秒待機後リトライ...")
                time.sleep(20)
        except Exception as e:
            if attempt == max_retries: raise e
            print(f"      ⚠️ 予期せぬ通信エラー ({e}) (試行 {attempt}/{max_retries}): 20秒待機後リトライ...")
            time.sleep(20)
    raise RuntimeError("❌ リトライ上限超過")

# =========================================================
# 📂 ファイル取得 ＆ 大問番号抽出
# =========================================================
def get_auto_paired_files():
    mp4_files = sorted(glob("*.mp4"))
    vtt_files = sorted(glob("*.vtt"))
    if not mp4_files:
        return []
    pairs = []
    for i, mp4 in enumerate(mp4_files):
        vtt = vtt_files[i] if i < len(vtt_files) else None
        pairs.append((mp4, vtt))
    return pairs

def extract_question_number(textbook_content):
    match = re.search(r"PART\s*(\d+)", textbook_content, re.IGNORECASE)
    return match.group(1) if match else ""

# =========================================================
# 🤖 動的役割推論 (🌟 教材MD照合 ＆ 大問検知強化)
# =========================================================
def detect_video_role(vtt_content, video_name, textbook_content=""):
    if not vtt_content:
        return "exercise_walkthrough"

    schema = {
        "type": "OBJECT",
        "properties": {
            "role": {
                "type": "STRING", 
                "enum": ["concept_lecture", "exercise_walkthrough", "concept_application"]
            },
            "reason": {"type": "STRING"}
        },
        "required": ["role", "reason"]
    }
    
    prompt = f"""以下の「字幕データ」および「教材テキスト」を分析し、この講義動画の役割を以下の3つのいずれかに分類してください。

【分類の選択肢と基準】

1. `concept_lecture` (概念講義)
   - 新しい公式、定理、用語の導入や証明、基礎的な意味の解説が「動画全体のメインテーマ」である場合。
   - 🌟【重要ルール】タイトルや単元名に「〜の利用」「〜の応用」と含まれていても、「概念・条件・公式の理論的な説明（例：共有点をもつ条件はD≧0である理由など）」に終始している場合は、必ず `concept_lecture` に分類してください。

2. `exercise_walkthrough` (例題演習)
   - 教材内の具体的な「大問」「確認問題」「問題」（例: 大問1、次の二次不等式を解け 等）の計算手順・解法解説を行っている場合。「例」の解答解説は含みません。
　 - 🌟【判定の最優先ルール】字幕の冒頭や途中で「大問○番目を見ていきましょう」「問題○」といった発言があり、教材テキストに掲載されている具体問題の解法を解説している場合は、冒頭で「Point Pickup」などの公式おさらいをしていても、必ず `exercise_walkthrough` に分類してください。

3. `concept_application` (概念の応用・利用)
   - すでに学習した概念や公式を利用して、「例」において、文章題や図形問題などの「応用問題」（例: ○○の利用など）を解き、知識の活用方法を解説している場合。
   - 🌟【判定の最優先ルール】「問題の解法や解決プロセス」を見せることがメインである場合にのみ選択します。

【動画名】: {video_name}

【教材テキスト (一部)】:
{textbook_content[:1500]}

【字幕データ (冒頭2000文字)】:
{vtt_content[:2000]}
"""
    print(f"  ├─ 🔍 [事前推論] 動画 '{video_name}' の役割を教材MDと照合して自動判定中...")
    
    try:
        response = generate_content_with_retry([prompt], schema, max_retries=3)
        result = json.loads(response.text)
        role = result.get("role", "exercise_walkthrough")
        reason = result.get("reason", "判定成功")
        
        # 表示を分かりやすく翻訳
        role_label = ""
        if role == "concept_lecture": role_label = "概念講義"
        elif role == "exercise_walkthrough": role_label = "例題演習"
        elif role == "concept_application": role_label = "概念の応用・利用"
        
        print(f"  ├─ 🎯 判定結果: {role_label} [{role}] (理由: {reason})")
        return role
    except Exception as e:
        print(f"  ├─ ⚠️ 事前推論に失敗しました({e})。安全のため「例題演習(exercise_walkthrough)」として処理を続行します。")
        return "exercise_walkthrough"

# =========================================================
# 🏁 メイン実行パイプライン
# =========================================================
def main():
    print(f"=== 🎬 [Phase 2 Ver 2.5] 教材MD連動・大問検知強化版 起動 ===")

    with open(TEXTBOOK_MD_PATH, "r", encoding="utf-8") as f:
        textbook_content = f.read()

    question_number = extract_question_number(textbook_content)
    pairs = get_auto_paired_files()
    if not pairs:
        print("⚠️ フォルダ内に .mp4 ファイルが見つかりません。Phase 2 をスキップします。")
        return

    all_video_maps = []

    for idx, (mp4_path, vtt_path) in enumerate(pairs, 1):
        print(f"\n--------------------------------------------------")
        print(f"📹 [{idx}/{len(pairs)}] 動画処理プロセス開始: {mp4_path}")

        vtt_content = ""
        if vtt_path and os.path.exists(vtt_path):
            with open(vtt_path, "r", encoding="utf-8", errors="ignore") as f:
                vtt_content = f.read()

        # 1. ロールの自動判定 (教材MDを入力に追加)
        role = detect_video_role(vtt_content, mp4_path, textbook_content)

        # 2. 動画ファイルのGeminiへのアップロード
        print("  ├─ ⏳ 動画をGemini APIへアップロード中...")
        try:
            uploaded_video = client.files.upload(file=mp4_path)
        except Exception as e:
            print(f"❌ {mp4_path} のアップロードに失敗しました: {e}")
            continue

        print("  ├─ ⏳ Google側の動画処理完了を待機しています...")
        while uploaded_video.state.name == "PROCESSING":
            time.sleep(5)
            uploaded_video = client.files.get(name=uploaded_video.name)

        if uploaded_video.state.name == "FAILED":
            print(f"❌ 動画処理に失敗しました: {mp4_path}")
            continue

        print("  ├─ 🟢 動画の準備完了 (ACTIVE)")

        # 3. 解析プロンプトの出し分け
        if role == "concept_lecture":
            granularity_instruction = "【概念理解特化・極細分割】: 1〜3分単位のミクロな解説ステップ（公式の導入、意味、証明、注意点など）を細かく分割してください。"
        else:
            # exercise_walkthrough と concept_application はこちら
            granularity_instruction = "【問題解説特化・超極細ステップ分割】: 各小問の計算の途中経過、数十秒〜1、2分単位の微細な計算ステップ（立式、変形、答えの確認など）ごとに徹底的に細かくセグメントを細分化してください。"

        prompt = f"""動画のタイムラインを解析し、詳細なチャプター（セグメント）を作成してください。

【最優先：粒度の超極細化ルール】
- 指示された通りの極細粒度（{granularity_instruction}）で網羅して作成してください。
- 各セグメントの開始時間（`start_time`）と終了時間（`end_time`）を MM:SS 形式で正確に記録してください。

【★最重要：黒板・スライドのLaTeX書き起こし (blackboard_ocr)★】
- 動画内の黒板、ホワイトボード、スライドに書かれている数式・文字・図の情報を読み取り、`blackboard_ocr` 項目へLaTeX形式（$ ... $ または $$ ... $$）で正確に書き起こしてください。

【出力ルール】
1. 日本語出力
2. 教材テキストとの超シンクロ（何ページ、どの問の解説か意識すること）

【教材テキスト】
{textbook_content}

【字幕データ】
{vtt_content if vtt_content else "字幕データなし。動画の音声と映像から解析してください。"}
"""
        schema = {
            "type": "OBJECT",
            "properties": {
                "segments": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "topic": {"type": "STRING"},
                            "start_time": {"type": "STRING"},
                            "end_time": {"type": "STRING"},
                            "blackboard_ocr": {"type": "STRING"},
                            "explanation_summary": {"type": "STRING"},
                        },
                        "required": ["topic", "start_time", "end_time", "blackboard_ocr", "explanation_summary"],
                    },
                }
            },
            "required": ["segments"],
        }

        print("  ├─ 🧠 マルチモーダル超極細解析＆板書OCRを実行中...")
        response = generate_content_with_retry([uploaded_video, prompt], schema)
        result_data = json.loads(response.text)
        segments = result_data.get("segments", [])

        # 4. ノイズカット処理
        if segments:
            first_seg = segments[0]
            first_topic = first_seg.get("topic", "").lower()
            if any(w in first_topic for w in ["intro", "イントロ", "opening", "オープニング", "タイトル", "チャプター"]) or first_seg.get("end_time", "") <= "00:05":
                print(f"  ├─ ✂️ 冒頭のノイズセグメントを自動カット: '{first_seg.get('topic')}'")
                segments.pop(0)
                if segments: segments[0]["start_time"] = "00:05"

            if segments:
                last_seg = segments[-1]
                last_topic = last_seg.get("topic", "").lower()
                if any(w in last_topic for w in ["ending", "エンディング", "outro", "アウトロ", "挨拶", "締め", "お疲れ様"]):
                    print(f"  ├─ ✂️ 末尾のノイズセグメントを自動カット: '{last_seg.get('topic')}'")
                    segments.pop(-1)

        # 5. トピック名の正規化処理 (🌟 応用問題も例題フォーマットを適用)
        if role in ["exercise_walkthrough", "concept_application"]:
            current_shomon = ""
            current_edamon = ""
            for seg in segments:
                original_topic = seg.get("topic", "")
                if "schema says" in original_topic.lower():
                    match = re.search(r"schema says\s*(.*)$", original_topic, re.IGNORECASE)
                    if match: original_topic = match.group(1).strip()

                raw_text = re.sub(r"^\[?例題\]?\s*", "", original_topic)
                raw_text = re.sub(r"^大問\s*\d+\s*", "", raw_text)

                shomon_match = re.search(r"\(([1-9]\d*)\)", raw_text)
                edamon_match = re.search(r"\(([ivx]+)\)|小問\(([ivx]+)\)", raw_text, re.IGNORECASE)

                if shomon_match:
                    new_shomon = f"({shomon_match.group(1)})"
                    if new_shomon != current_shomon:
                        current_shomon = new_shomon
                        current_edamon = ""
                if edamon_match:
                    val = edamon_match.group(1) or edamon_match.group(2)
                    current_edamon = f"({val.lower()})"

                cleaned_topic = raw_text
                cleaned_topic = re.sub(r"\[\d+\]", "", cleaned_topic)
                cleaned_topic = re.sub(r"\([1-9]\d*\)", "", cleaned_topic)
                cleaned_topic = re.sub(r"小問\([ivx]+\)", "", cleaned_topic, flags=re.IGNORECASE)
                cleaned_topic = re.sub(r"\([ivx]+\)", "", cleaned_topic, flags=re.IGNORECASE)
                cleaned_topic = re.sub(r"^[\]\}><\-\s:\x2d\u2010-\u2015\u2212]+", "", cleaned_topic)
                cleaned_topic = re.sub(r"\s+", " ", cleaned_topic).strip()

                parts = ["[例題]"]
                if question_number: parts.append(f"大問{question_number}")
                if current_shomon: parts.append(current_shomon)
                if current_edamon: parts.append(current_edamon)
                parts.append(cleaned_topic)

                seg["topic"] = " ".join(parts)
        else:
            print("  ├─ 💡 概念講義と判定されたため、トピック名の強制上書きはスキップします。")

        all_video_maps.append({
            "video_file": os.path.basename(mp4_path),
            "vtt_file": os.path.basename(vtt_path) if vtt_path else None,
            "role": role,
            "segments": segments
        })

        try:
            client.files.delete(name=uploaded_video.name)
            print("  └─ 🧹 クラウド上の動画一時ファイルを削除しました。")
        except Exception:
            pass

        time.sleep(3)

    output_data = {
        "engine_version": "2.5_role_detection_textbook_sync",
        "videos": all_video_maps
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("\n=========================================================")
    print(f"🎉 講義マップ (lecture_map.json) の完全解析生成が完了しました！")
    print(f"💾 保存先: {OUTPUT_FILE}")
    print("=========================================================")

if __name__ == "__main__":
    main()