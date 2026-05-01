from flask import Flask
from flask_socketio import SocketIO
import redis
import threading
import json
import os

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CHANNEL = "telemetry_updates"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # use message_queue param if using multiple nodes

r = redis.from_url(REDIS_URL)

def redis_listener():
    pubsub = r.pubsub()
    pubsub.subscribe(CHANNEL)
    for msg in pubsub.listen():
        if not msg or msg['type'] != 'message':
            continue
        try:
            payload = json.loads(msg['data'])
        except Exception:
            payload = {"raw": msg['data'].decode() if isinstance(msg['data'], bytes) else str(msg['data'])}
        # broadcast to all connected clients
        socketio.emit('telemetry', payload)

@socketio.on('connect')
def on_connect():
    print('client connected')

@socketio.on('disconnect')
def on_disconnect():
    print('client disconnected')

if __name__ == "__main__":
    t = threading.Thread(target=redis_listener, daemon=True)
    t.start()
    socketio.run(app, host="0.0.0.0", port=6000)