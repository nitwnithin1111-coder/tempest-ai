"""
Starts both the LiveKit agent and the Flask web server
in a single process — works on Render's free tier.
"""
import subprocess
import sys
import os
import time

if __name__ == "__main__":
    print("🌩️  Starting Tempest AI...")

    # Start the LiveKit agent in background
    agent = subprocess.Popen(
        [sys.executable, "agent.py", "start"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    print("✅ Agent started (PID:", agent.pid, ")")

    # Small delay to let agent connect first
    time.sleep(2)

    # Start Flask server (blocks here — keeps the service alive)
    print("✅ Starting web server...")
    import server
    port = int(os.getenv("PORT", 8080))
    server.app.run(host="0.0.0.0", port=port, debug=False)
