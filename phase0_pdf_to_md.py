import os
import time
import shutil
from glob import glob
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ .env ファイルに GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-3.6-flash"

def main():
    print("=== 📄 [Phase 0 Ver 1.0] PDF to Markdown 変換処理開始 ===")
    print("   💡 [強化版] レイアウト構造化 ＋ 図形の自動言語化 を有効化")
    
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
        print(f"   ⬆️ PDFファイルをアップロード中: {pdf_path}")
        uploaded_file = client.files.upload(file=temp_pdf_path)

        print("   ⏳ Google側のPDF処理完了を待機しています...")
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(5)
            uploaded_file = client.files.get(name=uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            raise Exception("❌ PDFファイルの処理に失敗しました。")

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
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[uploaded_file, prompt]
        )

        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"   💾 変換完了！ 保存先: {md_filename}")

        try:
            client.files.delete(name=uploaded_file.name)
            print("   🗑️ クラウド上のPDFキャッシュを削除しました。")
        except Exception:
            pass

    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

if __name__ == "__main__":
    main()