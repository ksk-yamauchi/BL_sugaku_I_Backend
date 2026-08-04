import os
import json
import time
import re
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
    return genai.Client(api_key=API_KEYS[current_key_index])

def rotate_key():
    """次のAPIキーへローテーション"""
    global current_key_index
    if len(API_KEYS) <= 1:
        print("   ⚠️ 登録されているAPIキーが1つのため、キー切り替えができません。")
        return False
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    masked_key = f"{API_KEYS[current_key_index][:6]}...{API_KEYS[current_key_index][-4:]}" if len(API_KEYS[current_key_index]) > 10 else "INVALID"
    print(f"   🔄 APIキーを切り替えました (Key {current_key_index + 1}/{len(API_KEYS)}: {masked_key})")
    return True

# =========================================================
# 🔄 API 呼び出し (JSON修復 ＋ 制限検知キー切り替え ＋ 動的リトライ)
# =========================================================
def generate_content_and_parse_json(prompt, max_retries=None):
    if max_retries is None:
        # キーの数の2倍までリトライを許可する
        max_retries = max(5, len(API_KEYS) * 2)

    config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)

    for attempt in range(1, max_retries + 1):
        try:
            client = get_client()
            print(f"      [通信開始: 試行 {attempt}/{max_retries}]")
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
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
                # LaTeXの \ をエスケープし忘れたエラーに対する自動修復
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
                    continue
                else:
                    print("      ⏳ 40秒待機後にリトライします...")
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

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(CURRENT_DIR, "output_result")

PHASE1_FILE = os.path.join(OUTPUT_DIR, "final_knowledge_graph.json")
PHASE2_FILE = os.path.join(OUTPUT_DIR, "lecture_map.json")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "final_knowledge_graph_complete.json")

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def time_to_seconds(t_str):
    """ 'MM:SS' 形式の文字列を秒数（整数）に変換する """
    try:
        m, s = map(int, t_str.split(':'))
        return m * 60 + s
    except:
        return -1

def execute_phase3_alignment(phase1_data, phase2_data):
    print("🚀 [Phase 3] 概念・確認問題・動画の三位一体アライメントを実行中...")

    concepts = phase1_data.get("extracted_concepts", [])
    questions = phase1_data.get("questions", [])
    alignments = phase1_data.get("alignments", [])
    video_segments = phase2_data.get("videos", [])

    prompt = f"""あなたは教育工学とカリキュラム・アライメントのエキスパートです。
以下の【Phase 1: 概念・問題データ】と【Phase 2: 動画タイムラインデータ】を読み込み、
「概念」および「確認問題」と、「動画セグメント」を紐づけてください。

【Phase 1: 概念・問題データ】
{json.dumps({"concepts": concepts, "questions": questions, "alignments": alignments}, ensure_ascii=False, indent=2)}

【Phase 2: 動画タイムラインデータ】
{json.dumps(video_segments, ensure_ascii=False, indent=2)}

【★マッチングの絶対ルール★】
1. concept_video_alignments (概念と動画の紐付け):
   各概念（concept_name）について、その概念を「直接解説しているインプット講義」のセグメントを探し紐付けてください。
   - alignment_typeは "concept_input" (概念の直接解説) としてください。

2. question_video_alignments (問題と動画の紐付け):
   各確認問題（question_number）について、それを解くための解説動画セグメントを探してください。
   - alignment_typeは "direct_explanation" (例題の直接解説) または "prerequisite" (前提概念の解説) を指定してください。

3. video_file の完全一致指定 (【最重要】伏字・省略の絶対禁止):
   - `video_file` の項目には、必ず【Phase 2: 動画タイムラインデータ】内に存在する実際のファイル名（例: `BL_sugaku_I_01-1-3.mp4` など）をそのまま正確に記述してください。

【★最重要: LaTeXとJSONエスケープの絶対ルール★】
`reasoning` (理由付け) のテキスト内にLaTeX数式（$...$）を含める場合、**必ずバックスラッシュを二重にエスケープ（例: \\\\frac, \\\\subset）** してください。JSONフォーマットとしてInvalidにならないよう細心の注意を払ってください。

【出力JSONフォーマット】:
{{
  "concept_video_alignments": [
    {{
      "concept_name": "...",
      "aligned_videos": [
        {{
          "video_file": "Phase 2に存在する実際の動画ファイル名",
          "start_time": "MM:SS",
          "alignment_type": "concept_input",
          "reasoning": "なぜこの動画セグメントがこの概念の解説に該当するかの理由"
        }}
      ]
    }}
  ],
  "question_video_alignments": [
    {{
      "question_number": "...",
      "aligned_videos": [
        {{
          "video_file": "Phase 2に存在する実際の動画ファイル名",
          "start_time": "MM:SS",
          "alignment_type": "direct_explanation | prerequisite",
          "reasoning": "なぜこの動画セグメントが該当するかの理由"
        }}
      ]
    }}
  ]
}}
"""
    # ★ APIを叩いてパースまで完結する堅牢な関数を使用
    return generate_content_and_parse_json(prompt)

