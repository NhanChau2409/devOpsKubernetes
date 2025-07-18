import uuid
from flask import Flask
from datetime import datetime

app = Flask(__name__)
ping_counter = 0


@app.route("/pingpong", methods=["GET"])
def pingpong():
    global ping_counter
    ping_counter += 1
    timestamp = datetime.utcnow().isoformat() + "Z"
    random_string = str(uuid.uuid4())
    response = f"pong {ping_counter}"
    print(f"{timestamp}: {ping_counter}: {random_string}")
    return response, 200


@app.route("/pings", methods=["GET"])
def get_pings():
    """Return the current ping count without incrementing"""
    global ping_counter
    return {"pings": ping_counter}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
