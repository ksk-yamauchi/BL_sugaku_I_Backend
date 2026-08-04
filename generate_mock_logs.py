import json
import os
import random
import uuid
from datetime import datetime, timedelta

# =========================================================
# ⚙️ 設定
# =========================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(CURRENT_DIR, "global_vector_db_cache.json")
OUTPUT_LOG_FILE = os.path.join(CURRENT_DIR, "mock_student_logs.json")

NUM_STUDENTS = 40  # 1クラス分のシミュレーション人数

# ペルソナの定義と出現割合
PERSONAS = [
    {"type": "knowledge_heavy", "name": "知識・技能偏重型", "weight": 30},
    {"type": "thinking_heavy", "name": "思考力・判断力特化型", "weight": 20},
    {"type": "domain_biased", "name": "分野特化の偏り型", "weight": 20},
    {"type": "overall_strong", "name": "全体得意型", "weight": 15},
    {"type": "overall_weak", "name": "全体苦手型", "weight": 15}
]

# =========================================================
# 🧠 ペルソナに基づくベース正答率の計算
# =========================================================
def get_base_probability(student, question_competency, parent_concept):
    p_type = student["persona"]
    
    if p_type == "knowledge_heavy":
        return 0.85 if question_competency == "knowledge_skill" else 0.30
    elif p_type == "thinking_heavy":
        return 0.50 if question_competency == "knowledge_skill" else 0.80
    elif p_type == "domain_biased":
        # 得意分野なら90%、苦手分野なら20%、それ以外は50%
        if parent_concept in student.get("strong_domains", []):
            return 0.90
        elif parent_concept in student.get("weak_domains", []):
            return 0.20
        return 0.50
    elif p_type == "overall_strong":
        return 0.90
    elif p_type == "overall_weak":
        return 0.25
    return 0.50

# =========================================================
# 🎓 ログ生成メインロジック (GNN-KT 連鎖ペナルティ適用)
# =========================================================
def main():
    print("=== 🧪 [GNN-KT対応] ダミー学習ログ生成ツール 起動 ===")
    
    if not os.path.exists(DB_FILE):
        print(f"❌ 統合DBが見つかりません: {DB_FILE}")
        return

    with open(DB_FILE, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    questions = db_data.get("questions", [])
    concepts = db_data.get("concepts", [])
    
    if not questions:
        print("⚠️ データベースに問題が含まれていません。")
        return

    # 1. 概念マップの構築 (前提知識を引きやすくするため)
    concept_map = {c.get("concept_name"): c for c in concepts}

    # 2. 生徒データの生成
    students = []
    # 偏り型のための全親概念リスト抽出
    all_parents = list(set([c.get("parent_concept", "") for c in concepts if c.get("parent_concept")]))
    
    population = [p["type"] for p in PERSONAS]
    weights = [p["weight"] for p in PERSONAS]
    
    for i in range(NUM_STUDENTS):
        assigned_persona = random.choices(population, weights=weights, k=1)[0]
        student = {
            "student_id": f"STU_{str(uuid.uuid4())[:8].upper()}",
            "persona": assigned_persona,
            "mastery_state": {} # Level 3概念の理解度状態を保持 (True/False)
        }
        
        # 分野特化型の場合、ランダムに得意/苦手な親概念を割り当て
        if assigned_persona == "domain_biased" and len(all_parents) >= 2:
            sampled = random.sample(all_parents, 2)
            student["strong_domains"] = [sampled[0]]
            student["weak_domains"] = [sampled[1]]
            
        # 生徒ごとに、各親概念（Level 3）の潜在的な理解状態を事前決定しておく
        for parent in all_parents:
            base_prob = get_base_probability(student, "knowledge_skill", parent)
            # ベース確率が高いほど、その概念を「理解している（True）」可能性が高い
            student["mastery_state"][parent] = random.random() < base_prob
            
        students.append(student)

    print(f"   👥 {NUM_STUDENTS}人のペルソナ付き生徒データを生成しました。")

    # 3. 学習ログのシミュレーション
    logs = []
    base_time = datetime.now() - timedelta(days=30) # 過去30日間のログとする

    for student in students:
        for q in questions:
            q_num = q.get("question_number", "Unknown")
            q_competency = q.get("competency", "knowledge_skill")
            
            # 問題に紐づく概念（Level 4）を取得
            aligned_concept_names = q.get("aligned_concepts", [])
            target_concept = None
            for ac in aligned_concept_names:
                if ac in concept_map:
                    target_concept = concept_map[ac]
                    break
            
            if not target_concept:
                continue

            parent_concept = target_concept.get("parent_concept", "")
            prerequisites = target_concept.get("prerequisite_concepts", [])

            # ① ペルソナに基づくベース正答率
            prob = get_base_probability(student, q_competency, parent_concept)

            # ② 🌟 GNN-KT 連鎖ペナルティの適用
            for prereq in prerequisites:
                prereq_name = prereq.get("concept_name")
                dep_type = prereq.get("dependency_type", "supplementary")
                
                # 生徒がこの前提知識（Level 3）を理解していない場合、ペナルティ発動
                is_mastered = student["mastery_state"].get(prereq_name, True)
                if not is_mastered:
                    if dep_type == "mandatory":
                        prob *= 0.1 # 必須前提が抜けているとほぼ解けない
                    else:
                        prob *= 0.7 # 補足前提が抜けていると少し苦戦する

            # ③ 正誤の判定
            is_correct = random.random() < prob
            
            # 解答時間のシミュレーション (正解＝早い、不正解＝時間がかかる傾向)
            time_taken = random.randint(30, 120) if is_correct else random.randint(90, 300)
            
            log_entry = {
                "log_id": str(uuid.uuid4()),
                "student_id": student["student_id"],
                "persona": student["persona"],
                "question_number": q_num,
                "aligned_concept": target_concept.get("concept_name"),
                "parent_concept": parent_concept,
                "competency": q_competency,
                "is_correct": is_correct,
                "time_taken_sec": time_taken,
                "timestamp": (base_time + timedelta(days=random.randint(0, 30), minutes=random.randint(0, 1440))).isoformat()
            }
            logs.append(log_entry)

    # 4. JSON保存
    # 時間順にソート
    logs.sort(key=lambda x: x["timestamp"])
    
    output_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_students": NUM_STUDENTS,
            "total_logs": len(logs)
        },
        "logs": logs
    }

    with open(OUTPUT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"🎉 シミュレーション完了！")
    print(f"   📊 生成されたログ数: {len(logs)} 件")
    print(f"   💾 保存先: {OUTPUT_LOG_FILE}")

if __name__ == "__main__":
    main()