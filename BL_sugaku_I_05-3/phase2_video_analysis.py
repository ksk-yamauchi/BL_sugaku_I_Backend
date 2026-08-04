import json
import os
import re
import time
from glob import glob
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

# =========================================================
# ⚙️ 設定・初期化 (.env 複数APIキー対応 ＆ 強制上書き)
# =========================================================
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

# 🌟 override=True を指定してターミナル内の古い環境変数を強制上書き
load_dotenv(dotenv_path=ENV_PATH, override=True)

# 不可視文字(BOM等)や引用符を除去するクレンジング関数
def clean_key(k_str):
    if not k_str:
        return ""
    return k_str.strip().strip("'\"").replace('\ufeff', '')

# GEMINI_API_KEYS と GEMINI_API_KEY の両方に対応し、どちらでもカンマで分割する
raw_keys = os.environ.get("GEMINI_API_KEYS", "") or os.environ.get("GEMINI_API_KEY", "")
API_KEYS = [clean_key(k) for k in raw_keys.split(",") if clean_key(k)]

if not API_KEYS:
    raise ValueError("❌ .env ファイルに GEMINI_API_KEYS または GEMINI_API_KEY が設定されていません。")

current_key_index = 0
MODEL_NAME = "gemini-3.6-flash"

def get_client():
    """現在のインデックスのAPIキーでGemini Clientを生成"""
    global current_key_index
    key = API_KEYS[current_key_index]
    return genai.Client(api_key=key)

def rotate_key():
    """次のAPIキーへローテーション"""
    global current_key_index
    if len(API_KEYS) <= 1:
        print("      ⚠️ 登録されているAPIキーが1つのため、キー切り替えができません。")
        return False
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    masked_key = f"{API_KEYS[current_key_index][:6]}...{API_KEYS[current_key_index][-4:]}" if len(API_KEYS[current_key_index]) > 10 else "INVALID"
    print(f"      🔄 APIキーを切り替えました (Key {current_key_index + 1}/{len(API_KEYS)}: {masked_key})")
    return True

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
# 🔄 API 呼び出し (JSON修復 ＋ 制限検知キー切り替え ＋ ファイル権限エラー対応)
# =========================================================
def generate_content_and_parse_json(contents, response_schema=None, max_retries=None):
    if max_retries is None:
        # キーの数の2倍までリトライを許可する（8キーなら16回）
        max_retries = max(5, len(API_KEYS) * 2)

    config_kwargs = {
        "temperature": 0.1,
        "response_mime_type": "application/json"
    }
    if response_schema:
        config_kwargs["response_schema"] = response_schema
        
    config = types.GenerateContentConfig(**config_kwargs)

    for attempt in range(1, max_retries + 1):
        try:
            client = get_client()
            print(f"      [通信開始: 試行 {attempt}/{max_retries}]")
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config
            )
            print("      [通信完了]")
            
            # Markdownブロックの除去
            text = response.text
            text = re.sub(r'^```json\s*', '', text.strip(), flags=re.IGNORECASE)
            text = re.sub(r'\s*```$', '', text)
            
            # JSONのパースと自動修復
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                fixed_text = text.replace('\\', '\\\\').replace('\\\\"', '\\"').replace('\\\\n', '\\n')
                try:
                    return json.loads(fixed_text)
                except json.JSONDecodeError as je:
                    print(f"      ⚠️ AI出力のJSON形式エラー(LaTeXエスケープ起因等)。安全に再生成します... (試行 {attempt}/{max_retries})")
                    if attempt == max_retries:
                        raise RuntimeError(f"❌ JSONパースが{max_retries}回失敗しました: {je}")
                    time.sleep(3)
                    continue

        except errors.APIError as e:
            err_str = str(e).lower()
            if any(k in err_str for k in ["429", "quota", "resource_exhausted", "api_key_invalid", "invalid_argument"]):
                curr_k = API_KEYS[current_key_index]
                masked_k = f"{curr_k[:6]}...{curr_k[-4:]}" if len(curr_k) > 10 else "INVALID"
                print(f"      ⚠️ API制限/無効キーを検知しました (Key: {masked_k}, 試行 {attempt}/{max_retries})")
                if rotate_key():
                    print("      ⏩ 新しいAPIキーで即座にリトライします...")
                    
                    # 🌟 [重要] 渡されたcontentsにFileオブジェクトが含まれている場合、
                    # キーが変わると100% 403エラーになるため、APIを叩かずに再アップロードを要求する
                    has_file = False
                    if isinstance(contents, list):
                        for c in contents:
                            if hasattr(c, 'name') and hasattr(c, 'uri'):
                                has_file = True
                    if has_file:
                        raise Exception("NEED_REUPLOAD")
                    
                    continue
                else:
                    print("      ⏳ 40秒待機後にリトライします...")
                    time.sleep(40)
            elif "403" in err_str or "permission_denied" in err_str:
                print(f"      ⚠️ 403アクセス拒否エラーを検知。別アカウントでのアップロードが必要なため再アップロードを要求します。")
                raise Exception("NEED_REUPLOAD")
            elif "503" in err_str or "unavailable" in err_str:
                print(f"      ⚠️ 503サーバーエラー (試行 {attempt}/{max_retries}): 30秒待機後リトライ...")
                time.sleep(30)
            else:
                if attempt == max_retries: raise e
                print(f"      ⚠️ API通信エラー ({e}) (試行 {attempt}/{max_retries}): 20秒待機後リトライ...")
                time.sleep(20)
        except Exception as e:
            # NEED_REUPLOAD 例外はそのまま上に投げる
            if "NEED_REUPLOAD" in str(e):
                raise e
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
   - 🌟【重要ルール】タイトルや単元名に「〜の利用」「〜の応用」と含まれていても、「概念・条件・公式の理論的な説明」に終始している場合は、必ず `concept_lecture` に分類してください。

