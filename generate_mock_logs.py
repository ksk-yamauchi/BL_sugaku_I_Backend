import json
import random
import os
from datetime import datetime, timedelta

# ==========================================
# ⚙️ 設定
# ==========================================
DB_FILE = 'global_vector_db_cache.json'   # 読み込む統合データベース
OUTPUT_FILE = 'mock_student_logs.json'    # 出力するダミーログ
NUM_STUDENTS = 30                         # 生成する生徒の数

# ペルソナの定義
PERSONAS = [
    "知識・技能偏重型",      # 基礎はできるが応用が苦手
    "思考力・判断力特化型",  # 基礎抜けがあるが応用問題に強い
    "分野特化型",            # 特定の分野だけ極端に得意/苦手
    "数学得意型",            # 全体的に高得点
    "数学苦手型"             # 全体的に低得点
]

DOMAINS = ["数と式", "二次関数", "図形と計量", "データの分析", "場合の数と確率", "整数の性質"]

def get_domain(mext_hierarchy, bundle_name):
    """指導要領の階層テキストや単元名から「大項目（分野）」を抽出する"""
    text = (mext_hierarchy + bundle_name).replace(" ", "")
    for d in DOMAINS:
        if d.replace("と", "") in text or d in text:
            return d
    return "その他"

def calculate_base_probability(persona, competency, domain, student_domains):
    """ペルソナと問題の属性からベースの正答確率を算出する"""
    if persona == "知識・技能偏重型":
        return 0.85 if competency == "knowledge_skill" else 0.30
    elif persona == "思考力・判断力特化型":
        return 0.50 if competency == "knowledge_skill" else 0.80
    elif persona == "分野特化型":
        if domain == student_domains['good']:
            return 0.90
        elif domain == student_domains['bad']:
            return 0.20
        else:
            return 0.60
    elif persona == "数学得意型":
        return random.uniform(0.85, 0.95)
    elif persona == "数学苦手型":
        return random.uniform(0.15, 0.35)
    return 0.50

def generate_logs():
    print(f"🚀 GNN-KT検証用 ダミー学習ログ生成ツールを起動します...")
    
    # 1. 統合データベースの読み込み
    if not os.path.exists(DB_FILE):
        print(f"❌ {DB_FILE} が見つかりません。")
        return

    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
        
    global_nodes = db_data.get("global_concept_nodes", {})
    if not global_nodes:
        print(f"❌ {DB_FILE} 内に 'global_concept_nodes' が見つかりません。")
        return

    print(f"✅ {DB_FILE} を読み込みました (概念ノード数: {len(global_nodes)})")

    # 前提知識をたどるための「概念名 -> グローバルID」のマッピング辞書を作成
    name_to_id = {node["concept_name"]: node["global_c_id"] for node in global_nodes.values()}

    students = []
    all_logs = []
    
    # 2. 生徒プロフィールの生成
    for i in range(1, NUM_STUDENTS + 1):
        persona = random.choice(PERSONAS)
        student = {
            "student_id": f"STU_{i:03d}",
            "name": f"生徒_{i}",
            "persona": persona,
            "domains": {
                "good": random.choice(DOMAINS),
                "bad": random.choice(DOMAINS)
            } if persona == "分野特化型" else None,
            "results": {}  # { global_c_id: is_correct }
        }
        students.append(student)

    # 3. ログの生成ループ
    base_time = datetime.now() - timedelta(days=30)
    
    # 時系列順（global_timeline_index順）にソートして解かせる
    sorted_nodes = sorted(global_nodes.values(), key=lambda x: x.get("global_timeline_index", 0))

    for student in students:
        current_time = base_time
        
        for node in sorted_nodes:
            c_id = node["global_c_id"]
            domain = get_domain(node.get("mext_hierarchy", ""), node.get("bundle_name", ""))
            competency = node.get("competency", "knowledge_skill")
            prerequisites = node.get("prerequisite_concepts", [])
            
            # ペルソナに基づくベース正答率
            prob = calculate_base_probability(student['persona'], competency, domain, student['domains'])
            
            # 🔗 【GNN-KT連動】本物の前提知識ネットワークに基づく連鎖エラー処理
            for prereq in prerequisites:
                # 💡 辞書型（Ver 12.0新形式）と文字列型（旧形式）の混在を安全に処理
                if isinstance(prereq, dict):
                    p_name = prereq.get("concept_name")
                    p_type = prereq.get("dependency_type", "mandatory")
                else:
                    p_name = str(prereq)
                    p_type = "mandatory" # 単なる文字列の場合は安全のため「必須前提」として処理
                
                # DB内に存在する前提知識のIDを取得
                p_id = name_to_id.get(p_name)
                
                # もし過去にその前提知識を解いていて、かつ「不正解」だった場合
                if p_id and p_id in student['results'] and not student['results'][p_id]:
                    if p_type == 'mandatory':
                        prob *= 0.2  # 必須前提が抜けているとほぼ解けない
                    else:
                        prob *= 0.6  # 補足前提が抜けているとミスしやすい

            # 最終的な正誤判定
            is_correct = random.random() < prob
            student['results'][c_id] = is_correct
            
            # ログレコードの作成
            log_record = {
                "log_id": f"LOG_{student['student_id']}_{c_id[-8:]}", 
                "student_id": student['student_id'],
                "global_c_id": c_id,
                "concept_name": node.get("concept_name", ""),
                "branch_code": node.get("branch_code", ""),
                "mext_code": node.get("mext_code", ""),
                "competency": competency,
                "is_correct": is_correct,
                "time_spent_seconds": random.randint(15, 120) if is_correct else random.randint(30, 300),
                "timestamp": current_time.isoformat()
            }
            all_logs.append(log_record)
            
            # 次の問題を解くまでの時間を進める
            current_time += timedelta(minutes=random.randint(5, 60))

    # 4. JSONファイルへの出力
    output_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "num_students": NUM_STUDENTS,
            "total_logs": len(all_logs),
            "source_db": DB_FILE
        },
        "student_profiles": [
            {
                "student_id": s["student_id"], 
                "persona": s["persona"], 
                "domain_traits": s["domains"]
            } for s in students
        ],
        "logs": all_logs
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"🎉 ダミーログの生成が完了しました！")
    print(f"📄 出力先: {OUTPUT_FILE} (ログ件数: {len(all_logs)}件)")

if __name__ == "__main__":
    generate_logs()