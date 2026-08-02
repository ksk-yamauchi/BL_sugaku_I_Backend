# 1. ターミナルで事前に以下のコマンドを実行してライブラリをインストールしてください
# pip install plyer

from plyer import notification
import platform
import os

def show_completion_notification():
    """バッチ処理完了時にポップアップ通知と音を鳴らす関数"""
    try:
        # 画面右下（Macは右上）にポップアップ通知を出す
        notification.notify(
            title="スタサプRAG バッチ完了",
            message="全PARTの解析およびDB構築が完了しました！",
            app_name="Stasap RAG Engine",
            timeout=10  # 10秒間表示
        )
        
        # ついでにOSの標準の完了音を鳴らす
        if platform.system() == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif platform.system() == "Darwin": # Macの場合
            os.system('afplay /System/Library/Sounds/Glass.aiff')
            
    except Exception as e:
        print(f"通知の送信に失敗しましたが、処理自体は完了しています: {e}")

# =======================================================
# 実際のバッチファイル（run_single_part_batch.py など）での組み込みイメージ
# =======================================================
def main():
    print("バッチ処理を開始します...")
    # ... (既存の重い処理) ...
    print("バッチ処理が完了しました！")
    
    # 一番最後にこの関数を呼び出すだけです！
    show_completion_notification()

if __name__ == "__main__":
    main()