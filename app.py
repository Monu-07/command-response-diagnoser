from flask import Flask, request, jsonify
from collections import deque
from threading import Lock
from datetime import datetime, timezone

app = Flask(__name__)

records = deque(maxlen=500)
lock = Lock()

@app.get("/")
def home():
    return "Command-Response Diagnoser API is running."

@app.post("/timing")
def receive_timing():
    data = request.get_json(silent=True) or {}

    response_ms = data.get("response_ms")

    if (
        isinstance(response_ms, bool)
        or not isinstance(response_ms, (int, float))
        or response_ms < 0
    ):
        return jsonify({"error": "Invalid response_ms"}), 400

    # Automatically determine the status based on duration for your LCD
    if response_ms < 1000:
        status = "normal"
    elif response_ms < 2000:
        status = "delay"
    else:
        status = "overtime"

    record = {
        "response_ms": response_ms,
        "status": status,
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    with lock:
        records.append(record)

    # Return plain text status so the ESP32 can send it right to the STM32 LCD
    return status, 201, {'Content-Type': 'text/plain'}

@app.get("/records")
def get_records():
    with lock:
        result = list(records)

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
