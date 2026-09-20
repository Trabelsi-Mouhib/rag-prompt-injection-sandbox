import json
import os
from datetime import datetime, timezone

LOG_FILE = "logs/security_audit.json"

def log_security_event(event_type: str, layer: str, details: str, user_query: str):
    """Génère un log JSON structuré pour intégration SIEM."""
    os.makedirs("logs", exist_ok=True)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": "WARNING",
        "event_type": event_type,
        "layer": layer,
        "details": details,
        "user_query": user_query
    }

    # Écriture sous forme de ligne JSON (NDJSON)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
