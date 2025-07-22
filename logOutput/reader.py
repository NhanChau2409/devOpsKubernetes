from flask import Flask, Response
import requests
import time
import os

# Ping pong service URL - will be resolved by Kubernetes DNS
PINGPONG_SERVICE_URL = "http://pingpong-service:8080"

app = Flask(__name__)


def read_config_data():
    """Read ConfigMap data from file and environment variable"""
    file_content = ""
    message = ""

    # Read file content from mounted ConfigMap
    try:
        with open("/config/information.txt", "r") as f:
            file_content = f.read().strip()
    except FileNotFoundError:
        file_content = "Config file not found"
    except Exception as e:
        file_content = f"Error reading config file: {e}"

    # Read environment variable
    message = os.getenv("MESSAGE", "MESSAGE not set")

    return file_content, message


@app.route("/")
def get_logs():
    """Main endpoint that shows logs with current ping count"""
    # Read ConfigMap data
    file_content, message = read_config_data()

    try:
        # Get ping count from pingpong service
        response = requests.get(f"{PINGPONG_SERVICE_URL}/pings", timeout=5)
        if response.status_code == 200:
            ping_count = response.json().get("pings", 0)
            log_content = f"file content: {file_content}\n"
            log_content += f"env variable: MESSAGE={message}\n"
            log_content += f"{time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]}: {os.getenv('HOSTNAME', 'unknown')}.\n"
            log_content += f"Ping / Pongs: {ping_count}\n"
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
