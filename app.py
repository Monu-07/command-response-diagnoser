
from flask import Flask, request, jsonify
from collections import deque
from threading import Lock
from datetime import datetime, timezone

app = Flask(__name__)

records = deque(maxlen=500)
records_lock = Lock()


@app.get("/")
def home():
    return "Command-Response Diagnoser API is running!"


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/timing")
def receive_timing():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON data"}), 400

    response_ms = data.get("response_ms")

    if (
        isinstance(response_ms, bool)
        or not isinstance(response_ms, (int, float))
        or response_ms < 0
    ):
        return jsonify({
            "error": "response_ms must be a non-negative number"
        }), 400

    record = {
        "response_ms": response_ms,
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    with records_lock:
        records.append(record)

    return jsonify({
        "message": "Timing record received",
        "record": record
    }), 201


@app.get("/records")
def get_records():
    with records_lock:
        result = list(records)

    return jsonify(result)
