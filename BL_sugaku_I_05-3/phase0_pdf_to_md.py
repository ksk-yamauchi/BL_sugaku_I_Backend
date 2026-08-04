import os
import time
import shutil
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
MODEL_ID = "gemini-3.6-flash"

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

def generate_content_with_key_rotation(uploaded_file, prompt, max_retries=None):
    """429制限や400無効キーエラー検知時に自動でAPIキーを切り替えて即座に再トライする関数"""
    if max_retries is None:
        # ★ キーの数の2倍までリトライを許可する（8キーなら16回）
        max_retries = max(5, len(API_KEYS) * 2)

    for attempt in range(1, max_retries + 1):
        try:
            client = get_client()
            print(f"   [通信開始: 試行 {attempt}/{max_retries}]")
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[uploaded_file, prompt]
            )
            print("   [通信完了]")
            return response
        except errors.APIError as e:
            err_str = str(e).lower()
            if any(k in err_str for k in ["429", "quota", "resource_exhausted", "api_key_invalid", "invalid_argument"]):
                curr_k = API_KEYS[current_key_index]
                masked_k = f"{curr_k[:6]}...{curr_k[-4:]}" if len(curr_k) > 10 else "INVALID"
                print(f"   ⚠️ APIエラー/無効キーを検知しました (Key: {masked_k}, 試行 {attempt}/{max_retries})")
                if rotate_key():
                    print("   ⏩ 新しいAPIキーで即座にリトライします...")
                    # 🌟 [重要] ファイル解析の場合、キーが変わると100% 403エラーになるため再アップロードを要求
                    raise Exception("NEED_REUPLOAD")
                else:
                    print("   ⏳ 40秒待機後に再トライします...")
                    time.sleep(40)
            elif "403" in err_str or "permission_denied" in err_str:
                print(f"   ⚠️ 403アクセス拒否エラーを検知。別アカウントでのアップロードが必要なため再アップロードを要求します。")
                raise Exception("NEED_REUPLOAD")
            elif "503" in err_str or "unavailable" in err_str:
                print(f"   ⚠️ 503サーバーエラー (試行 {attempt}/{max_retries}): 30秒待機後に再トライ...")
                time.sleep(30)
            else:
                if attempt == max_retries: raise e
                print(f"   ⚠️ APIエラー ({e}) (試行 {attempt}/{max_retries}): 15秒待機後に再トライ...")
                time.sleep(15)
        except Exception as e:
            if "NEED_REUPLOAD" in str(e):
                raise e
            if attempt == max_retries: raise e
            print(f"   ⚠️ 通信エラー ({e}) (試行 {attempt}/{max_retries}): 15秒待機後に再トライ...")
            time.sleep(15)
    raise RuntimeError("❌ リトライ上限超過")

