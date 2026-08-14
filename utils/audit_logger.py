import json
import datetime
from config import AUDIT_LOG_FILE


def log_action(action_type: str, command: str, result: str):
    """Log every agent action with timestamp for full auditability."""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "action_type": action_type,
        "command": command,
        "result": result[:500] if len(result) > 500 else result
    }
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_audit_log() -> list:
    """Read and return all audit log entries."""
    try:
        with open(AUDIT_LOG_FILE, "r") as f:
            return [json.loads(line) for line in f.readlines()]
    except FileNotFoundError:
        return []


def format_audit_summary() -> str:
    """Return a formatted summary of recent actions."""
    entries = get_audit_log()
    if not entries:
        return "No actions logged yet."

    summary = []
    for entry in entries[-10:]:
        summary.append(
            f"[{entry['timestamp']}] {entry['action_type']}: {entry['command'][:80]}"
        )
    return "\n".join(summary)
