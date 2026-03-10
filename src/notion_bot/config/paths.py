import json
from pathlib import Path

def find_project_root(start_path: Path, marker_file: str = "pyproject.toml") -> Path:
    current = start_path.resolve()
    while not (current / marker_file).exists() and current != current.parent:
        current = current.parent
    return current

BASE_DIR = find_project_root(Path(__file__))

DATA = BASE_DIR / "data" 
HISTORY_FILE = DATA / "chat_history.json"

for path in [
    DATA
]:
    path.mkdir(parents=True, exist_ok=True)

for file in [
    HISTORY_FILE
]:
    if not file.exists():
        with open(file, "w") as f:
            json.dump([], f) 