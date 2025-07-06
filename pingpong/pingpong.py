import os
import uuid
from flask import Flask
from datetime import datetime

app = Flask(__name__)
LOG_FILE = "/shared/log.txt"


def get_counter():
    if not os.path.exists(LOG_FILE):
        return 0
    with open(LOG_FILE, "r") as f:
        return sum(1 for _ in f)


@app.route("/pingpong", methods=["GET"])
def pingpong():
    counter = get_counter()
    timestamp = datetime.utcnow().isoformat() + "Z"
    random_string = str(uuid.uuid4())
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp}: {counter}: {random_string}\n")
    response = f"pong {counter}"
    return response, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
