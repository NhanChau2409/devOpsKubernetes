from flask import Flask, Response
import os

LOG_FILE = "/shared/log.txt"

app = Flask(__name__)


@app.route("/logs")
def get_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            content = f.read()
        return Response(content, mimetype="text/plain")
    else:
        return Response("No logs yet.", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
