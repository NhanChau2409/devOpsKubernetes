import time
import requests
import os
from flask import Flask, Response
import threading

app = Flask(__name__)

# Ping pong service URL - will be resolved by Kubernetes DNS
PINGPONG_SERVICE_URL = "http://pingpong-service:8080"

# Global variables to store log data
log_entries = []
config_data = {"file_content": "", "message": ""}


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


def write_logs():
    """Write logs with ping count from pingpong service"""
    counter = 0

    # Read ConfigMap data once at startup
    file_content, message = read_config_data()
    config_data["file_content"] = file_content
    config_data["message"] = message
    print(f"file content: {file_content}")
    print(f"env variable: MESSAGE={message}")

    while True:
        try:
            # Get ping count from pingpong service
            response = requests.get(f"{PINGPONG_SERVICE_URL}/pings", timeout=5)
            if response.status_code == 200:
                ping_count = response.json().get("pings", 0)
                log_entry = f"Log entry {counter}: {time.strftime('%Y-%m-%d %H:%M:%S')} - Pings: {ping_count}"
            else:
                log_entry = f"Log entry {counter}: {time.strftime('%Y-%m-%d %H:%M:%S')} - Error getting ping count"

            # Store log entry for web display
            log_entries.append(log_entry)
            # Keep only last 100 entries to prevent memory issues
            if len(log_entries) > 100:
                log_entries.pop(0)

            print(log_entry)
            counter += 1
            time.sleep(5)  # Write a log every 5 seconds
        except requests.exceptions.RequestException as e:
            error_entry = f"Log entry {counter}: {time.strftime('%Y-%m-%d %H:%M:%S')} - Error connecting to pingpong service: {e}"
            log_entries.append(error_entry)
            if len(log_entries) > 100:
                log_entries.pop(0)
            print(error_entry)
            time.sleep(1)
        except Exception as e:
            error_entry = f"Log entry {counter}: {time.strftime('%Y-%m-%d %H:%M:%S')} - Error writing log: {e}"
            log_entries.append(error_entry)
            if len(log_entries) > 100:
                log_entries.pop(0)
            print(error_entry)
            time.sleep(1)


@app.route("/", methods=["GET"])
def root():
    """Root endpoint for health check and basic info"""
    try:
        # Get ping count from pingpong service
        response = requests.get(f"{PINGPONG_SERVICE_URL}/pings", timeout=5)
        ping_count = (
            response.json().get("pings", 0) if response.status_code == 200 else 0
        )
    except:
        ping_count = 0

    return {
        "service": "log-output",
        "status": "healthy",
        "current_pings": ping_count,
        "config": config_data,
        "endpoints": {
            "/": "Service information",
            "/logoutput": "Get log entries",
            "/logs": "Get recent log entries",
        },
    }, 200


@app.route("/logoutput", methods=["GET"])
def get_logs():
    """Return log entries as plain text"""
    try:
        # Get ping count from pingpong service
        response = requests.get(f"{PINGPONG_SERVICE_URL}/pings", timeout=5)
        if response.status_code == 200:
            ping_count = response.json().get("pings", 0)
        else:
            ping_count = 0
    except:
        ping_count = 0

    log_content = f"file content: {config_data['file_content']}\n"
    log_content += f"env variable: MESSAGE={config_data['message']}\n"
    log_content += f"{time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3]}: {os.getenv('HOSTNAME', 'unknown')}.\n"
    log_content += f"Ping / Pongs: {ping_count}\n"

    # Add recent log entries
    log_content += "\nRecent log entries:\n"
    for entry in log_entries[-10:]:  # Show last 10 entries
        log_content += f"{entry}\n"

    return Response(log_content, mimetype="text/plain")


@app.route("/logs", methods=["GET"])
def get_log_entries():
    """Return recent log entries as JSON"""
    return {
        "logs": log_entries[-20:],  # Return last 20 entries
        "total_entries": len(log_entries),
        "config": config_data,
    }, 200


if __name__ == "__main__":
    print("Starting log writer...")

    # Start log writing in a separate thread
    log_thread = threading.Thread(target=write_logs, daemon=True)
    log_thread.start()

    # Start Flask app
    app.run(host="0.0.0.0", port=8080)
