import time
import requests
import os

# Ping pong service URL - will be resolved by Kubernetes DNS
PINGPONG_SERVICE_URL = "http://pingpong-service:8080"


def write_logs():
    """Write logs with ping count from pingpong service"""
    counter = 0
    while True:
        try:
            # Get ping count from pingpong service
            response = requests.get(f"{PINGPONG_SERVICE_URL}/pings", timeout=5)
            if response.status_code == 200:
                ping_count = response.json().get("pings", 0)
                log_entry = f"Log entry {counter}: {time.strftime('%Y-%m-%d %H:%M:%S')} - Pings: {ping_count}"
            else:
                log_entry = f"Log entry {counter}: {time.strftime('%Y-%m-%d %H:%M:%S')} - Error getting ping count"

            print(log_entry)
            counter += 1
            time.sleep(5)  # Write a log every 5 seconds
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to pingpong service: {e}")
            time.sleep(1)
        except Exception as e:
            print(f"Error writing log: {e}")
            time.sleep(1)


if __name__ == "__main__":
    print("Starting log writer...")
    write_logs()
