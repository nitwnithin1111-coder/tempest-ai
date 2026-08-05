import os
import uuid
import subprocess
import sys
import threading
import time
from datetime import timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from livekit.api import AccessToken, VideoGrants
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

LIVEKIT_API_KEY    = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL        = os.getenv("LIVEKIT_URL")
ROOM_NAME          = "tempest-room"


def start_agent():
    """Start the LiveKit agent in background and restart if it crashes."""
    time.sleep(3)
    while True:
        print("🤖 Starting Tempest AI agent...", flush=True)
        try:
            proc = subprocess.Popen(
                [sys.executable, "agent.py", "start"],
                stdout=sys.stdout,
                stderr=sys.stderr,
                env=os.environ.copy()
            )
            print(f"✅ Agent running (PID: {proc.pid})", flush=True)
            proc.wait()
            print("⚠️  Agent stopped — restarting in 5s...", flush=True)
        except Exception as e:
            print(f"❌ Agent error: {e} — retrying in 5s...", flush=True)
        time.sleep(5)


# Start agent in background thread when server boots
agent_thread = threading.Thread(target=start_agent, daemon=True)
agent_thread.start()


@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/api/token")
def get_token():
    participant_name = request.args.get("name", f"user-{uuid.uuid4().hex[:6]}")

    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return jsonify({"error": "LiveKit credentials not configured"}), 500

    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(participant_name)
        .with_name(participant_name)
        .with_grants(VideoGrants(
            room_join=True, room=ROOM_NAME,
            can_publish=True, can_subscribe=True
        ))
        .with_ttl(timedelta(hours=2))
        .to_jwt()
    )

    return jsonify({"token": token, "url": LIVEKIT_URL, "room": ROOM_NAME})


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "agent": "Tempest AI"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"🌩️  Tempest AI server running at http://localhost:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False)
