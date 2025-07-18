from flask import Flask, Response
import requests
import time

# Ping pong service URL - will be resolved by Kubernetes DNS
PINGPONG_SERVICE_URL = "http://pingpong-service:8080"

app = Flask(__name__)


@app.route("/")
def get_logs():
    """Main endpoint that shows logs with current ping count"""
    try:
        # Get ping count from pingpong service
        response = requests.get(f"{PINGPONG_SERVICE_URL}/pings", timeout=5)
        if response.status_code == 200:
            ping_count = response.json().get("pings", 0)
            log_content = f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            log_content += f"Total pings: {ping_count}\n"
            log_content += f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            log_content = f"Error getting ping count from pingpong service\n"
            log_content += f"Status code: {response.status_code}\n"
    except requests.exceptions.RequestException as e:
        log_content = f"Error connecting to pingpong service: {e}\n"
    except Exception as e:
        log_content = f"Unexpected error: {e}\n"

    return Response(log_content, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
