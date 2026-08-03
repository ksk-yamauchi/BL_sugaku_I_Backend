import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# =========================================================
# ⚙️ 設定・初期化 (.env 対応)
# =========================================================
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ .env ファイルに GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=API_KEY)
# ※Phase1に合わせたモデル名を指定
MODEL_NAME = "gemini-3.6-flash"

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

def execute_phase3_alignment(phase1_data, phase2_data):
    print("🚀 [Phase 3] 概念・確認問題・動画の三位一体アライメントを実行中...")

    # Phase 1 のデータ（概念リスト、問題リスト、アライメント）
    concepts = phase1_data.get("extracted_concepts", [])
    questions = phase1_data.get("questions", [])
    alignments = phase1_data.get("alignments", [])
    
    # Phase 2 のデータ（動画チャプター要約）
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

【出力JSONフォーマット】:
{{
  "concept_video_alignments": [
    {{
      "concept_name": "...",
      "aligned_videos": [
        {{
          "video_file": "...",
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
          "video_file": "...",
          "start_time": "MM:SS",
          "alignment_type": "direct_explanation | prerequisite",
          "reasoning": "なぜこの動画セグメントが該当するかの理由"
        }}
      ]
    }}
  ]
}}
"""
    
    # APIリクエスト
    response = client.models.generate_content(
        model=MODEL_NAME, 
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
    )
    
    return json.loads(response.text)

def main():
    print("=== 🏁 【Ver 10.0 概念・動画ダイレクトリンク対応】Phase 3 起動 ===")
    
    phase1_data = load_json(PHASE1_FILE)
    phase2_data = load_json(PHASE2_FILE)
    
    if not phase1_data:
        print("❌ Phase 1 のデータが見つかりません。先に Phase 1 を実行してください。")
        return

    # Phase 2 が無い場合（スキップ時）は空の状態で統合
    if not phase2_data:
        print("⚠️ Phase 2 のデータがありません。動画リンクなしで最終JSONを生成します。")
        final_graph = phase1_data.copy()
        final_graph["metadata"]["engine_version"] = "10.0_video_skipped"
    else:
        # LLMによる三位一体アライメント
        alignment_result = execute_phase3_alignment(phase1_data, phase2_data)
        
        # 紐付け結果をマージ
        concept_alignments = {item["concept_name"]: item["aligned_videos"] for item in alignment_result.get("concept_video_alignments", [])}
        question_alignments = {str(item["question_number"]): item["aligned_videos"] for item in alignment_result.get("question_video_alignments", [])}
        
        # 元のPhase 1データに動画リンクを埋め込む
        enriched_concepts = []
        for c in phase1_data.get("extracted_concepts", []):
            c_copy = c.copy()
            c_copy["aligned_videos"] = concept_alignments.get(c["concept_name"], [])
            enriched_concepts.append(c_copy)
            
        enriched_questions = []
        for q in phase1_data.get("questions", []):
            q_copy = q.copy()
            q_num = str(q.get("question_number", ""))
            q_copy["aligned_videos"] = question_alignments.get(q_num, [])
            enriched_questions.append(q_copy)
            
        final_graph = {
            "metadata": phase1_data.get("metadata", {}),
            "extracted_concepts": enriched_concepts,
            "questions_with_video_alignment": enriched_questions,
            "alignments": phase1_data.get("alignments", []),
            "raw_alignments": phase1_data.get("raw_alignments", [])
        }
        final_graph["metadata"]["engine_version"] = "10.0_concept_video_hub"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_graph, f, ensure_ascii=False, indent=2)
        
    print(f"🎉 統合完了！概念と動画が直接リンクされました。 💾 保存先: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()