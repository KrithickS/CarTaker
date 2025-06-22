#!/usr/bin/env bash
# NOTE: we omit `-e` so that our trap still fires on SIGINT
set -uo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# 0) Locate and cd into the directory this script lives in
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# 1) CONFIG / ABSOLUTE PATHS
# ─────────────────────────────────────────────────────────────────────────────
CAM_PY="$SCRIPT_DIR/cam_qual.py"
DETECT_SH="$SCRIPT_DIR/run_model_eval.sh"
TEMP_SH="$SCRIPT_DIR/temp_log.sh"
MQ_SH="$SCRIPT_DIR/mq_runner.sh"
SERVO_SCRIPT="$SCRIPT_DIR/servo_control.py"

FACE_STATUS="$SCRIPT_DIR/face.status"
TEMP_STATUS="$SCRIPT_DIR/temp.status"

CAM_LOG="$SCRIPT_DIR/cam_qual.log"
DETECT_LOG="$SCRIPT_DIR/run_model_eval.log"
TEMP_LOG="$SCRIPT_DIR/temp_log.log"
MQ_LOG="$SCRIPT_DIR/mq_runner.log"

THRESHOLD_SECS=10
TEMP_LIMIT=50
INTERVAL=1

# ─────────────────────────────────────────────────────────────────────────────
# 2) SETUP CLEANUP HANDLER
# ─────────────────────────────────────────────────────────────────────────────
pids=()
cleanup() {
  echo
  echo "[master] 🛑 Caught interrupt – shutting down…"
  for pid in "${pids[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  exit 0
}
trap cleanup SIGINT SIGTERM

# ─────────────────────────────────────────────────────────────────────────────
# 3) LAUNCH YOUR PRODUCERS
# ─────────────────────────────────────────────────────────────────────────────
echo "[master] ▶ Starting camera capture…"
nohup python3 "$CAM_PY" > "$CAM_LOG" 2>&1 &
pids+=($!)

echo "[master] ▶ Starting face/emotion detector…"
nohup bash "$DETECT_SH" > "$DETECT_LOG" 2>&1 &
pids+=($!)

echo "[master] ▶ Starting temperature logger…"
nohup bash "$TEMP_SH" > "$TEMP_LOG" 2>&1 &
pids+=($!)

echo "[master] ▶ Starting CO₂ logger…"
nohup bash "$MQ_SH" > "$MQ_LOG" 2>&1 &
pids+=($!)

# ensure status files exist
: > "$FACE_STATUS"
: > "$TEMP_STATUS"

# ─────────────────────────────────────────────────────────────────────────────
# 4) MONITOR LOOP
# ─────────────────────────────────────────────────────────────────────────────
echo "[master] 🔄 Monitoring face & temp… (ctrl+c to stop)"
face_cnt=0
temp_cnt=0

while :; do
  # read & sanitize face.status
  raw_face=$(<"$FACE_STATUS" 2>/dev/null || echo 0)
  face=${raw_face//[^0-9]/}; face=${face:-0}

  # read & sanitize temp.status
  raw_temp=$(<"$TEMP_STATUS" 2>/dev/null || echo 0)
  temp_clean=${raw_temp//[!0-9.]/}
  temp_int=${temp_clean%%.*}; temp_int=${temp_int:-0}

  # update streaks
  if (( face == 1 )); then ((face_cnt++)); else face_cnt=0; fi
  if (( temp_int > TEMP_LIMIT )); then ((temp_cnt++)); else temp_cnt=0; fi

  # debug output
  echo "[debug] face=$face, temp=$temp_int, face_cnt=$face_cnt, temp_cnt=$temp_cnt"

  # danger
  if (( face_cnt >= THRESHOLD_SECS && temp_cnt >= THRESHOLD_SECS )); then
    echo "danger"

    # spin servo
    if [[ -x "$SERVO_SCRIPT" ]]; then
      python3 "$SERVO_SCRIPT" > /dev/null 2>&1 &
      pids+=($!)
      wait "${pids[-1]}"
    else
      echo "[master] ⚠ Servo script missing/executable bit not set"
    fi

    face_cnt=0
    temp_cnt=0
  fi

  sleep "$INTERVAL"
done
