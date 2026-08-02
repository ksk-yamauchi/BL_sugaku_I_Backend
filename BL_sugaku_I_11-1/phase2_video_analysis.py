import os
import json
import time
from glob import glob
from dotenv import load_dotenv
from google import genai
from google.genai import types

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

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(CURRENT_DIR, "output_result")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "lecture_map.json")

def process_video_and_vtt(mp4_path, vtt_path):
    video_filename = os.path.basename(mp4_path)
    print(f"\n🎥 動画解析開始: {video_filename}")

    # 字幕ファイルの読み込み（字幕がある場合、LLMの理解精度が格段に上がるためプロンプトに含める）
    vtt_content = ""
    if os.path.exists(vtt_path):
        with open(vtt_path, "r", encoding="utf-8") as f:
            vtt_content = f.read()

    # 動画をGeminiへアップロード
    print(f"   ⬆️ 動画をアップロード中: {mp4_path}")
    uploaded_video = client.files.upload(file=mp4_path)

    # 処理完了を待機
    print("   ⏳ Google側の動画処理完了を待機しています...")
    while uploaded_video.state.name == "PROCESSING":
        print("      ... 処理中 ...")
        time.sleep(10)
        uploaded_video = client.files.get(name=uploaded_video.name)
    
    if uploaded_video.state.name == "FAILED":
        raise Exception(f"❌ 動画ファイルの処理に失敗しました: {video_filename}")

    print("   🧠 Geminiによる動画タイムライン解析を実行中...")
    prompt = f"""
あなたは教育動画のタイムライン・アナリストです。
アップロードされた講義動画と、以下の字幕データ（VTT形式）を解析し、動画の構成をチャプター分割してください。

【字幕データ】:
{vtt_content if vtt_content else "字幕データなし。動画の音声と映像から解析してください。"}

【★ルール★】
1. 動画を意味のある数分単位のチャプター（セグメント）に分割してください。
2. 各チャプターの「開始時間（start_time）」を MM:SS 形式で記録してください。
3. 各チャプターが「概念の解説（concept_input）」なのか「例題・確認問題の解説（direct_explanation）」なのかを判定してください。
4. そのチャプターで解説されている内容の要約（summary）を記載してください。

【出力JSONフォーマット】:
{{
  "video_file": "{video_filename}",
  "segments": [
    {{
      "start_time": "00:00",
      "type": "concept_input または direct_explanation",
      "summary": "このチャプターで解説されている内容の要約"
    }}
  ]
}}
"""

   # 🌟 429エラー対策：最大3回まで、30秒待機して自動リトライする仕組み
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME, 
                contents=[uploaded_video, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
            )
            break  # 成功したらループを抜ける
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"      ⚠️ API制限(429)を検知。30秒待機して再挑戦します... ({attempt + 1}/{max_retries})")
                time.sleep(30)  # 30秒間プログラムを一時停止
            else:
                # 429以外の予期せぬエラーの場合はそのまま終了
                raise e
    else:
        # 3回連続で失敗した場合はエラーを出して止める
        raise Exception("❌ API制限によるリトライ上限に達しました。しばらく時間を置いてから再度実行してください。")
    
    # 🧹 API上のファイルをクリーンアップ（削除）
    try:
        client.files.delete(name=uploaded_video.name)
        print("   🗑️ クラウド上の動画キャッシュを削除しました。")
    except Exception:
        pass

    return json.loads(response.text)

def main():
    print("=== 🎬 [Phase 2] 講義動画タイムライン解析 起動 ===")
    
    mp4_files = glob("*.mp4")
    if not mp4_files:
        print("⚠️ フォルダ内に .mp4 ファイルが見つかりません。Phase 2 をスキップします。")
        return

    all_video_data = []
    for mp4_file in mp4_files:
        base_name = os.path.splitext(mp4_file)[0]
        vtt_file = f"{base_name}.vtt"
        
        try:
            video_data = process_video_and_vtt(mp4_file, vtt_file)
            all_video_data.append(video_data)
        except Exception as e:
            print(f"❌ {mp4_file} の解析中にエラーが発生しました: {e}")

    output_data = {
        "engine_version": "2.0_video_timeline",
        "videos": all_video_data
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 全動画の解析完了！ 💾 保存先: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()