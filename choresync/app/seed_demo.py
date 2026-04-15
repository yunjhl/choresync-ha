import os, random, bcrypt
from datetime import datetime, timedelta, timezone
from app.database import SessionLocal
from app.models.user import User
from app.models.family import Family, FamilyMember
from app.models.chore import ChoreTask, CompletionHistory, IntensityLevel, TaskStatus
from app.services.chore import calc_score

DEMO_TASKS = [
    ("거실 청소", "청소", 20, IntensityLevel.NORMAL),
    ("설거지", "주방", 15, IntensityLevel.LIGHT),
    ("세탁기 돌리기", "빨래", 10, IntensityLevel.LIGHT),
    ("재활용 분리수거", "쓰레기", 20, IntensityLevel.NORMAL),
    ("화장실 청소", "청소", 30, IntensityLevel.HARD),
    ("장보기", "장보기", 60, IntensityLevel.NORMAL),
    ("바닥 청소기", "청소", 25, IntensityLevel.NORMAL),
]

def _hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def run_seed():
    if not os.getenv("DEMO_SEED"):
        return
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "demo@demo.com").first():
            print("Demo data already seeded.")
            return
        pw = _hash("demo1234")
        admin = User(email="demo@demo.com", password_hash=pw, name="데모 관리자")
        m1 = User(email="member1@choresync.local", password_hash=pw, name="가족구성원1")
        m2 = User(email="member2@choresync.local", password_hash=pw, name="가족구성원2")
        db.add_all([admin, m1, m2])
        db.flush()
        family = Family(name="데모 가족", invite_code="DEMO2024", created_by=admin.id)
        db.add(family)
        db.flush()
        ma = FamilyMember(family_id=family.id, user_id=admin.id, role="Admin")
        fm1 = FamilyMember(family_id=family.id, user_id=m1.id, role="Member")
        fm2 = FamilyMember(family_id=family.id, user_id=m2.id, role="Member")
        db.add_all([ma, fm1, fm2])
        db.flush()
        members = [ma, fm1, fm2]
        now = datetime.now(timezone.utc)
        total = 0
        for day_offset in range(730):
            day = now - timedelta(days=day_offset)
            for _ in range(random.randint(2, 5)):
                tpl = random.choice(DEMO_TASKS)
                member = random.choice(members)
                score = calc_score(tpl[2], tpl[3])
                task = ChoreTask(
                    family_id=family.id,
                    name=tpl[0], category=tpl[1],
                    estimated_minutes=tpl[2], intensity=tpl[3],
                    score=score, status=TaskStatus.COMPLETED,
                    created_by=member.id, created_at=day,
                )
                db.add(task)
                db.flush()
                db.add(CompletionHistory(
                    task_id=task.id, completed_by=member.id,
                    score_earned=score, completed_at=day,
                ))
                total += 1
        db.commit()
        print(f"Demo seed: family_id={family.id}, 3 members, {total} tasks")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
