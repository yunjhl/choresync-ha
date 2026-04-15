"""가족 유형별 할일 템플릿 시드

팩 종류:
  공통        — 45개 범용 템플릿 (기본)
  1인         — 혼자 사는 경우 + 공통
  2인         — 부부/커플 + 공통
  3인_영유아  — 영아·유아(0~5세) 자녀 + 공통
  3인_초등   — 초등학생(6~12세) 자녀 + 공통
  3인_중고등  — 중·고등학생(13~18세) 자녀 + 공통
  4인         — 부모 + 자녀 2명 + 공통
"""

from sqlalchemy.orm import Session

from app.models.chore import ChoreTemplate, IntensityLevel

# ─────────────────────────────────────────
# 공통 템플릿 (45개)
# ─────────────────────────────────────────
COMMON_TEMPLATES = [
    # 청소 (10)
    {"name": "거실 청소기 돌리기",   "category": "청소", "estimated_minutes": 20, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "weekly"},
    {"name": "화장실 청소",           "category": "청소", "estimated_minutes": 30, "intensity": IntensityLevel.HARD,    "recurrence_interval": "weekly"},
    {"name": "주방 청소",             "category": "청소", "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "weekly"},
    {"name": "방 청소기 돌리기",       "category": "청소", "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "weekly"},
    {"name": "창문 닦기",             "category": "청소", "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "monthly"},
    {"name": "베란다 청소",           "category": "청소", "estimated_minutes": 20, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "monthly"},
    {"name": "먼지 털기",             "category": "청소", "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "weekly"},
    {"name": "바닥 걸레질",           "category": "청소", "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "weekly"},
    {"name": "욕실 타일 닦기",        "category": "청소", "estimated_minutes": 20, "intensity": IntensityLevel.HARD,    "recurrence_interval": "monthly"},
    {"name": "전체 대청소",           "category": "청소", "estimated_minutes": 120, "intensity": IntensityLevel.HARD,   "recurrence_interval": "monthly"},
    # 주방 (9)
    {"name": "설거지",               "category": "주방", "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "daily"},
    {"name": "식기세척기 비우기",     "category": "주방", "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "daily"},
    {"name": "냉장고 정리",           "category": "주방", "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "monthly"},
    {"name": "싱크대 닦기",           "category": "주방", "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "weekly"},
    {"name": "가스레인지 청소",       "category": "주방", "estimated_minutes": 20, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "weekly"},
    {"name": "전자레인지 청소",       "category": "주방", "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "monthly"},
    {"name": "음식물 쓰레기 버리기",  "category": "주방", "estimated_minutes": 5,  "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "daily"},
    {"name": "냉동실 정리",           "category": "주방", "estimated_minutes": 20, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "monthly"},
    {"name": "오븐 청소",             "category": "주방", "estimated_minutes": 40, "intensity": IntensityLevel.HARD,    "recurrence_interval": "monthly"},
    # 빨래 (6)
    {"name": "세탁기 돌리기",         "category": "빨래", "estimated_minutes": 5,  "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "weekly"},
    {"name": "빨래 널기",             "category": "빨래", "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "weekly"},
    {"name": "빨래 개기",             "category": "빨래", "estimated_minutes": 20, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "weekly"},
    {"name": "다림질",               "category": "빨래", "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "weekly"},
    {"name": "이불 빨기",             "category": "빨래", "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "monthly"},
    {"name": "빨래 걷기",             "category": "빨래", "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "weekly"},
    # 쓰레기 (4)
    {"name": "일반 쓰레기 버리기",    "category": "쓰레기", "estimated_minutes": 5,  "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "재활용 분리수거",       "category": "쓰레기", "estimated_minutes": 15, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "종량제 봉투 교체",      "category": "쓰레기", "estimated_minutes": 5,  "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "대형 폐기물 정리",      "category": "쓰레기", "estimated_minutes": 30, "intensity": IntensityLevel.HARD,   "recurrence_interval": None},
    # 장보기 (5)
    {"name": "마트 장보기",           "category": "장보기", "estimated_minutes": 60, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "온라인 주문",           "category": "장보기", "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "식자재 정리",           "category": "장보기", "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "편의점 심부름",         "category": "장보기", "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": None},
    {"name": "시장 장보기",           "category": "장보기", "estimated_minutes": 90, "intensity": IntensityLevel.HARD,   "recurrence_interval": "monthly"},
    # 돌봄 (5)
    {"name": "아이 목욕시키기",       "category": "돌봄", "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "daily"},
    {"name": "반려동물 밥 주기",      "category": "돌봄", "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "daily"},
    {"name": "반려동물 산책",         "category": "돌봄", "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "daily"},
    {"name": "화초 물 주기",          "category": "돌봄", "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "weekly"},
    {"name": "아이 숙제 도와주기",    "category": "돌봄", "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "daily"},
    # 정리 (6)
    {"name": "옷장 정리",             "category": "정리", "estimated_minutes": 40, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "monthly"},
    {"name": "신발장 정리",           "category": "정리", "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "monthly"},
    {"name": "책상 정리",             "category": "정리", "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "weekly"},
    {"name": "창고 정리",             "category": "정리", "estimated_minutes": 60, "intensity": IntensityLevel.HARD,    "recurrence_interval": "monthly"},
    {"name": "드레스룸 정리",         "category": "정리", "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL,  "recurrence_interval": "monthly"},
    {"name": "서랍 정리",             "category": "정리", "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,   "recurrence_interval": "monthly"},
]

# ─────────────────────────────────────────
# 1인 가족 추가 템플릿 (혼자 사는 경우)
# 특징: 짧은 시간, 소규모, 혼자 끝낼 수 있는 분량
# ─────────────────────────────────────────
PACK_1인 = [
    {"name": "[1인] 욕실 빠른 청소",         "category": "청소",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[1인] 방+거실 청소기",         "category": "청소",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[1인] 바닥 닦기",              "category": "청소",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[1인] 싱크대+가스레인지 닦기", "category": "주방",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[1인] 빠른 설거지",            "category": "주방",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[1인] 냉장고 유통기한 점검",   "category": "주방",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[1인] 세탁+건조+개기 한번에",  "category": "빨래",  "estimated_minutes": 35, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[1인] 쓰레기 분리배출",        "category": "쓰레기","estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[1인] 온라인 장보기",          "category": "장보기","estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[1인] 간편 장보기",            "category": "장보기","estimated_minutes": 30, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[1인] 책상·침대 주변 정리",    "category": "정리",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[1인] 월간 집 전체 점검",      "category": "청소",  "estimated_minutes": 60, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "monthly"},
    {"name": "[1인] 가계부 작성",            "category": "관리",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "monthly"},
    {"name": "[1인] 배달음식 쓰레기 정리",   "category": "쓰레기","estimated_minutes": 5,  "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
]

# ─────────────────────────────────────────
# 2인 가족 추가 템플릿 (부부/커플)
# 특징: 역할 분담, 2인 기준 빨래·요리 분량
# ─────────────────────────────────────────
PACK_2인 = [
    {"name": "[2인] 거실+침실 청소기",       "category": "청소",  "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[2인] 화장실 청소 (담당자)",   "category": "청소",  "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[2인] 침실 이불 정리",         "category": "청소",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[2인] 함께 저녁 요리",         "category": "주방",  "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "daily"},
    {"name": "[2인] 냉장고 유통기한 점검",   "category": "주방",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[2인] 빨래 세탁+널기",         "category": "빨래",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[2인] 이불 세탁",              "category": "빨래",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "monthly"},
    {"name": "[2인] 주간 장보기",            "category": "장보기","estimated_minutes": 50, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[2인] 장보기 목록 작성",       "category": "장보기","estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[2인] 재활용 분리수거",        "category": "쓰레기","estimated_minutes": 15, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[2인] 화초·식물 관리",         "category": "돌봄",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[2인] 가계부 작성",            "category": "관리",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "monthly"},
    {"name": "[2인] 청구서·공과금 확인",     "category": "관리",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "monthly"},
    {"name": "[2인] 계절 옷 교체 정리",      "category": "정리",  "estimated_minutes": 50, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "monthly"},
    {"name": "[2인] 주말 함께 대청소",       "category": "청소",  "estimated_minutes": 80, "intensity": IntensityLevel.HARD,   "recurrence_interval": "monthly"},
]

# ─────────────────────────────────────────
# 3인 가족 — 영유아(0~5세) 추가 템플릿
# 특징: 아이 돌봄 중심, 위생·소독 강화
# ─────────────────────────────────────────
PACK_3인_영유아 = [
    {"name": "[영유아] 아이 목욕 준비·진행",     "category": "돌봄",  "estimated_minutes": 35, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "daily"},
    {"name": "[영유아] 이유식·분유 준비",         "category": "돌봄",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[영유아] 젖병·이유식 용기 소독",   "category": "돌봄",  "estimated_minutes": 10, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "daily"},
    {"name": "[영유아] 아이 잠자리 준비",         "category": "돌봄",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[영유아] 장난감 정리·소독",         "category": "돌봄",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[영유아] 기저귀 쓰레기 버리기",     "category": "쓰레기","estimated_minutes": 5,  "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[영유아] 아이 옷·턱받이 세탁",     "category": "빨래",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[영유아] 아기 침구 세탁",           "category": "빨래",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[영유아] 바닥 소독 청소",           "category": "청소",  "estimated_minutes": 30, "intensity": IntensityLevel.HARD,   "recurrence_interval": "weekly"},
    {"name": "[영유아] 아기방 청소기",            "category": "청소",  "estimated_minutes": 20, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[영유아] 욕조·욕실 소독",           "category": "청소",  "estimated_minutes": 20, "intensity": IntensityLevel.HARD,   "recurrence_interval": "weekly"},
    {"name": "[영유아] 유아 용품 정리",           "category": "정리",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[영유아] 유모차·아기띠 청소",       "category": "청소",  "estimated_minutes": 20, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "monthly"},
    {"name": "[영유아] 예방접종·병원 일정 확인",  "category": "관리",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "monthly"},
    {"name": "[영유아] 아이 외출 가방 준비",      "category": "돌봄",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": None},
    {"name": "[영유아] 분유·이유식 재료 장보기",  "category": "장보기","estimated_minutes": 30, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
]

# ─────────────────────────────────────────
# 3인 가족 — 초등학생(6~12세) 추가 템플릿
# 특징: 아이가 일부 참여 가능, 학교 일정 관리
# ─────────────────────────────────────────
PACK_3인_초등 = [
    {"name": "[초등] 아이 방 청소 지도",          "category": "청소",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[초등] 식탁 닦기 (아이 담당)",      "category": "주방",  "estimated_minutes": 5,  "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[초등] 빨래 개기 함께 하기",        "category": "빨래",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[초등] 신발장 정리 (아이 담당)",    "category": "정리",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[초등] 쓰레기통 비우기 (아이 담당)","category": "쓰레기","estimated_minutes": 5,  "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[초등] 화분 물 주기 (아이 담당)",   "category": "돌봄",  "estimated_minutes": 5,  "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[초등] 아이 학교 준비물 챙기기",    "category": "돌봄",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[초등] 저녁 식사 준비",             "category": "주방",  "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "daily"},
    {"name": "[초등] 청소기 돌리기 (전체)",       "category": "청소",  "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[초등] 화장실 청소",               "category": "청소",  "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[초등] 주간 장보기",               "category": "장보기","estimated_minutes": 50, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[초등] 주말 가족 대청소",           "category": "청소",  "estimated_minutes": 90, "intensity": IntensityLevel.HARD,   "recurrence_interval": "monthly"},
    {"name": "[초등] 계절 옷 정리",              "category": "정리",  "estimated_minutes": 45, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "monthly"},
    {"name": "[초등] 학교 서류·공지 처리",       "category": "관리",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[초등] 학원 이동 준비",            "category": "돌봄",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
]

# ─────────────────────────────────────────
# 3인 가족 — 중·고등학생(13~18세) 추가 템플릿
# 특징: 청소년이 본격 분담, 자기 몫 담당
# ─────────────────────────────────────────
PACK_3인_중고등 = [
    {"name": "[중고등] 화장실 청소 (청소년 담당)",  "category": "청소",  "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[중고등] 청소기 돌리기 (청소년 담당)","category": "청소",  "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[중고등] 설거지 (청소년 담당)",       "category": "주방",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[중고등] 빨래 세탁+개기 (청소년)",   "category": "빨래",  "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[중고등] 재활용 분리수거 (청소년)",   "category": "쓰레기","estimated_minutes": 15, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[중고등] 식후 식탁 정리 (청소년)",   "category": "주방",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[중고등] 자기 방 청소 (청소년)",     "category": "청소",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[중고등] 마트 심부름 (청소년)",      "category": "장보기","estimated_minutes": 30, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": None},
    {"name": "[중고등] 저녁 식사 준비 (부모)",     "category": "주방",  "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "daily"},
    {"name": "[중고등] 주간 장보기 (부모)",        "category": "장보기","estimated_minutes": 50, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[중고등] 베란다·창문 청소 (부모)",   "category": "청소",  "estimated_minutes": 35, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "monthly"},
    {"name": "[중고등] 냉장고 정리 (부모)",        "category": "주방",  "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "monthly"},
    {"name": "[중고등] 집 전체 대청소 (함께)",     "category": "청소",  "estimated_minutes": 90, "intensity": IntensityLevel.HARD,   "recurrence_interval": "monthly"},
    {"name": "[중고등] 집 관리·수리 점검 (부모)",  "category": "관리",  "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "monthly"},
    {"name": "[중고등] 가계부 작성 (부모)",        "category": "관리",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "monthly"},
]

# ─────────────────────────────────────────
# 4인 가족 추가 템플릿 (부모 + 자녀 2명)
# 특징: 규모 큰 청소·빨래, 아이 2명 관리, 많은 요리 분량
# ─────────────────────────────────────────
PACK_4인 = [
    {"name": "[4인] 전체 청소기 (2층 또는 넓은 집)","category": "청소",  "estimated_minutes": 35, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[4인] 욕실 2개 청소",               "category": "청소",  "estimated_minutes": 40, "intensity": IntensityLevel.HARD,   "recurrence_interval": "weekly"},
    {"name": "[4인] 거실+주방 바닥 닦기",          "category": "청소",  "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[4인] 4인 식사 준비",               "category": "주방",  "estimated_minutes": 35, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "daily"},
    {"name": "[4인] 4인 설거지",                  "category": "주방",  "estimated_minutes": 20, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "daily"},
    {"name": "[4인] 냉장고 정리 (대가족)",         "category": "주방",  "estimated_minutes": 30, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "monthly"},
    {"name": "[4인] 대량 빨래 세탁",              "category": "빨래",  "estimated_minutes": 10, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[4인] 빨래 개기 (4인 분량)",        "category": "빨래",  "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[4인] 이불 세탁 (4인 분량)",        "category": "빨래",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "monthly"},
    {"name": "[4인] 주간 대형 장보기",            "category": "장보기","estimated_minutes": 70, "intensity": IntensityLevel.HARD,   "recurrence_interval": "weekly"},
    {"name": "[4인] 아이 1 방 청소 지도",         "category": "청소",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[4인] 아이 2 방 청소 지도",         "category": "청소",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[4인] 아이들 학교 준비물 챙기기",    "category": "돌봄",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "daily"},
    {"name": "[4인] 도시락 준비 (2명분)",         "category": "주방",  "estimated_minutes": 25, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "daily"},
    {"name": "[4인] 재활용 분리수거",             "category": "쓰레기","estimated_minutes": 20, "intensity": IntensityLevel.NORMAL, "recurrence_interval": "weekly"},
    {"name": "[4인] 집 전체 대청소 (가족 모두)",  "category": "청소",  "estimated_minutes": 120, "intensity": IntensityLevel.HARD,  "recurrence_interval": "monthly"},
    {"name": "[4인] 가계부·청구서 관리",          "category": "관리",  "estimated_minutes": 20, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "monthly"},
    {"name": "[4인] 학교 서류·공지 처리",         "category": "관리",  "estimated_minutes": 15, "intensity": IntensityLevel.LIGHT,  "recurrence_interval": "weekly"},
    {"name": "[4인] 계절 의류 교체 정리",         "category": "정리",  "estimated_minutes": 60, "intensity": IntensityLevel.HARD,   "recurrence_interval": "monthly"},
]

# ─────────────────────────────────────────
# 팩 매핑
# ─────────────────────────────────────────
FAMILY_PACKS: dict[str, list[dict]] = {
    "공통":      COMMON_TEMPLATES,
    "1인":       COMMON_TEMPLATES + PACK_1인,
    "2인":       COMMON_TEMPLATES + PACK_2인,
    "3인_영유아": COMMON_TEMPLATES + PACK_3인_영유아,
    "3인_초등":  COMMON_TEMPLATES + PACK_3인_초등,
    "3인_중고등": COMMON_TEMPLATES + PACK_3인_중고등,
    "4인":       COMMON_TEMPLATES + PACK_4인,
}

VALID_PACKS = list(FAMILY_PACKS.keys())

# 이전 호환성을 위한 별칭
DEFAULT_TEMPLATES = COMMON_TEMPLATES


def seed_templates(family_id: int, member_id: int, db: Session, pack: str = "공통") -> int:
    """가족에게 템플릿 팩을 시드한다. 이미 있으면 건너뜀."""
    existing = (
        db.query(ChoreTemplate)
        .filter(ChoreTemplate.family_id == family_id)
        .count()
    )
    if existing > 0:
        return 0

    templates_data = FAMILY_PACKS.get(pack, COMMON_TEMPLATES)
    templates = [
        ChoreTemplate(
            family_id=family_id,
            created_by=member_id,
            name=t["name"],
            category=t["category"],
            estimated_minutes=t["estimated_minutes"],
            intensity=t["intensity"],
            recurrence_interval=t.get("recurrence_interval"),
        )
        for t in templates_data
    ]
    db.add_all(templates)
    db.commit()
    return len(templates)


def reseed_templates(family_id: int, member_id: int, db: Session, pack: str) -> int:
    """기존 템플릿을 모두 삭제하고 새 팩으로 재시드한다."""
    db.query(ChoreTemplate).filter(ChoreTemplate.family_id == family_id).delete()
    db.commit()
    # 이미 있는지 체크를 건너뛰기 위해 직접 삽입
    templates_data = FAMILY_PACKS.get(pack, COMMON_TEMPLATES)
    templates = [
        ChoreTemplate(
            family_id=family_id,
            created_by=member_id,
            name=t["name"],
            category=t["category"],
            estimated_minutes=t["estimated_minutes"],
            intensity=t["intensity"],
            recurrence_interval=t.get("recurrence_interval"),
        )
        for t in templates_data
    ]
    db.add_all(templates)
    db.commit()
    return len(templates)
