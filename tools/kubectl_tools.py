import subprocess
import json
from config import DRY_RUN
from utils.audit_logger import log_action


def run_kubectl(command: list, dry_run: bool = False) -> dict:
    """Execute a kubectl command and return structured output."""
    full_command = ["kubectl"] + command
    command_str = " ".join(full_command)

    if dry_run or DRY_RUN:
        log_action("DRY_RUN", command_str, "Skipped — dry run mode")
        return {"success": True, "output": f"[DRY RUN] Would execute: {command_str}", "dry_run": True}

    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=30
        )
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        log_action("KUBECTL", command_str, output.strip())
        return {"success": success, "output": output.strip(), "dry_run": False}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Command timed out after 30 seconds", "dry_run": False}
    except Exception as e:
        return {"success": False, "output": str(e), "dry_run": False}


def get_pods(namespace: str = None) -> dict:
    """Get all pods, optionally filtered by namespace."""
    cmd = ["get", "pods", "-o", "json"]
    if namespace:
        cmd += ["-n", namespace]
    else:
        cmd += ["--all-namespaces"]
    return run_kubectl(cmd)


def get_pod_details(pod_name: str, namespace: str) -> dict:
    """Describe a specific pod for detailed diagnostics."""
    return run_kubectl(["describe", "pod", pod_name, "-n", namespace])


def get_pod_logs(pod_name: str, namespace: str, previous: bool = False, tail: int = 50) -> dict:
    """Get logs from a pod, optionally from previous crashed container."""
    cmd = ["logs", pod_name, "-n", namespace, f"--tail={tail}"]
    if previous:
        cmd.append("--previous")
    return run_kubectl(cmd)


def get_events(namespace: str) -> dict:
    """Get events from a namespace sorted by time."""
    return run_kubectl([
        "get", "events",
        "-n", namespace,
        "--sort-by=.lastTimestamp"
    ])


def scale_deployment(deployment: str, namespace: str, replicas: int, dry_run: bool = False) -> dict:
    """Scale a deployment to specified replica count."""
    # First get current replica count for safety check
    current = run_kubectl([
        "get", "deployment", deployment,
        "-n", namespace,
        "-o", "jsonpath={.spec.replicas}"
    ])

    cmd = ["scale", "deployment", deployment,
           "-n", namespace, f"--replicas={replicas}"]

    if dry_run or DRY_RUN:
        return run_kubectl(cmd, dry_run=True)

    result = run_kubectl(cmd)
    if result["success"]:
        verify = run_kubectl([
            "rollout", "status",
            f"deployment/{deployment}",
            "-n", namespace
        ])
        result["verification"] = verify["output"]
    return result


def get_node_resources() -> dict:
    """Check node resource availability."""
    return run_kubectl(["top", "nodes", "--no-headers"])


def get_resource_quota(namespace: str) -> dict:
    """Check resource quotas in a namespace."""
    return run_kubectl(["describe", "resourcequota", "-n", namespace])


def get_failing_pods(namespace: str = None) -> dict:
    """Get all non-running pods for quick health check."""
    cmd = ["get", "pods"]
    if namespace:
        cmd += ["-n", namespace]
    else:
        cmd += ["--all-namespaces"]
    cmd += ["--field-selector=status.phase!=Running", "-o", "json"]
    return run_kubectl(cmd)
