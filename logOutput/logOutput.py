import time
import uuid
from datetime import datetime

# Generate and store the random string (UUID)
random_string = str(uuid.uuid4())

while True:
    # Get current UTC timestamp in ISO format
    timestamp = datetime.utcnow().isoformat() + "Z"
    print(f"{timestamp}: {random_string}")
    time.sleep(5)
