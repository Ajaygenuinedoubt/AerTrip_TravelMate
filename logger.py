import json
import os
from datetime import datetime

LOG_FILE = "logs/conversations.json"

def log_turn(user_text, assistant_text, latency):

    os.makedirs("logs", exist_ok=True)

    record = {
        "timestamp": datetime.now().isoformat(),
        "user": user_text,
        "assistant": assistant_text,
        "latency": latency
    }

    data = []

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        except:
            data = []

    data.append(record)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)