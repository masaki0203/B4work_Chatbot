import json
import os
from datetime import datetime

HISTORIES_DIR = os.path.join(os.path.dirname(__file__), "../histories")


def save_history(messages: list[dict], name: str = "") -> str:
    os.makedirs(HISTORIES_DIR, exist_ok=True)
    filename = name.strip() or datetime.now().strftime("%Y%m%d_%H%M%S")
    if not filename.endswith(".json"):
        filename += ".json"
    path = os.path.join(HISTORIES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    return filename


def load_history(filename: str) -> list[dict]:
    path = os.path.join(HISTORIES_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_histories() -> list[str]:
    os.makedirs(HISTORIES_DIR, exist_ok=True)
    files = [f for f in os.listdir(HISTORIES_DIR) if f.endswith(".json")]
    return sorted(files, reverse=True)
