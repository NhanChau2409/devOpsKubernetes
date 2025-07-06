import time
import os

LOG_FILE = "/shared/log.txt"


def write_logs():
    """Write logs to the shared file"""
    counter = 0
    while True:
        try:
            with open(LOG_FILE, "a") as f:
                f.write(f"Log entry {counter}: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            counter += 1
            time.sleep(5)  # Write a log every 5 seconds
        except Exception as e:
            print(f"Error writing log: {e}")
            time.sleep(1)


if __name__ == "__main__":
    print("Starting log writer...")
    write_logs()
