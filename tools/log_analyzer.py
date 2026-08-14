import re
from tools.kubectl_tools import get_pod_logs
from utils.audit_logger import log_action

ERROR_PATTERNS = [
    (r"OOMKilled|out of memory|Cannot allocate memory", "OOM -- pod exceeded memory limits"),
    (r"Connection refused|ECONNREFUSED", "Connection refused -- dependency may be down"),
    (r"CrashLoopBackOff", "CrashLoopBackOff -- container keeps crashing on startup"),
    (r"permission denied|EACCES", "Permission denied -- check RBAC or file permissions"),
    (r"ImagePullBackOff|ErrImagePull", "Image pull failed -- check image name and registry credentials"),
    (r"Liveness probe failed|Readiness probe failed", "Health probe failing -- check probe configuration"),
    (r"exit code [1-9]", "Non-zero exit code -- application crashed"),
]

def analyze_logs(pod_name: str, namespace: str) -> dict:
    current_logs = get_pod_logs(pod_name, namespace, previous=False, tail=100)
    previous_logs = get_pod_logs(pod_name, namespace, previous=True, tail=100)

    all_logs = ""
    if current_logs["success"]:
        all_logs += current_logs["output"]
    if previous_logs["success"]:
        all_logs += "\n" + previous_logs["output"]

    if not all_logs.strip():
        return {"success": False, "output": "No logs available for this pod."}

    findings = []
    for pattern, description in ERROR_PATTERNS:
        if re.search(pattern, all_logs, re.IGNORECASE):
            findings.append(description)

    if findings:
        analysis = "Log analysis findings:\n"
        for i, finding in enumerate(findings, 1):
            analysis += f"{i}. {finding}\n"
        analysis += "\nRaw logs (last 20 lines):\n"
        analysis += "\n".join(all_logs.strip().split("\n")[-20:])
    else:
        analysis = "No common error patterns detected in logs.\n\n"
        analysis += f"Raw logs:\n{all_logs.strip()}"

    log_action("LOG_ANALYSIS", f"{pod_name}/{namespace}", analysis[:200])
    return {"success": True, "output": analysis}
