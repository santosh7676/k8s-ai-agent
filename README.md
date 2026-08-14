# k8s-ai-agent

> CrashLoopBackOff at 2AM: An AI agent that diagnoses, scales, and explains your Kubernetes cluster in plain English.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Claude](https://img.shields.io/badge/LLM-Claude%20API-orange.svg)](https://anthropic.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-326CE5.svg)](https://kubernetes.io)
[![Minikube](https://img.shields.io/badge/Tested%20on-Minikube-blue.svg)](https://minikube.sigs.k8s.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What is this?

k8s-ai-agent is an open source Python-based AI agent that takes natural language prompts,
translates them into Kubernetes operations, executes them safely, verifies results,
and explains what it did in plain English.

Instead of this:

    kubectl get pods --all-namespaces --field-selector=status.phase!=Running
    kubectl describe pod payment-service-7d9f8b-xk2p9 -n production
    kubectl logs payment-service-7d9f8b-xk2p9 -n production --previous

You type this:

    > Why is my payment service down?

And the agent does the rest.

## Demo

    k8s> Why is broken-app pod failing in prod-ns namespace?
    Analysing your cluster...

    Agent Response:
    Diagnosis: broken-app is in CrashLoopBackOff

    The pod has restarted 94 times over 7.5 hours.
    Root cause: container command hardcoded to exit with code 1.

    /bin/sh -c "echo starting && sleep 2 && exit 1"

    Fix: kubectl edit deployment broken-app -n prod-ns
    and correct the args field to the intended startup command.

    Prevention:
    - Add liveness/readiness probes
    - Alert when restartCount > 5 in 10 minutes
    - Validate entrypoints in CI/CD before deploying to production

## Features

- Pod health diagnosis: detects CrashLoopBackOff, OOMKilled, Pending, ImagePullBackOff with root cause analysis
- Log analysis: reads and summarises container logs intelligently using pattern matching
- Intelligent scaling: scales deployments safely with pre-checks and verification
- Runbook generation: auto-generates incident documentation after resolution
- Dry-run mode: shows what it would do before doing it
- Audit logging: records every kubectl action with timestamp and reasoning for regulated environments
- Rich terminal UI: clean formatted output with colour coding and structured panels

## Architecture

    User prompt (plain English)
            |
        Claude API (reasoning layer - Anthropic)
            |
        Tool selection (kubectl, logs, events, metrics)
            |
        Safe execution (dry-run first, then apply)
            |
        Result verification
            |
        Plain English explanation with recommendations

## Project Structure

    k8s-ai-agent/
    |-- agent/
    |   |-- core.py          # Main agent loop with Claude API and tool use
    |   |-- __init__.py
    |-- tools/
    |   |-- kubectl_tools.py     # kubectl command wrappers
    |   |-- log_analyzer.py      # Log pattern analysis
    |   |-- runbook_generator.py # Incident runbook generation
    |   |-- __init__.py
    |-- utils/
    |   |-- audit_logger.py  # Full audit trail for compliance
    |   |-- display.py       # Rich terminal UI
    |   |-- __init__.py
    |-- main.py              # Entry point
    |-- config.py            # Configuration
    |-- requirements.txt

## Tech Stack

- Python 3.10+
- Claude API (Anthropic) -- LLM reasoning layer
- kubectl -- Kubernetes operations via subprocess
- Rich -- terminal output formatting
- Docker -- containerised demo environment
- Minikube -- local Kubernetes cluster

## Getting Started

### Prerequisites

- Python 3.10+
- kubectl installed and configured
- Minikube or any Kubernetes cluster
- Anthropic API key (console.anthropic.com)

### Installation

    git clone https://github.com/santosh7676/k8s-ai-agent.git
    cd k8s-ai-agent
    pip install -r requirements.txt

### Configuration

Create a .env file:

    ANTHROPIC_API_KEY=your_api_key_here
    DRY_RUN=false
    DEFAULT_NAMESPACE=default
    AUDIT_LOG_FILE=audit.log

### Run

    python3 main.py

## Available Commands

Natural language queries:

    k8s> Why is my payment service down?
    k8s> Show me all failing pods in prod-ns
    k8s> Scale the frontend deployment to 3 replicas
    k8s> Generate a runbook for the broken-app incident

Special commands:

    audit  -- show recent action log with timestamps
    help   -- show available commands
    exit   -- quit the agent

## Audit Log

Every action is logged for full traceability:

    Timestamp              Type          Command
    2026-08-14T16:00:00    KUBECTL       kubectl describe pod broken-app -n prod-ns
    2026-08-14T16:00:00    LOG_ANALYSIS  broken-app/prod-ns
    2026-08-14T16:00:16    AGENT_RESPO   Why is broken-app pod failing in prod-ns

## Use Cases

- On-call diagnosis: instantly understand why a pod is failing at 2AM
- Runbook automation: auto-generate incident documentation
- Cluster health checks: scan all namespaces for issues in one query
- Safe scaling: scale deployments with built-in verification
- Compliance: full audit trail of every action taken

## Presented At

- CNCG Pune August Meetup (submitted)
- TechXConf AI, Cloud and Data Conference 2026 (submitted)

## Author

Santosh Mahale -- AVP DevOps and Infrastructure Engineering

- GitHub: https://github.com/santosh7676
- LinkedIn: https://linkedin.com/in/santosh-mahale
- HackerNoon: https://hackernoon.com/u/santoshmahale

## Related Projects

- ansible-ai-agent: https://github.com/rockygeekz/ansible-ai-agent

## License

MIT