2. `exercise_walkthrough` (例題演習)
   - 教材内の具体的な「大問」「確認問題」「問題」の計算手順・解法解説を行っている場合。

3. `concept_application` (概念の応用・利用)
   - すでに学習した概念や公式を利用して、「例」において、文章題や図形問題などの「応用問題」を解き、知識の活用方法を解説している場合。

【★最重要: LaTeXとJSONエスケープの絶対ルール★】
理由(reason)の記述にLaTeX数式（$...$）を含める場合、必ずバックスラッシュを二重にエスケープ（例: \\\\frac）してください。

【動画名】: {video_name}

【教材テキスト (一部)】:
{textbook_content[:1500]}

【字幕データ (冒頭2000文字)】:
{vtt_content[:2000]}
"""
    print(f"  ├─ 🔍 [事前推論] 動画 '{video_name}' の役割を教材MDと照合して自動判定中...")
    
    try:
        result = generate_content_and_parse_json([prompt], schema)
        role = result.get("role", "exercise_walkthrough")
        reason = result.get("reason", "判定成功")
        
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
    print(f"=== 🎬 [Phase 2 Ver 2.5.4] 403検知・動的再アップロード対応版 起動 ===")
    print(f"   🔑 読み込み済み有効APIキー数: {len(API_KEYS)} 個")
    first_key_masked = f"{API_KEYS[0][:6]}...{API_KEYS[0][-4:]}" if len(API_KEYS[0]) > 10 else "INVALID"
    print(f"   👉 現在使用中のキー: {first_key_masked}")

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

        # 1. ロールの自動判定 (テキストのみなのでキー切替の巻き添えを食わない)
        role = detect_video_role(vtt_content, mp4_path, textbook_content)

        # ---------------------------------------------------------
        # 2. 動画アップロードと解析ループ (APIキー切り替え・403対策)
        # ---------------------------------------------------------
        max_upload_retries = max(5, len(API_KEYS) * 2)
        upload_attempt = 0
        segments = []

        while upload_attempt < max_upload_retries:
            upload_attempt += 1
            print(f"  ├─ ⏳ 動画をGemini APIへアップロード中... (試行 {upload_attempt}/{max_upload_retries})")
            
            upload_client = get_client()
            try:
                uploaded_video = upload_client.files.upload(file=mp4_path)
            except Exception as e:
                err_str = str(e).lower()
                if any(k in err_str for k in ["429", "quota", "api_key_invalid"]):
                    print("  ├─ ⚠️ アップロード時にAPI制限を検知。キーを切り替えて再試行します...")
                    rotate_key()
                    continue
                print(f"❌ {mp4_path} のアップロードに失敗しました: {e}")
                break

            print("  ├─ ⏳ Google側の動画処理完了を待機しています...")
            try:
                while uploaded_video.state.name == "PROCESSING":
                    time.sleep(5)
                    uploaded_video = upload_client.files.get(name=uploaded_video.name)
            except Exception as e:
                pass # 一時的な通信エラーは無視してステータスチェックを続行

            if uploaded_video.state.name == "FAILED":
                print(f"❌ 動画処理に失敗しました: {mp4_path}")
                break

            print("  ├─ 🟢 動画の準備完了 (ACTIVE)")

            # 3. 解析プロンプトの出し分け
            if role == "concept_lecture":
                granularity_instruction = "【概念理解特化・極細分割】: 1〜3分単位のミクロな解説ステップ（公式の導入、意味、証明、注意点など）を細かく分割してください。"
            else:
                granularity_instruction = "【問題解説特化・超極細ステップ分割】: 各小問の計算の途中経過、数十秒〜1、2分単位の微細な計算ステップ（立式、変形、答えの確認など）ごとに徹底的に細かくセグメントを細分化してください。"

            prompt = f"""動画のタイムラインを解析し、詳細なチャプター（セグメント）を作成してください。

