"""마켓플레이스 시드 데이터 (연령별 가족 구성 포함, 200개+)"""
from sqlalchemy.orm import Session
from app.models.marketplace import MarketplaceTemplate


TEMPLATES = [
    # ============================================================
    # 전체 (35개) — 모든 가족 공통, 귀가/외출 트리거 포함
    # ============================================================
    {"name": "주방 쓰레기 버리기", "category": "청소", "estimated_minutes": 5, "intensity": "Light", "family_size": "전체", "recurrence_interval": "daily"},
    {"name": "세면대 닦기", "category": "청소", "estimated_minutes": 10, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "바닥 쓸기", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "전체", "recurrence_interval": "daily"},
    {"name": "유리창 닦기", "category": "청소", "estimated_minutes": 30, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "monthly"},
    {"name": "냉장고 내부 청소", "category": "청소", "estimated_minutes": 30, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "monthly"},
    {"name": "전자레인지 청소", "category": "청소", "estimated_minutes": 10, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "가스레인지 청소", "category": "요리", "estimated_minutes": 15, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "냉장고 정리", "category": "요리", "estimated_minutes": 20, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "싱크대 청소", "category": "청소", "estimated_minutes": 15, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "욕실 청소", "category": "청소", "estimated_minutes": 30, "intensity": "Hard", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "변기 청소", "category": "청소", "estimated_minutes": 15, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "분리수거", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "쓰레기 분류", "category": "청소", "estimated_minutes": 10, "intensity": "Light", "family_size": "전체", "recurrence_interval": "daily"},
    {"name": "빨래 돌리기", "category": "세탁", "estimated_minutes": 10, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "빨래 건조", "category": "세탁", "estimated_minutes": 15, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "빨래 개기", "category": "세탁", "estimated_minutes": 20, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "빨래 넣기 (서랍)", "category": "세탁", "estimated_minutes": 10, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "장보기", "category": "쇼핑", "estimated_minutes": 60, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "온라인 장보기 주문", "category": "쇼핑", "estimated_minutes": 20, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "청소기 돌리기", "category": "청소", "estimated_minutes": 30, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "밀걸레질", "category": "청소", "estimated_minutes": 30, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "귀가 후 현관 정리", "category": "정리정돈", "estimated_minutes": 5, "intensity": "Light", "family_size": "전체", "trigger_context": "on_arrival", "description": "귀가하면 신발을 정리하고 가방을 제자리에 두세요."},
    {"name": "외출 전 집 점검", "category": "정리정돈", "estimated_minutes": 5, "intensity": "Light", "family_size": "전체", "trigger_context": "on_departure", "description": "가스 잠금, 창문 닫기, 전등 끄기를 확인하세요."},
    {"name": "귀가 후 손 씻기 준비", "category": "위생", "estimated_minutes": 2, "intensity": "Light", "family_size": "전체", "trigger_context": "on_arrival"},
    {"name": "외출 전 식재료 확인", "category": "요리", "estimated_minutes": 5, "intensity": "Light", "family_size": "전체", "trigger_context": "on_departure"},
    {"name": "설거지", "category": "요리", "estimated_minutes": 20, "intensity": "Light", "family_size": "전체", "recurrence_interval": "daily"},
    {"name": "주방 정리", "category": "요리", "estimated_minutes": 10, "intensity": "Light", "family_size": "전체", "recurrence_interval": "daily"},
    {"name": "화장실 수건 교체", "category": "세탁", "estimated_minutes": 5, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "침구 교체", "category": "세탁", "estimated_minutes": 30, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "biweekly"},
    {"name": "소독 (도어락, 리모컨)", "category": "위생", "estimated_minutes": 10, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "화분 물주기", "category": "기타", "estimated_minutes": 10, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "신발장 정리", "category": "정리정돈", "estimated_minutes": 15, "intensity": "Light", "family_size": "전체", "recurrence_interval": "monthly"},
    {"name": "책상/테이블 정리", "category": "정리정돈", "estimated_minutes": 10, "intensity": "Light", "family_size": "전체", "recurrence_interval": "weekly"},
    {"name": "에어컨 필터 청소", "category": "관리", "estimated_minutes": 20, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "monthly"},
    {"name": "배수구 청소", "category": "청소", "estimated_minutes": 15, "intensity": "Normal", "family_size": "전체", "recurrence_interval": "monthly"},

    # ============================================================
    # 1인 (25개) — 혼자 처리, 자기관리 중심
    # ============================================================
    {"name": "원룸 청소기", "category": "청소", "estimated_minutes": 20, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "원룸 밀대질", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "혼자 설거지", "category": "요리", "estimated_minutes": 10, "intensity": "Light", "family_size": "1인", "recurrence_interval": "daily"},
    {"name": "주 1회 밀프렙", "category": "요리", "estimated_minutes": 60, "intensity": "Hard", "family_size": "1인", "recurrence_interval": "weekly", "description": "한 주 분량 반찬/도시락을 미리 준비합니다."},
    {"name": "개인 빨래 (혼자)", "category": "세탁", "estimated_minutes": 10, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "냉장고 미니 정리", "category": "요리", "estimated_minutes": 10, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "편의점/마트 간단 장보기", "category": "쇼핑", "estimated_minutes": 30, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "책상 정리", "category": "정리정돈", "estimated_minutes": 10, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "침대 시트 교체", "category": "세탁", "estimated_minutes": 15, "intensity": "Light", "family_size": "1인", "recurrence_interval": "biweekly"},
    {"name": "욕실 청소 (1인)", "category": "청소", "estimated_minutes": 20, "intensity": "Normal", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "쓰레기 버리기 (1인)", "category": "청소", "estimated_minutes": 5, "intensity": "Light", "family_size": "1인", "recurrence_interval": "daily"},
    {"name": "분리수거 (1인)", "category": "청소", "estimated_minutes": 10, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "냉장고 유통기한 점검", "category": "요리", "estimated_minutes": 10, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "개인 건강 용품 보충", "category": "쇼핑", "estimated_minutes": 15, "intensity": "Light", "family_size": "1인", "recurrence_interval": "monthly"},
    {"name": "운동화 세탁", "category": "세탁", "estimated_minutes": 20, "intensity": "Normal", "family_size": "1인", "recurrence_interval": "monthly"},
    {"name": "전기세/공과금 확인", "category": "관리", "estimated_minutes": 10, "intensity": "Light", "family_size": "1인", "recurrence_interval": "monthly"},
    {"name": "방 환기", "category": "위생", "estimated_minutes": 5, "intensity": "Light", "family_size": "1인", "recurrence_interval": "daily"},
    {"name": "주방 쓰레기통 교체", "category": "청소", "estimated_minutes": 3, "intensity": "Light", "family_size": "1인", "recurrence_interval": "daily"},
    {"name": "현관 신발 정리 (1인)", "category": "정리정돈", "estimated_minutes": 5, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "옷장 계절 정리", "category": "정리정돈", "estimated_minutes": 60, "intensity": "Normal", "family_size": "1인", "recurrence_interval": "semiannual"},
    {"name": "세면대 청소 (1인)", "category": "청소", "estimated_minutes": 10, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "배달 음식 쓰레기 정리", "category": "청소", "estimated_minutes": 5, "intensity": "Light", "family_size": "1인", "recurrence_interval": "daily"},
    {"name": "가전 먼지 닦기", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},
    {"name": "창문틀 청소", "category": "청소", "estimated_minutes": 20, "intensity": "Normal", "family_size": "1인", "recurrence_interval": "monthly"},
    {"name": "홈 트레이닝 공간 정리", "category": "정리정돈", "estimated_minutes": 10, "intensity": "Light", "family_size": "1인", "recurrence_interval": "weekly"},

    # ============================================================
    # 2인 (25개) — 부부 분담, 교대 패턴
    # ============================================================
    {"name": "아침 식사 준비", "category": "요리", "estimated_minutes": 20, "intensity": "Light", "family_size": "2인", "recurrence_interval": "daily"},
    {"name": "저녁 식사 준비", "category": "요리", "estimated_minutes": 40, "intensity": "Normal", "family_size": "2인", "recurrence_interval": "daily"},
    {"name": "식후 설거지 (교대)", "category": "요리", "estimated_minutes": 15, "intensity": "Light", "family_size": "2인", "recurrence_interval": "daily", "description": "오늘의 당번이 설거지합니다."},
    {"name": "주방 바닥 청소", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "안방 청소기", "category": "청소", "estimated_minutes": 20, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "거실 청소기", "category": "청소", "estimated_minutes": 20, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "부부 침구 교체", "category": "세탁", "estimated_minutes": 30, "intensity": "Normal", "family_size": "2인", "recurrence_interval": "biweekly"},
    {"name": "세탁기 돌리기 (부부)", "category": "세탁", "estimated_minutes": 10, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "빨래 개기 (부부)", "category": "세탁", "estimated_minutes": 20, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "주간 장보기 (부부)", "category": "쇼핑", "estimated_minutes": 60, "intensity": "Normal", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "재활용 분리수거 (부부)", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "욕실 청소 (부부 교대)", "category": "청소", "estimated_minutes": 30, "intensity": "Hard", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "주방 청소 (부부)", "category": "청소", "estimated_minutes": 20, "intensity": "Normal", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "베란다 청소", "category": "청소", "estimated_minutes": 30, "intensity": "Normal", "family_size": "2인", "recurrence_interval": "monthly"},
    {"name": "가전 점검", "category": "관리", "estimated_minutes": 20, "intensity": "Light", "family_size": "2인", "recurrence_interval": "monthly"},
    {"name": "집 전체 청소 (주말)", "category": "청소", "estimated_minutes": 90, "intensity": "Hard", "family_size": "2인", "recurrence_interval": "weekly", "description": "주말에 함께 집을 청소합니다."},
    {"name": "약품/세제 재고 점검", "category": "쇼핑", "estimated_minutes": 10, "intensity": "Light", "family_size": "2인", "recurrence_interval": "monthly"},
    {"name": "냉장고 대청소 (부부)", "category": "청소", "estimated_minutes": 40, "intensity": "Normal", "family_size": "2인", "recurrence_interval": "monthly"},
    {"name": "옷장 정리 (공용)", "category": "정리정돈", "estimated_minutes": 45, "intensity": "Normal", "family_size": "2인", "recurrence_interval": "semiannual"},
    {"name": "조명 점검 및 교체", "category": "관리", "estimated_minutes": 15, "intensity": "Light", "family_size": "2인", "recurrence_interval": "monthly"},
    {"name": "환기 및 공기청정기 필터 교체", "category": "위생", "estimated_minutes": 15, "intensity": "Light", "family_size": "2인", "recurrence_interval": "monthly"},
    {"name": "안방 정리정돈", "category": "정리정돈", "estimated_minutes": 15, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "현관 정리 (부부)", "category": "정리정돈", "estimated_minutes": 5, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "화분 물주기 (부부)", "category": "기타", "estimated_minutes": 10, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},
    {"name": "주말 대청소 계획 세우기", "category": "정리정돈", "estimated_minutes": 15, "intensity": "Light", "family_size": "2인", "recurrence_interval": "weekly"},

    # ============================================================
    # 3인_영유아 (25개) — 아이 0~5세, 부모 전담, adult_only
    # ============================================================
    {"name": "기저귀 갈기", "category": "육아/교육", "estimated_minutes": 5, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "아이 목욕", "category": "육아/교육", "estimated_minutes": 20, "intensity": "Normal", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "어린이집 가방 준비", "category": "육아/교육", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "어린이집 등하원", "category": "육아/교육", "estimated_minutes": 30, "intensity": "Normal", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "아이 식사 준비", "category": "요리", "estimated_minutes": 20, "intensity": "Normal", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "이유식 준비", "category": "요리", "estimated_minutes": 30, "intensity": "Normal", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "분유/이유식 재고 점검", "category": "쇼핑", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "기저귀/물티슈 재고 보충", "category": "쇼핑", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 빨래 (영유아)", "category": "세탁", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "장난감 소독 및 정리", "category": "위생", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 방 청소", "category": "청소", "estimated_minutes": 20, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 침구 교체 (영유아)", "category": "세탁", "estimated_minutes": 20, "intensity": "Normal", "family_size": "3인_영유아", "recurrence_interval": "biweekly", "assignee_type": "adult_only"},
    {"name": "주방 이유식 도구 세척", "category": "요리", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "아이 약품/건강용품 점검", "category": "위생", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "성장일지 기록", "category": "육아/교육", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "소아과/예방접종 일정 관리", "category": "육아/교육", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "아이 수면 루틴 관리", "category": "육아/교육", "estimated_minutes": 30, "intensity": "Normal", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "유아용 세제 구비", "category": "쇼핑", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "바닥 청소 (기어다니는 아이 위해)", "category": "청소", "estimated_minutes": 20, "intensity": "Normal", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only", "description": "아이가 기어다니는 공간을 매일 닦아줍니다."},
    {"name": "어린이집 준비물 챙기기", "category": "육아/교육", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "영아 전용 욕조 청소", "category": "청소", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 카시트 점검", "category": "관리", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "유모차 청소", "category": "관리", "estimated_minutes": 20, "intensity": "Normal", "family_size": "3인_영유아", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "아이 그림책 읽어주기", "category": "육아/교육", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "아이 장난감 배터리 교체", "category": "관리", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_영유아", "recurrence_interval": "monthly", "assignee_type": "adult_only"},

    # ============================================================
    # 3인_초등 (25개) — 아이 6~12세, child_assist 포함
    # ============================================================
    {"name": "식탁 닦기", "category": "청소", "estimated_minutes": 5, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 6, "age_max": 12, "description": "식사 후 식탁을 행주로 닦아요."},
    {"name": "장난감/교구 정리", "category": "정리정돈", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 6, "age_max": 12},
    {"name": "신발 정리 (현관)", "category": "정리정돈", "estimated_minutes": 5, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 6, "age_max": 12},
    {"name": "분리수거 보조", "category": "청소", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "child_assist", "age_min": 8, "age_max": 12, "description": "부모와 함께 재활용품을 분류합니다."},
    {"name": "아이 방 청소 (초등)", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "child_assist", "age_min": 8, "age_max": 12},
    {"name": "애완동물 밥 주기", "category": "기타", "estimated_minutes": 5, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 7, "age_max": 12},
    {"name": "채소 씻기 보조", "category": "요리", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 8, "age_max": 12},
    {"name": "세탁물 건조대 정리 보조", "category": "세탁", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "child_assist", "age_min": 9, "age_max": 12},
    {"name": "책가방 정리 정돈", "category": "정리정돈", "estimated_minutes": 5, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 7, "age_max": 12},
    {"name": "스스로 방청소", "category": "청소", "estimated_minutes": 20, "intensity": "Normal", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "child_assist", "age_min": 9, "age_max": 12},
    {"name": "초등 아이 라면/간식 정리", "category": "요리", "estimated_minutes": 5, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 9, "age_max": 12},
    {"name": "학교 준비물 챙기기 (스스로)", "category": "육아/교육", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 8, "age_max": 12},
    {"name": "공용 컵/그릇 제자리 두기", "category": "정리정돈", "estimated_minutes": 5, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 6, "age_max": 12},
    {"name": "간단한 심부름 (편의점)", "category": "쇼핑", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "child_assist", "age_min": 10, "age_max": 12},
    # 부모 전담
    {"name": "초등 학원 도시락 준비", "category": "요리", "estimated_minutes": 20, "intensity": "Normal", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "아이 빨래 세탁", "category": "세탁", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 간식 및 영양 관리", "category": "육아/교육", "estimated_minutes": 20, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "학교/학원 스케줄 관리", "category": "육아/교육", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 숙제 봐주기", "category": "육아/교육", "estimated_minutes": 30, "intensity": "Normal", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "가족 욕실 청소 (초등)", "category": "청소", "estimated_minutes": 30, "intensity": "Hard", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "저녁 식사 준비 (초등 가족)", "category": "요리", "estimated_minutes": 40, "intensity": "Normal", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "주간 장보기 (초등 가족)", "category": "쇼핑", "estimated_minutes": 60, "intensity": "Normal", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "가족 청소기 (주방/거실)", "category": "청소", "estimated_minutes": 30, "intensity": "Normal", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 독서 습관 지원", "category": "육아/교육", "estimated_minutes": 20, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "주말 가족 외출 준비", "category": "정리정돈", "estimated_minutes": 20, "intensity": "Light", "family_size": "3인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},

    # ============================================================
    # 3인_중고등 (25개) — 아이 13~18세, child_independent 포함
    # ============================================================
    {"name": "저녁 설거지 당번", "category": "요리", "estimated_minutes": 20, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "daily", "assignee_type": "child_independent", "age_min": 13, "description": "저녁 식사 후 설거지를 맡아서 합니다."},
    {"name": "자기 방 청소기", "category": "청소", "estimated_minutes": 20, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 13},
    {"name": "빨래 넣기 (세탁기)", "category": "세탁", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 13},
    {"name": "자기 빨래 개기", "category": "세탁", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 14},
    {"name": "분리수거 완전 독립", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 13},
    {"name": "요리 보조 (부모 지도)", "category": "요리", "estimated_minutes": 30, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 15},
    {"name": "간단한 요리 (라면/계란)", "category": "요리", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "daily", "assignee_type": "child_independent", "age_min": 13},
    {"name": "거실 청소기", "category": "청소", "estimated_minutes": 20, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 13},
    {"name": "쓰레기 버리기 (독립)", "category": "청소", "estimated_minutes": 5, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "daily", "assignee_type": "child_independent", "age_min": 13},
    {"name": "빨래 건조대 걸기", "category": "세탁", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 14},
    {"name": "마트 심부름", "category": "쇼핑", "estimated_minutes": 30, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 15, "description": "부모가 목록을 주면 혼자 마트에서 장봐옵니다."},
    {"name": "자기 세면대 청소", "category": "청소", "estimated_minutes": 10, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 13},
    {"name": "욕실 청소 (독립)", "category": "청소", "estimated_minutes": 25, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 16},
    {"name": "이불 정리", "category": "정리정돈", "estimated_minutes": 5, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "daily", "assignee_type": "child_independent", "age_min": 13},
    {"name": "자기 빨래 독립 (세탁~개기)", "category": "세탁", "estimated_minutes": 40, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 16},
    # 부모 전담
    {"name": "주간 장보기 (중고등 가족)", "category": "쇼핑", "estimated_minutes": 60, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "저녁 식사 준비 (중고등 가족)", "category": "요리", "estimated_minutes": 40, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "청구서/공과금 관리", "category": "관리", "estimated_minutes": 15, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "냉장고 대청소 (중고등)", "category": "청소", "estimated_minutes": 40, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "가족 욕실 대청소", "category": "청소", "estimated_minutes": 40, "intensity": "Hard", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 진학/상담 준비", "category": "육아/교육", "estimated_minutes": 30, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "가족 건강 관리 (검진)", "category": "위생", "estimated_minutes": 60, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "semiannual", "assignee_type": "adult_only"},
    {"name": "자녀 진로 대화", "category": "육아/교육", "estimated_minutes": 30, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "가전 수리/관리", "category": "관리", "estimated_minutes": 30, "intensity": "Normal", "family_size": "3인_중고등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "자녀 스트레스 해소 대화", "category": "육아/교육", "estimated_minutes": 20, "intensity": "Light", "family_size": "3인_중고등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},

    # ============================================================
    # 4인_영유아 (20개) — 막내 0~5세, 두 아이 모두 adult_only 대상
    # ============================================================
    {"name": "영아 새벽 수유/분유", "category": "육아/교육", "estimated_minutes": 30, "intensity": "Hard", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "영아 기저귀 (4인)", "category": "육아/교육", "estimated_minutes": 5, "intensity": "Light", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "두 아이 목욕 (4인)", "category": "육아/교육", "estimated_minutes": 40, "intensity": "Hard", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "어린이집/유치원 두 아이 등하원", "category": "육아/교육", "estimated_minutes": 45, "intensity": "Normal", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "두 아이 식사 준비 (4인)", "category": "요리", "estimated_minutes": 30, "intensity": "Normal", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "두 아이 빨래 (4인)", "category": "세탁", "estimated_minutes": 20, "intensity": "Light", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "장난감 정리 (4인 영유아)", "category": "정리정돈", "estimated_minutes": 15, "intensity": "Light", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "기저귀/물티슈 대량 구매", "category": "쇼핑", "estimated_minutes": 15, "intensity": "Light", "family_size": "4인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "이유식/유아식 주간 밀프렙", "category": "요리", "estimated_minutes": 60, "intensity": "Hard", "family_size": "4인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 방 바닥 매일 청소 (4인)", "category": "청소", "estimated_minutes": 20, "intensity": "Normal", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "가족 욕실 청소 (4인 영유아)", "category": "청소", "estimated_minutes": 30, "intensity": "Hard", "family_size": "4인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "전체 빨래 주간 세탁", "category": "세탁", "estimated_minutes": 30, "intensity": "Normal", "family_size": "4인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "가족 대량 장보기 (4인)", "category": "쇼핑", "estimated_minutes": 90, "intensity": "Normal", "family_size": "4인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 약 관리 (4인)", "category": "위생", "estimated_minutes": 10, "intensity": "Light", "family_size": "4인_영유아", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "주방 대청소 (4인)", "category": "청소", "estimated_minutes": 40, "intensity": "Hard", "family_size": "4인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이 성장 기록 (4인)", "category": "육아/교육", "estimated_minutes": 15, "intensity": "Light", "family_size": "4인_영유아", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "유아 소독 (젖꼭지/컵)", "category": "위생", "estimated_minutes": 10, "intensity": "Light", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "두 아이 예방접종 일정 관리", "category": "위생", "estimated_minutes": 15, "intensity": "Light", "family_size": "4인_영유아", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "침구 전체 교체 (4인)", "category": "세탁", "estimated_minutes": 45, "intensity": "Hard", "family_size": "4인_영유아", "recurrence_interval": "biweekly", "assignee_type": "adult_only"},
    {"name": "두 아이 읽어주기/놀아주기", "category": "육아/교육", "estimated_minutes": 30, "intensity": "Light", "family_size": "4인_영유아", "recurrence_interval": "daily", "assignee_type": "adult_only"},

    # ============================================================
    # 4인_초등 (20개) — 막내 6~12세, 아이 2명 child_assist 포함
    # ============================================================
    {"name": "큰아이 방청소 보조", "category": "청소", "estimated_minutes": 20, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "child_assist", "age_min": 9, "age_max": 12},
    {"name": "작은아이 신발/장난감 정리", "category": "정리정돈", "estimated_minutes": 10, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 6, "age_max": 8},
    {"name": "식탁 닦기 (4인 초등)", "category": "청소", "estimated_minutes": 5, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 6, "age_max": 12},
    {"name": "두 아이 분리수거 보조", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "child_assist", "age_min": 8, "age_max": 12},
    {"name": "형제 방 함께 청소", "category": "청소", "estimated_minutes": 25, "intensity": "Normal", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "child_assist", "age_min": 9, "age_max": 12, "description": "두 아이가 함께 방을 청소합니다."},
    {"name": "애완동물 밥주기 교대", "category": "기타", "estimated_minutes": 5, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 7, "age_max": 12},
    {"name": "부모 요리 보조 (4인 초등)", "category": "요리", "estimated_minutes": 15, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "daily", "assignee_type": "child_assist", "age_min": 10, "age_max": 12},
    {"name": "세탁물 건조대 걸기 보조", "category": "세탁", "estimated_minutes": 10, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "child_assist", "age_min": 9, "age_max": 12},
    # 부모 전담
    {"name": "가족 4인 장보기", "category": "쇼핑", "estimated_minutes": 90, "intensity": "Normal", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "두 아이 도시락 준비", "category": "요리", "estimated_minutes": 30, "intensity": "Normal", "family_size": "4인_초등", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "주방 대청소 (4인 초등)", "category": "청소", "estimated_minutes": 40, "intensity": "Hard", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "욕실 청소 (4인 초등)", "category": "청소", "estimated_minutes": 35, "intensity": "Hard", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "4인 침구 교체", "category": "세탁", "estimated_minutes": 50, "intensity": "Hard", "family_size": "4인_초등", "recurrence_interval": "biweekly", "assignee_type": "adult_only"},
    {"name": "두 아이 학원 스케줄 관리", "category": "육아/교육", "estimated_minutes": 20, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "두 아이 숙제 봐주기", "category": "육아/교육", "estimated_minutes": 45, "intensity": "Normal", "family_size": "4인_초등", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "가족 주말 대청소 (4인 초등)", "category": "청소", "estimated_minutes": 120, "intensity": "Hard", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "아이들 건강 관리 (진료)", "category": "위생", "estimated_minutes": 60, "intensity": "Normal", "family_size": "4인_초등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "주방 냉장고 주간 정리", "category": "요리", "estimated_minutes": 20, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "4인 가족 빨래 (부모)", "category": "세탁", "estimated_minutes": 30, "intensity": "Normal", "family_size": "4인_초등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "가전 점검 및 관리 (4인 초등)", "category": "관리", "estimated_minutes": 20, "intensity": "Light", "family_size": "4인_초등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},

    # ============================================================
    # 4인_중고등 (20개) — 막내 13~18세, 두 아이 child_independent
    # ============================================================
    {"name": "설거지 당번 4명 순환", "category": "요리", "estimated_minutes": 20, "intensity": "Light", "family_size": "4인_중고등", "recurrence_interval": "daily", "assignee_type": "child_independent", "age_min": 13, "description": "4명이 돌아가며 설거지 당번을 맡습니다."},
    {"name": "큰아이 거실 청소기", "category": "청소", "estimated_minutes": 25, "intensity": "Normal", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 15},
    {"name": "작은아이 방 청소기", "category": "청소", "estimated_minutes": 20, "intensity": "Light", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 13},
    {"name": "큰아이 자기 빨래 독립", "category": "세탁", "estimated_minutes": 40, "intensity": "Normal", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 16},
    {"name": "작은아이 빨래 넣기", "category": "세탁", "estimated_minutes": 10, "intensity": "Light", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 13},
    {"name": "분리수거 형제 교대", "category": "청소", "estimated_minutes": 15, "intensity": "Light", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 13},
    {"name": "동생 숙제 봐주기", "category": "육아/교육", "estimated_minutes": 30, "intensity": "Normal", "family_size": "4인_중고등", "recurrence_interval": "daily", "assignee_type": "child_independent", "age_min": 16, "description": "고등학생 형/누나가 동생 숙제를 도와줍니다."},
    {"name": "마트 심부름 (4인 중고등)", "category": "쇼핑", "estimated_minutes": 30, "intensity": "Normal", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 15},
    {"name": "쓰레기 버리기 (형제 교대)", "category": "청소", "estimated_minutes": 5, "intensity": "Light", "family_size": "4인_중고등", "recurrence_interval": "daily", "assignee_type": "child_independent", "age_min": 13},
    {"name": "욕실 청소 (큰아이)", "category": "청소", "estimated_minutes": 25, "intensity": "Normal", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "child_independent", "age_min": 16},
    # 부모 전담
    {"name": "4인 주간 대량 장보기", "category": "쇼핑", "estimated_minutes": 90, "intensity": "Normal", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "저녁 식사 조리 (4인)", "category": "요리", "estimated_minutes": 50, "intensity": "Normal", "family_size": "4인_중고등", "recurrence_interval": "daily", "assignee_type": "adult_only"},
    {"name": "주방 대청소 (4인 중고등)", "category": "청소", "estimated_minutes": 40, "intensity": "Hard", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "욕실 대청소 (부모)", "category": "청소", "estimated_minutes": 40, "intensity": "Hard", "family_size": "4인_중고등", "recurrence_interval": "weekly", "assignee_type": "adult_only"},
    {"name": "4인 침구 세탁 (부모)", "category": "세탁", "estimated_minutes": 50, "intensity": "Hard", "family_size": "4인_중고등", "recurrence_interval": "biweekly", "assignee_type": "adult_only"},
    {"name": "아이들 진학 상담 준비", "category": "육아/교육", "estimated_minutes": 30, "intensity": "Normal", "family_size": "4인_중고등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "가족 건강검진 예약", "category": "위생", "estimated_minutes": 20, "intensity": "Light", "family_size": "4인_중고등", "recurrence_interval": "annual", "assignee_type": "adult_only"},
    {"name": "냉장고 대청소 (4인 중고등)", "category": "청소", "estimated_minutes": 40, "intensity": "Normal", "family_size": "4인_중고등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "공과금/보험 관리", "category": "관리", "estimated_minutes": 20, "intensity": "Light", "family_size": "4인_중고등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
    {"name": "집 보안 점검 (도어락/CCTV)", "category": "관리", "estimated_minutes": 15, "intensity": "Light", "family_size": "4인_중고등", "recurrence_interval": "monthly", "assignee_type": "adult_only"},
]


def seed(db: Session, force: bool = False):
    """마켓플레이스 시드 데이터 삽입. force=True이면 기존 데이터 모두 삭제 후 재삽입."""
    existing = db.query(MarketplaceTemplate).count()
    if existing > 0 and not force:
        if existing >= len(TEMPLATES):
            return  # 최신 데이터 있으면 스킵
        # 템플릿 수가 적으면 강제 업데이트
        force = True
        print(f"[seed] 기존 {existing}개 < 목표 {len(TEMPLATES)}개 → 자동 갱신")

    if force:
        db.query(MarketplaceTemplate).delete()
        db.commit()

    for t in TEMPLATES:
        obj = MarketplaceTemplate(
            name=t["name"],
            category=t["category"],
            estimated_minutes=t["estimated_minutes"],
            intensity=t["intensity"],
            family_size=t.get("family_size", "전체"),
            description=t.get("description"),
            recurrence_interval=t.get("recurrence_interval"),
            recurrence_day=t.get("recurrence_day"),
            trigger_context=t.get("trigger_context"),
            age_min=t.get("age_min"),
            age_max=t.get("age_max"),
            assignee_type=t.get("assignee_type"),
            approved=True,
            import_count=0,
        )
        db.add(obj)
    db.commit()
    print(f"[seed] {len(TEMPLATES)}개 마켓플레이스 템플릿 삽입 완료")


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    seed(db)
    db.close()
