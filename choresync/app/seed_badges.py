"""배지 정의 20종 시드 데이터"""
import json
from app.database import SessionLocal
from app.models.badge import BadgeDefinition

BADGES = [
    {"code":"first_complete","name":"첫 걸음","icon":"👣","badge_type":"first_complete","tier":"bronze","points_bonus":5,"description":"첫 번째 할일을 완료했습니다","condition_json":{"type":"first_complete"}},
    {"code":"streak_3","name":"3일 연속","icon":"🔥","badge_type":"streak","tier":"bronze","points_bonus":10,"description":"3일 연속으로 할일을 완료했습니다","condition_json":{"type":"streak","days":3}},
    {"code":"streak_7","name":"일주일 전사","icon":"⚔️","badge_type":"streak","tier":"silver","points_bonus":25,"description":"7일 연속으로 할일을 완료했습니다","condition_json":{"type":"streak","days":7}},
    {"code":"streak_14","name":"2주 챔피언","icon":"🏆","badge_type":"streak","tier":"gold","points_bonus":50,"description":"14일 연속으로 할일을 완료했습니다","condition_json":{"type":"streak","days":14}},
    {"code":"streak_30","name":"한 달 마스터","icon":"👑","badge_type":"streak","tier":"platinum","points_bonus":100,"description":"30일 연속으로 할일을 완료했습니다","condition_json":{"type":"streak","days":30}},
    {"code":"score_50","name":"50점 달성","icon":"⭐","badge_type":"score_total","tier":"bronze","points_bonus":5,"description":"누적 점수 50점 달성","condition_json":{"type":"score_total","threshold":50}},
    {"code":"score_100","name":"100점 달성","icon":"💯","badge_type":"score_total","tier":"bronze","points_bonus":10,"description":"누적 점수 100점 달성","condition_json":{"type":"score_total","threshold":100}},
    {"code":"score_300","name":"300점 달성","icon":"🌟","badge_type":"score_total","tier":"silver","points_bonus":20,"description":"누적 점수 300점 달성","condition_json":{"type":"score_total","threshold":300}},
    {"code":"score_500","name":"500점 달성","icon":"💫","badge_type":"score_total","tier":"gold","points_bonus":50,"description":"누적 점수 500점 달성","condition_json":{"type":"score_total","threshold":500}},
    {"code":"score_1000","name":"포인트 왕","icon":"💎","badge_type":"score_total","tier":"platinum","points_bonus":100,"description":"누적 점수 1000점 달성","condition_json":{"type":"score_total","threshold":1000}},
    {"code":"task_10","name":"10개 완료","icon":"✅","badge_type":"task_count","tier":"bronze","points_bonus":5,"description":"할일 10개를 완료했습니다","condition_json":{"type":"task_count","threshold":10}},
    {"code":"task_30","name":"30개 완료","icon":"📋","badge_type":"task_count","tier":"silver","points_bonus":15,"description":"할일 30개를 완료했습니다","condition_json":{"type":"task_count","threshold":30}},
    {"code":"task_50","name":"50개 완료","icon":"🎯","badge_type":"task_count","tier":"silver","points_bonus":25,"description":"할일 50개를 완료했습니다","condition_json":{"type":"task_count","threshold":50}},
    {"code":"task_100","name":"100개 완료","icon":"🏅","badge_type":"task_count","tier":"gold","points_bonus":50,"description":"할일 100개를 완료했습니다","condition_json":{"type":"task_count","threshold":100}},
    {"code":"task_200","name":"200개 완료","icon":"🥇","badge_type":"task_count","tier":"platinum","points_bonus":100,"description":"할일 200개를 완료했습니다","condition_json":{"type":"task_count","threshold":200}},
    {"code":"quest_first","name":"퀘스트 도전자","icon":"⚡","badge_type":"quest_count","tier":"bronze","points_bonus":10,"description":"첫 퀘스트를 완료했습니다","condition_json":{"type":"quest_count","threshold":1}},
    {"code":"quest_5","name":"퀘스트 영웅","icon":"🦸","badge_type":"quest_count","tier":"silver","points_bonus":30,"description":"퀘스트 5개를 완료했습니다","condition_json":{"type":"quest_count","threshold":5}},
    {"code":"quest_10","name":"퀘스트 마스터","icon":"🧙","badge_type":"quest_count","tier":"gold","points_bonus":60,"description":"퀘스트 10개를 완료했습니다","condition_json":{"type":"quest_count","threshold":10}},
    {"code":"streak_2","name":"이틀 연속","icon":"✌️","badge_type":"streak","tier":"bronze","points_bonus":3,"description":"2일 연속으로 할일을 완료했습니다","condition_json":{"type":"streak","days":2}},
    {"code":"score_1","name":"시작이 반","icon":"🌱","badge_type":"score_total","tier":"bronze","points_bonus":1,"description":"첫 점수를 획득했습니다","condition_json":{"type":"score_total","threshold":1}},
]


def seed_badges():
    db = SessionLocal()
    try:
        for b in BADGES:
            existing = db.query(BadgeDefinition).filter(BadgeDefinition.code == b["code"]).first()
            if existing:
                continue
            defn = BadgeDefinition(
                code=b["code"], name=b["name"], icon=b["icon"],
                badge_type=b["badge_type"], tier=b["tier"],
                points_bonus=b["points_bonus"], description=b["description"],
                condition_json=json.dumps(b["condition_json"]),
                is_active=True,
            )
            db.add(defn)
        db.commit()
        print(f"[ChoreSync] Seeded {len(BADGES)} badge definitions")
    finally:
        db.close()


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    seed_badges()