【最優先：粒度の超極細化ルール】
- 指示された通りの極細粒度（{granularity_instruction}）で網羅して作成してください。
- 各セグメントの開始時間（`start_time`）と終了時間（`end_time`）を MM:SS 形式で正確に記録してください。

【★最重要：黒板・スライドのLaTeX書き起こし (blackboard_ocr) とJSONエスケープ★】
- 動画内の数式・図の情報を読み取り、`blackboard_ocr` 項目や `explanation_summary` へLaTeX形式（$...$ または $$...$$）で書き起こしてください。
- 出力はJSONフォーマットとなります。JSON内でLaTeXを記述する際は、**必ずバックスラッシュを二重にエスケープ（例: \\\\frac, \\\\sqrt）** してください。

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

            try:
                print("  ├─ 🧠 マルチモーダル超極細解析＆板書OCRを実行中...")
                result_data = generate_content_and_parse_json([uploaded_video, prompt], schema)
                segments = result_data.get("segments", [])
                
                try:
                    upload_client.files.delete(name=uploaded_video.name)
                    print("  └─ 🧹 クラウド上の動画一時ファイルを削除しました。")
                except: pass
                
                break # 解析大成功！whileループを抜ける

            except Exception as e:
                # 🌟 APIキーが切り替わった事によるファイルアクセスエラーを捕捉
                if "NEED_REUPLOAD" in str(e):
                    print("  ├─ 🔄 APIキーが切り替わりました。別アカウントとなるため、動画を新しいキーで再アップロードして解析を再開します...")
                    try:
                        # 念のため古いキーのクライアントで消去を試みる
                        upload_client.files.delete(name=uploaded_video.name)
                    except: pass
                    continue # whileループの最初（アップロード）に戻る
                else:
                    print(f"  ├─ ❌ 予期せぬ解析エラー: {e}")
                    try:
                        upload_client.files.delete(name=uploaded_video.name)
                    except: pass
                    break

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

        # 5. トピック名の正規化処理
        if role == "exercise_walkthrough":
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

        all_video_maps.append({
            "video_file": os.path.basename(mp4_path),
            "vtt_file": os.path.basename(vtt_path) if vtt_path else None,
            "role": role,
            "segments": segments
        })
        time.sleep(3)

    output_data = {
        "engine_version": "2.5.4_403_reupload_robust",
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