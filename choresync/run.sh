#!/bin/bash
set -e

# HA 애드온: /data/options.json에서 설정 읽기
OPTIONS="/data/options.json"
if [ -f "${OPTIONS}" ]; then
  echo "[ChoreSync] Loading options from ${OPTIONS}..."
  export SECRET_KEY=$(jq -r ".secret_key // \"\"" "${OPTIONS}")
  export DEMO_SEED=$(jq -r ".demo_seed // false" "${OPTIONS}")
  export LOG_LEVEL=$(jq -r ".log_level // \"info\"" "${OPTIONS}")
  export MQTT_BROKER=$(jq -r ".mqtt_broker // \"\"" "${OPTIONS}")
  export MQTT_USER=$(jq -r ".mqtt_user // \"\"" "${OPTIONS}")
  export MQTT_PASS=$(jq -r ".mqtt_pass // \"\"" "${OPTIONS}")
  export MQTT_PORT=$(jq -r ".mqtt_port // 1883" "${OPTIONS}")
  export HA_URL=$(jq -r ".ha_url // \"\"" "${OPTIONS}")
  export HA_TOKEN=$(jq -r ".ha_token // \"\"" "${OPTIONS}")
  export HA_TTS_ENTITY=$(jq -r ".ha_tts_entity // \"\"" "${OPTIONS}")
  export HA_WEBHOOK_ID=$(jq -r ".ha_webhook_id // \"\"" "${OPTIONS}")
  export SCHEDULER_ENABLED=$(jq -r ".scheduler_enabled // true" "${OPTIONS}")
  export LLM_URL=$(jq -r ".llm_url // \"\"" "${OPTIONS}")
  export LLM_MODEL=$(jq -r ".llm_model // \"qwen2.5:1.5b\"" "${OPTIONS}")
fi

DB_PATH="${DB_PATH:-/data/choresync.db}"
PORT="${PORT:-8099}"
LOG_LEVEL="${LOG_LEVEL:-info}"

export DATABASE_URL="sqlite:///${DB_PATH}"
export PYTHONPATH="/app:${PYTHONPATH}"

echo "[ChoreSync] v0.7.0 | DB: ${DB_PATH} | Port: ${PORT}"
echo "[ChoreSync] Running migrations..."
alembic upgrade head

if [ "${DEMO_SEED}" = "true" ]; then
  echo "[ChoreSync] Seeding demo data..."
  python -m app.seed_demo
fi

echo "[ChoreSync] Seeding marketplace templates..."
python -m app.seed_marketplace

echo "[ChoreSync] Starting server on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" --log-level "${LOG_LEVEL}" --no-access-log
