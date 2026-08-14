import os
from dotenv import load_dotenv

load_dotenv()

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-6"

# Agent settings
MAX_ITERATIONS = 10
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# Kubernetes settings
KUBECONFIG = os.getenv("KUBECONFIG", os.path.expanduser("~/.kube/config"))
DEFAULT_NAMESPACE = os.getenv("DEFAULT_NAMESPACE", "default")

# Audit log
AUDIT_LOG_FILE = os.getenv("AUDIT_LOG_FILE", "audit.log")
