"""설정 로더 — 환경 변수 및 HA options.json에서 읽기"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./choresync.db"
    jwt_secret: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    demo_seed: bool = False
    mqtt_broker: str = ""
    mqtt_user: str = ""
    mqtt_pass: str = ""
    mqtt_port: int = 1883
    # HA 설정
    ha_url: str = ""           # e.g. "http://192.168.1.102:8123"
    ha_token: str = ""         # HA long-lived access token
    ha_tts_entity: str = "tts.google_translate_en_com"
    ha_webhook_id: str = ""    # HA automation webhook ID
    # Scheduler
    scheduler_enabled: bool = True
    # LLM 챗봇 (Ollama)
    llm_url: str = ""          # e.g. "http://192.168.1.199:8080" or "http://localhost:11434"
    llm_model: str = "qwen2.5:1.5b"   # CPU 미니PC 기본 모델

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
