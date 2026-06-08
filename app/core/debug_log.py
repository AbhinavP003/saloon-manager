"""Debug session logging — remove after Cloud Run startup issue is resolved."""

import json
import os
import time
from pathlib import Path


def _log_path() -> Path:
    candidates = [
        Path("debug-754d4a.log"),
        Path("/tmp/debug-754d4a.log"),
        Path(os.environ.get("DEBUG_LOG_PATH", "debug-754d4a.log")),
    ]
    for path in candidates:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        except OSError:
            continue
    return Path("debug-754d4a.log")


def debug_log(location: str, message: str, data: dict | None = None, hypothesis_id: str = "") -> None:
    # #region agent log
    entry = {
        "sessionId": "754d4a",
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data or {},
        "hypothesisId": hypothesis_id,
    }
    line = json.dumps(entry) + "\n"
    try:
        with _log_path().open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass
    print(f"[DEBUG-754d4a] {message} {json.dumps(data or {})}", flush=True)
    # #endregion
