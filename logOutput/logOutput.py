import time
import uuid
from datetime import datetime

LOG_FILE = "/shared/log.txt"


def log_loop():
    random_string = str(uuid.uuid4())
    while True:
        timestamp = datetime.utcnow().isoformat() + "Z"
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp}: {random_string}\n")
        time.sleep(5)


if __name__ == "__main__":
    log_loop()
