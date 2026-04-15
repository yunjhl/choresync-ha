# ChoreSync — Home Assistant 애드온

가족 구성원이 함께 집안일을 관리하는 Home Assistant 애드온입니다.
할일 점수제, 퀘스트, 위시리스트, IoT 자동화, LLM 챗봇을 통합 제공합니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 할일 관리 | 템플릿 + 담당자 지정 + 점수 시스템 |
| 퀘스트 | 특별 임무 + 보상 포인트 |
| 위시리스트 | 가족 포인트로 소원 달성 |
| 가족 레벨 | 함께 올리는 가족 레벨 + 업적 배지 |
| IoT 연동 | MQTT 트리거 → 자동 할일 생성 |
| TTS 브리핑 | 매일 아침 날씨 + 오늘 할일 읽어주기 |
| LLM 챗봇 | 자연어로 할일 추가 ("내일 설거지 민준이가 해줘") |
| 주간 리포트 | 가족 활동 요약 카드 |
| PWA 지원 | 모바일 홈 화면에 설치 가능 |

---

## 설치 방법

### 1단계 — 저장소 추가

1. Home Assistant에서 **설정 → 애드온 → 애드온 스토어**로 이동합니다.
2. 우측 상단 **⋮ → 저장소** 를 클릭합니다.
3. 아래 URL을 입력하고 **추가**를 누릅니다.

   ```
   https://github.com/yunjhl/choresync-ha
   ```

4. 페이지를 새로고침하면 애드온 스토어에 **ChoreSync**가 표시됩니다.

### 2단계 — 애드온 설치

1. **ChoreSync**를 클릭 → **설치**를 누릅니다.
2. 설치 완료 후 **설정** 탭으로 이동합니다.

### 3단계 — 설정

설정 탭에서 아래 항목을 채운 뒤 저장합니다.

```yaml
secret_key: "랜덤-32자-이상-문자열"   # 필수: 세션 암호화 키
demo_seed: false                        # true로 설정 시 데모 데이터 자동 생성
log_level: info

# MQTT (선택 — IoT 자동 완료 사용 시)
mqtt_broker: "192.168.1.x"
mqtt_user: "사용자명"
mqtt_pass: "비밀번호"
mqtt_port: 1883

# TTS 브리핑 (선택 — 아침 브리핑 사용 시)
ha_url: "http://homeassistant.local:8123"
ha_token: "HA Long-Lived Access Token"
ha_tts_entity: "tts.google_translate_ko_com"

# LLM 챗봇 (선택 — Ollama 등 로컬 LLM 사용 시)
llm_url: "http://192.168.1.x:11434"
llm_model: "exaone3.5:2.4b"
```

> `secret_key`는 터미널에서 `openssl rand -hex 32` 로 생성할 수 있습니다.

### 4단계 — 시작

1. **시작** 버튼을 누릅니다.
2. HA 사이드바에 빗자루 아이콘(🧹)이 생기면 성공입니다.
3. 또는 직접 `http://<HA주소>:8099` 로 접속합니다.

---

## 처음 실행 시

1. **회원가입**으로 계정을 만듭니다.
2. **가족 만들기** → 가족 이름 입력.
3. 구성원을 초대하거나 직접 추가합니다.
4. 할일 템플릿에서 원하는 집안일을 등록합니다.

데모 데이터를 먼저 보고 싶다면 설정에서 `demo_seed: true` 후 재시작하세요.

---

## HA Long-Lived Access Token 발급 방법

TTS 브리핑 또는 HA 연동 기능을 사용하려면 토큰이 필요합니다.

1. HA → 좌측 하단 프로필 아이콘 클릭
2. 스크롤 내려서 **보안 → 장기 액세스 토큰 → 만들기**
3. 이름 입력 후 생성 → 토큰 복사
4. ChoreSync 설정의 `ha_token`에 붙여넣기

---

## Docker로 직접 실행 (HA 없이)

```bash
docker run -d \
  --name choresync \
  -p 8099:8099 \
  -v choresync_data:/data \
  -e SECRET_KEY=your-secret-key-here \
  -e DEMO_SEED=true \
  ghcr.io/yunjhl/choresync:latest
```

---

## 점수 계산

```
점수 = round(예상시간(분) / 5 × 강도배율, 2)
```

| 강도 | 배율 | 예시 (30분) |
|------|------|------------|
| 가벼움 | 1.0 | 6점 |
| 보통 | 1.5 | 9점 |
| 힘듦 | 2.0 | 12점 |

---

## 기술 스택

- **백엔드**: Python 3.12 · FastAPI · SQLAlchemy 2.0 · SQLite
- **프론트엔드**: HTMX · Pico CSS · Chart.js · FullCalendar
- **인증**: JWT (python-jose)
- **연동**: aiomqtt · Home Assistant REST/WebSocket API
- **AI**: Ollama (로컬 LLM) · 규칙 기반 폴백

## API 문서

애드온 실행 후 `http://<HA주소>:8099/api/docs` 에서 Swagger UI를 확인할 수 있습니다.
