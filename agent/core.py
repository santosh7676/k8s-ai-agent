import json
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_ITERATIONS, DEFAULT_NAMESPACE
from tools.kubectl_tools import (
    get_pods, get_pod_details, get_pod_logs,
    get_events, scale_deployment, get_failing_pods,
    get_node_resources, get_resource_quota
)
from tools.log_analyzer import analyze_logs
from tools.runbook_generator import generate_runbook
from utils.audit_logger import log_action
from utils.display import (
    print_thinking, print_tool_call,
    print_tool_result, print_agent_response
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are k8s-ai-agent, an expert Kubernetes operations AI assistant.
You help engineers diagnose and fix Kubernetes issues in plain English.

Your capabilities:
- Diagnose pod failures: CrashLoopBackOff, OOMKilled, Pending, ImagePullBackOff
- Analyse container logs to find root causes
- Scale deployments safely with pre-checks
- Generate incident runbooks automatically
- Check cluster resource availability

Rules you must follow:
1. Always check pod status before taking any action
2. Always show what you found before recommending fixes
3. For scaling operations, always confirm current replica count first
4. In regulated environments, explain compliance considerations
5. Be concise but thorough -- engineers are tired at 2AM
6. Always suggest preventive measures after diagnosis

When you call a tool, explain what you are doing and why in plain English.
After getting tool results, explain what they mean before taking next steps.
"""

TOOLS = [
    {
        "name": "get_pods",
        "description": "Get all pods in a namespace or across all namespaces. Use this first to get an overview of pod health.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Kubernetes namespace. Use all for all namespaces."
                }
            },
            "required": []
        }
    },
    {
        "name": "get_pod_details",
        "description": "Get detailed information about a specific pod including events, conditions, and container states.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string", "description": "Name of the pod to describe"},
                "namespace": {"type": "string", "description": "Namespace the pod is in"}
            },
            "required": ["pod_name", "namespace"]
        }
    },
    {
        "name": "get_pod_logs",
        "description": "Get logs from a pod container. Use previous=true for crashed containers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string", "description": "Name of the pod"},
                "namespace": {"type": "string", "description": "Namespace the pod is in"},
                "previous": {"type": "boolean", "description": "Get logs from previous crashed container"},
                "tail": {"type": "integer", "description": "Number of log lines to return"}
            },
            "required": ["pod_name", "namespace"]
        }
    },
    {
        "name": "get_events",
        "description": "Get Kubernetes events from a namespace sorted by time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "description": "Namespace to get events from"}
            },
            "required": ["namespace"]
        }
    },
    {
        "name": "get_failing_pods",
        "description": "Get all pods that are not in Running state for a quick cluster health check.",
        "input_schema": {
            "type": "object",
            "properties": {
                "namespace": {"type": "string", "description": "Namespace to check. Leave empty for all namespaces."}
            },
            "required": []
        }
    },
    {
        "name": "scale_deployment",
        "description": "Scale a Kubernetes deployment to a specified number of replicas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "deployment": {"type": "string", "description": "Name of the deployment to scale"},
                "namespace": {"type": "string", "description": "Namespace the deployment is in"},
                "replicas": {"type": "integer", "description": "Target number of replicas"},
                "dry_run": {"type": "boolean", "description": "If true, show what would happen without changes"}
            },
            "required": ["deployment", "namespace", "replicas"]
        }
    },
    {
        "name": "get_node_resources",
        "description": "Check node CPU and memory usage. Use when pods are Pending or OOMKilled.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "analyze_logs",
        "description": "Analyze pod logs for common error patterns like OOM, connection refused, permission denied.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string", "description": "Name of the pod to analyze"},
                "namespace": {"type": "string", "description": "Namespace the pod is in"}
            },
            "required": ["pod_name", "namespace"]
        }
    },
    {
        "name": "generate_runbook",
        "description": "Generate an incident runbook documenting what happened, what was done, and how to prevent recurrence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string", "description": "Name of the affected pod"},
                "namespace": {"type": "string", "description": "Namespace of the affected pod"},
                "issue": {"type": "string", "description": "Brief description of the issue diagnosed"},
                "resolution": {"type": "string", "description": "Steps taken to resolve the issue"}
            },
            "required": ["pod_name", "namespace", "issue", "resolution"]
        }
    }
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    namespace = tool_input.get("namespace", DEFAULT_NAMESPACE)
    if namespace == "all":
        namespace = None

    if tool_name == "get_pods":
        result = get_pods(namespace)
    elif tool_name == "get_pod_details":
        result = get_pod_details(tool_input["pod_name"], namespace)
    elif tool_name == "get_pod_logs":
        result = get_pod_logs(
            tool_input["pod_name"],
            namespace,
            tool_input.get("previous", False),
            tool_input.get("tail", 50)
        )
    elif tool_name == "get_events":
        result = get_events(namespace)
    elif tool_name == "get_failing_pods":
        result = get_failing_pods(namespace)
    elif tool_name == "scale_deployment":
        result = scale_deployment(
            tool_input["deployment"],
            namespace,
            tool_input["replicas"],
            tool_input.get("dry_run", False)
        )
    elif tool_name == "get_node_resources":
        result = get_node_resources()
    elif tool_name == "analyze_logs":
        result = analyze_logs(tool_input["pod_name"], namespace)
    elif tool_name == "generate_runbook":
        result = generate_runbook(
            tool_input["pod_name"],
            namespace,
            tool_input["issue"],
            tool_input["resolution"]
        )
    else:
        result = {"success": False, "output": f"Unknown tool: {tool_name}"}

    output = result.get("output", "No output returned")
    print_tool_result(output, result.get("success", False))
    return output


def run_agent(user_query: str) -> str:
    print_thinking()
    log_action("USER_QUERY", user_query, "Processing")

    messages = [{"role": "user", "content": user_query}]
    iterations = 0

    while iterations < MAX_ITERATIONS:
        iterations += 1

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            log_action("AGENT_RESPONSE", user_query, final_text[:200])
            print_agent_response(final_text)
            return final_text

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    print_tool_call(tool_name, str(tool_input))
                    result = execute_tool(tool_name, tool_input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

    return "Maximum iterations reached. Please try a more specific query."