def main():
    print("=== 📄 [Phase 0 Ver 1.2] 403検知・動的再アップロード対応版 起動 ===")
    print("   💡 [強化版] レイアウト構造化 ＋ 図形の自動言語化 を有効化")
    print(f"   🔑 読み込み済み有効APIキー数: {len(API_KEYS)} 個")
    first_key_masked = f"{API_KEYS[0][:6]}...{API_KEYS[0][-4:]}" if len(API_KEYS[0]) > 10 else "INVALID"
    print(f"   👉 現在使用中のキー: {first_key_masked}")
    
    pdf_files = glob("*.pdf")
    if not pdf_files:
        print("   ⚠️ PDFファイルが見つかりません。Phase 0 をスキップします。")
        return

    pdf_path = pdf_files[0]
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    md_filename = f"{base_name}_clean.md"

    if os.path.exists(md_filename):
        print(f"   ✅ 既に {md_filename} が存在します。API枠節約のため変換をスキップします。")
        return

    temp_pdf_path = "temp_processing_file.pdf"
    shutil.copy(pdf_path, temp_pdf_path)

    try:
        max_upload_retries = max(5, len(API_KEYS) * 2)
        upload_attempt = 0

        while upload_attempt < max_upload_retries:
            upload_attempt += 1
            print(f"   ⬆️ PDFファイルをアップロード中: {pdf_path} (試行 {upload_attempt}/{max_upload_retries})")
            
            upload_client = get_client()
            try:
                uploaded_file = upload_client.files.upload(file=temp_pdf_path)
            except Exception as e:
                err_str = str(e).lower()
                if any(k in err_str for k in ["429", "quota", "api_key_invalid"]):
                    print("   ⚠️ アップロード時にAPI制限を検知。キーを切り替えて再試行します...")
                    rotate_key()
                    continue
                print(f"❌ {pdf_path} のアップロードに失敗しました: {e}")
                break

            print("   ⏳ Google側のPDF処理完了を待機しています...")
            try:
                while uploaded_file.state.name == "PROCESSING":
                    time.sleep(5)
                    uploaded_file = upload_client.files.get(name=uploaded_file.name)
            except Exception as e:
                pass # 通信エラーは無視して続行

            if uploaded_file.state.name == "FAILED":
                print(f"❌ PDFファイルの処理に失敗しました。")
                break

            print("   🧠 GeminiによるMarkdown変換（および図形の言語化）を実行中...")
            prompt = """
あなたは、PDFの内容を正確に読み取り、Markdown形式のテキストデータに変換する高校数学専門のアシスタントです。
以下のルールに従って、PDFからテキストおよび「図形・グラフの意味情報」を抽出・成形してください。

【基本ルール】
1. 読み取った内容は、標準的なMarkdown形式で出力してください。見出し、箇条書き、太字などを適切に使用し、読みやすい構造にしてください。
2. 数学の数式や記号は、正確に読み取り、LaTeX形式に変換してください。インライン数式は `$` で、ブロック数式（独立した行の数式）は `$$` で囲んでください。
3. 空欄を示す四角形などの図形は、文脈に合わせて空欄とわかる記号や変数名（例: [ ア ]、x、y、□など）に置き換えてください。
4. 出力は、Markdownテキストのみとしてください。Markdownのコードブロック（```markdown ... ```）で囲む必要はありません。そのままテキストとして出力してください。

【★重要：図形・グラフの言語化ルール（検索DB用）】
PDF内にグラフ、ベン図、幾何図形、数直線、統計グラフなどが含まれる場合、視覚的な情報を無視せず、以下の基準に従って `[図の説明: 〇〇]` という形式でテキスト化して挿入してください。これが検索エンジンの重要なメタデータとなります。

・関数グラフ（1次・2次関数など）
  - グラフの形状（上に凸/下に凸の放物線、右上がりの直線など）
  - 頂点、軸、x軸やy軸との交点などの座標
  - 定義域の指定（実線・破線の区別）や、最大値・最小値の該当箇所
  - 【⚠️座標読み取りの強い注意】グラフ内の数値を読む際は、「その数値がどの軸上のものか」「破線でどの点と結ばれているか」を慎重に観察してください。例えば、x軸上に「3」、y軸上に「-9」があり、放物線がx軸の「3」に接している場合、頂点は(3, 0)であり、y切片が -9 です。近くにある数字を安易に組み合わせて「頂点が(3, -9)」と誤認しないよう注意してください。
  - 記述例: `[図の説明: 頂点が(2, -1)で下に凸の放物線のグラフ。x=2で最小値をとる実線が描かれている。]`

・数直線・不等式の領域
  - 示されている範囲（例：x > 2、-1 ≦ x < 3）
  - 白丸（含まない）と黒丸（含む）の区別、共通範囲（斜線部分）
  - 記述例: `[図の説明: 数直線上で、-2(黒丸)から3(白丸)までの範囲に斜線が引かれた図。-2 ≦ x < 3 を表す。]`

・ベン図（集合・命題）
  - 円の包含関係や交わり方
  - 斜線や色が塗られている部分が何を表しているか（共通部分、和集合、補集合など）
  - 記述例: `[図の説明: 全体集合Uの中で集合AとBの円が交わり、AとBの重なる部分（共通部分）に斜線が引かれたベン図。]`

・幾何図形（三角比・平面・空間図形）
  - 図形の形状（直角三角形、直方体、円、単位円と動径など）
  - 明記されている辺の長さ、角の大きさ、直角の位置
  - 記述例: `[図の説明: 角Cが直角の直角三角形ABC。AB=5、BC=3、角A=θと示されている。]`

・データの分析（統計グラフ）
  - ヒストグラム：データの分布傾向
  - 箱ひげ図：最小値、四分位数、最大値、外れ値のおおよその位置関係
  - 散布図：点の分布傾向（右上がり＝正の相関、右下がり＝負の相関）
  - 記述例: `[図の説明: 強い負の相関（右下がりの傾向）を示す散布図。]`
"""
            try:
                response = generate_content_with_key_rotation(uploaded_file, prompt)

                with open(md_filename, "w", encoding="utf-8") as f:
                    f.write(response.text)
                
                print(f"   💾 変換完了！ 保存先: {md_filename}")

                try:
                    upload_client.files.delete(name=uploaded_file.name)
                    print("   🗑️ クラウド上のPDFキャッシュを削除しました。")
                except Exception:
                    pass

                break # 解析大成功！ループを抜ける

            except Exception as e:
                # 🌟 APIキーが切り替わった事によるファイルアクセスエラーを捕捉
                if "NEED_REUPLOAD" in str(e):
                    print("   🔄 APIキーが切り替わりました。別アカウントとなるため、PDFを新しいキーで再アップロードして変換を再開します...")
                    try:
                        upload_client.files.delete(name=uploaded_file.name)
                    except: pass
                    continue # whileループの最初に戻る
                else:
                    print(f"   ❌ 予期せぬエラー: {e}")
                    try:
                        upload_client.files.delete(name=uploaded_file.name)
                    except: pass
                    break

    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

if __name__ == "__main__":
    main()