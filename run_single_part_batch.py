import os
import sys
import time
import subprocess
import platform
from glob import glob

# =========================================================
# ⚙️ 設定パラメータ（API無料枠・安全運用調整）
# =========================================================
# 各Phase実行間の安全ウェイト時間（秒）
INTERVAL_BETWEEN_PHASES = 60
# API制限（429エラー等）で失敗した際の自動リトライ回数と待機時間
MAX_RETRIES = 5
RETRY_WAIT_SECONDS = 60

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================================================
# 🔔 完了通知処理 (plyer 利用)
# =========================================================
def show_completion_notification(target_name=""):
    """バッチ処理完了時にポップアップ通知と音を鳴らす関数"""
    try:
        from plyer import notification
        
        msg = f"【{target_name}】の解析処理が正常に完了しました！" if target_name else "バッチ処理が正常に完了しました！"
        
        # デスクトップポップアップ通知
        notification.notify(
            title="スタサプRAG バッチ完了 🎓",
            message=msg,
            app_name="Stasap RAG Engine",
            timeout=10  # 10秒間表示
        )
        
        # OSの標準システム音を再生
        if platform.system() == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif platform.system() == "Darwin": # Macの場合
            os.system('afplay /System/Library/Sounds/Glass.aiff')
            
    except Exception as e:
        print(f"   ⚠️  通知の送信に失敗しましたが、処理自体は完了しています: {e}")

def run_phase_script(script_name, subfolder_path):
    """指定されたPhaseスクリプトを実行し、エラーが発生した場合は自動リトライする"""
    script_path = os.path.join(subfolder_path, script_name)
    if not os.path.exists(script_path):
        print(f"   ⚠️  [{script_name}] が見つかりません。スキップします。")
        return True

    print(f"\n▶️  実行中: {script_name} (対象: {os.path.basename(subfolder_path)})...")

    for attempt in range(1, MAX_RETRIES + 1):
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=subfolder_path,
            text=True,
            capture_output=False
        )

        if result.returncode == 0:
            print(f"✅ [{script_name}] 正常完了！")
            return True
        else:
            print(f"\n⚠️  [{script_name}] の実行中にエラーまたはAPI制限が発生しました。 (試行 {attempt}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES:
                print(f"⏳ API枠の回復を待つため、{RETRY_WAIT_SECONDS}秒間待機してから自動再実行します...")
                time.sleep(RETRY_WAIT_SECONDS)
            else:
                print(f"❌ [{script_name}] が{MAX_RETRIES}回失敗したため、処理を中断します。")
                return False

def process_subfolder(subfolder_name):
    """1つの子フォルダに対して Phase 0〜3 を順次実行"""
    subfolder_path = os.path.join(PARENT_DIR, subfolder_name)
    if not os.path.isdir(subfolder_path):
        print(f"❌ 指定されたフォルダが存在しません: {subfolder_name}")
        return

    print("=" * 80)
    print(f"🚀 【一括処理開始】 フォルダ: {subfolder_name}")
    print("=" * 80)

    # 0. Phase 0 実行 (PDF to MD)
    #if not run_phase_script("phase0_pdf_to_md.py", subfolder_path):
    #    return
    #print(f"☕ APIウェイト: {INTERVAL_BETWEEN_PHASES}秒待機中...")
    #time.sleep(INTERVAL_BETWEEN_PHASES)

    # 1. Phase 1 実行 (テキスト解析)
    if not run_phase_script("phase1_text_analysis_ontology.py", subfolder_path):
        return
    print(f"☕ APIウェイト: {INTERVAL_BETWEEN_PHASES}秒待機中...")
    time.sleep(INTERVAL_BETWEEN_PHASES)

    # 2. Phase 2 実行（動画解析）
    if not run_phase_script("phase2_video_analysis.py", subfolder_path):
        print("⚠️ Phase 2で中断したため、処理を停止します。")
        return
    print(f"☕ APIウェイト: {INTERVAL_BETWEEN_PHASES}秒待機中...")
    time.sleep(INTERVAL_BETWEEN_PHASES)

    # 3. Phase 3 実行（統合）
    if not run_phase_script("phase3_alignment_graph.py", subfolder_path):
        print("⚠️ Phase 3で中断したため、処理を停止します。")
        return

    print("\n" + "=" * 80)
    print(f"🎉 🎉 【完全完了】 {subfolder_name} の Phase 0 〜 Phase 3 が正常に完了しました！")
    print("=" * 80 + "\n")
    
    # 🔔 バッチ完了のポップアップ通知と音を発火
    show_completion_notification(subfolder_name)

def main():
    sub_dirs = [d for d in os.listdir(PARENT_DIR) if os.path.isdir(os.path.join(PARENT_DIR, d)) and "BL_sugaku" in d]
    sub_dirs.sort()

    if not sub_dirs:
        print("❌ 該当する子フォルダ（BL_sugaku_*）が見つかりません。")
        return

    print("\n📂 実行可能な単元フォルダ一覧:")
    for idx, d in enumerate(sub_dirs, 1):
        print(f"  [{idx}] {d}")

    choice = input("\n👉 実行したいフォルダの番号を入力してください（例: 1）: ").strip()
    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(sub_dirs):
            target_folder = sub_dirs[num - 1]
            process_subfolder(target_folder)
        else:
            print("❌ 無効な番号です。")
    else:
        print("❌ 数字を入力してください。")

if __name__ == "__main__":
    main()