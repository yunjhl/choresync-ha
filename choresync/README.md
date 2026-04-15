# ChoreSync HA Addon

가족 집안일 관리 앱 — Home Assistant 애드온

## 기능

- **할일 관리**: 집안일 템플릿 + 점수 시스템 (분/5 × 강도 배율)
- **퀘스트**: 특별 임무 + 보상 포인트 상태머신
- **위시리스트**: 가족 포인트로 소원 성취
- **IoT 연동**: MQTT 트리거로 자동 할일 생성
- **실시간 알림**: SSE 기반 실시간 업데이트
- **통계**: 구성원별 점수 + 일별 추이 차트

## 설치

### Home Assistant 애드온 방식
1. HA 애드온 스토어 → 저장소 추가 → 이 저장소 URL 입력
2. ChoreSync 설치 후 설정:
   ```yaml
   secret_key: "your-secret-key-here"  # 32자 이상 랜덤 문자열
   demo_seed: false                      # true: 데모 데이터 자동 생성
   log_level: info
   mqtt_broker: ""                       # MQTT 브로커 IP (선택)
   ```
3. 시작 → 포트 8099 접속

### Docker 직접 실행
```bash
docker build -t choresync .
docker run -d \
  -p 8099:8099 \
  -v choresync_data:/data \
  -e SECRET_KEY=your-secret-key \
  -e DEMO_SEED=true \
  choresync
```

### 개발 환경
```bash
pip install -r requirements.txt
alembic upgrade head
DEMO_SEED=true python -m app.seed_demo
uvicorn app.main:app --reload --port 8099
```

## 점수 계산

```
score = round((estimated_minutes / 5) × intensity_multiplier, 2)
```
| 강도 | 배율 |
|------|------|
| Light | 1.0 |
| Normal | 1.5 |
| Hard | 2.0 |

## API 문서

`http://localhost:8099/api/docs` (Swagger UI)

## 기술 스택

- Python 3.12 + FastAPI + SQLAlchemy 2.0
- SQLite (데이터 영속성)
- HTMX + Pico CSS (프론트엔드)
- JWT 인증 (python-jose)
- aiomqtt (선택적 MQTT 연동)
