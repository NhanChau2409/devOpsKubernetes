import time
import uuid
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify

app = Flask(__name__)

# Generate and store the random string (UUID)
random_string = str(uuid.uuid4())

status = {
    "random_string": random_string,
    "timestamp": datetime.utcnow().isoformat() + "Z",
}


def log_loop():
    while True:
        status["timestamp"] = datetime.utcnow().isoformat() + "Z"
        print(f"{status['timestamp']}: {random_string}")
        time.sleep(5)


@app.route("/status")
def get_status():
    return jsonify(status)


if __name__ == "__main__":
    Thread(target=log_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