def main():
    print("=== 🏁 【Ver 12.1 GNN-KT & ファジーマッチOCR結合対応】Phase 3 起動 ===")
    print(f"   🔑 読み込み済み有効APIキー数: {len(API_KEYS)} 個")
    first_key_masked = f"{API_KEYS[0][:6]}...{API_KEYS[0][-4:]}" if len(API_KEYS[0]) > 10 else "INVALID"
    print(f"   👉 現在使用中のキー: {first_key_masked}")
    
    phase1_data = load_json(PHASE1_FILE)
    phase2_data = load_json(PHASE2_FILE)
    
    if not phase1_data:
        print("❌ Phase 1 のデータが見つかりません。先に Phase 1 を実行してください。")
        return

    if not phase2_data:
        print("⚠️ Phase 2 のデータがありません。動画リンクなしで最終JSONを生成します。")
        final_graph = phase1_data.copy()
        final_graph["metadata"]["engine_version"] = "12.0_video_skipped"
    else:
        alignment_result = execute_phase3_alignment(phase1_data, phase2_data)
        video_segments = phase2_data.get("videos", [])
        
        concept_alignments = {item["concept_name"]: item["aligned_videos"] for item in alignment_result.get("concept_video_alignments", [])}
        question_alignments = {str(item["question_number"]): item["aligned_videos"] for item in alignment_result.get("question_video_alignments", [])}
        
        # 🌟 Phase 2の全データを安全に結合する関数（ファジーマッチ搭載）
        def enrich_videos(aligned_list, p2_videos):
            enriched = []
            for v in aligned_list:
                v_file = v.get("video_file", "")
                s_time = v.get("start_time", "")
                s_sec = time_to_seconds(s_time)
                new_v = v.copy()
                
                matched_seg = None
                for p2v in p2_videos:
                    if p2v.get("video_file") == v_file:
                        segments = p2v.get("segments", [])
                        
                        # 1. まずは完全一致を探す
                        for seg in segments:
                            if seg.get("start_time") == s_time:
                                matched_seg = seg
                                break
                                
                        # 2. 🌟完全一致がなければ、一番近い時間のセグメントを探す（フォールバック）
                        if not matched_seg and s_sec >= 0 and segments:
                            matched_seg = min(segments, key=lambda seg: abs(time_to_seconds(seg.get("start_time", "")) - s_sec))
                
                # 結合 (板書OCRや要約をPhase 2からマージ)
                if matched_seg:
                    new_v["end_time"] = matched_seg.get("end_time", "")
                    new_v["topic"] = matched_seg.get("topic", "")
                    new_v["blackboard_ocr"] = matched_seg.get("blackboard_ocr", "")
                    new_v["explanation_summary"] = matched_seg.get("explanation_summary", "")
                
                enriched.append(new_v)
            return enriched

        # Phase 1のデータ（観点タグや重み付き前提知識など）をそのままディープコピーして動画リンクを追加
        enriched_concepts = []
        for c in phase1_data.get("extracted_concepts", []):
            c_copy = c.copy()
            raw_aligned = concept_alignments.get(c["concept_name"], [])
            c_copy["aligned_videos"] = enrich_videos(raw_aligned, video_segments)
            enriched_concepts.append(c_copy)
            
        enriched_questions = []
        for q in phase1_data.get("questions", []):
            q_copy = q.copy()
            q_num = str(q.get("question_number", ""))
            raw_aligned = question_alignments.get(q_num, [])
            q_copy["aligned_videos"] = enrich_videos(raw_aligned, video_segments)
            enriched_questions.append(q_copy)
            
        final_graph = {
            "metadata": phase1_data.get("metadata", {}),
            "extracted_concepts": enriched_concepts,
            "questions_with_video_alignment": enriched_questions,
            "alignments": phase1_data.get("alignments", []),
            "raw_alignments": phase1_data.get("raw_alignments", [])
        }
        # メタデータをVer 12.0用に更新
        final_graph["metadata"]["engine_version"] = "12.0_gnn_kt_video_enriched"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_graph, f, ensure_ascii=False, indent=2)
        
    print(f"🎉 統合完了！概念と動画が直接リンクされ、板書データも安全に結合されました。 💾 保存先: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()