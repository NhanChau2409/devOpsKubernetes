from flask import Flask, jsonify
import os

LOG_FILE = "/shared/log.txt"

app = Flask(__name__)


@app.route("/logs")
def get_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        return jsonify({"logs": lines})
    else:
        return jsonify({"logs": []})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
