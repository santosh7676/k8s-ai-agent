# k8s-ai-agent

> CrashLoopBackOff at 2AM: An AI agent that diagnoses, scales, and explains your Kubernetes cluster in plain English.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Claude](https://img.shields.io/badge/LLM-Claude%20API-orange.svg)](https://anthropic.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-326CE5.svg)](https://kubernetes.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What is this?

`k8s-ai-agent` is an open source Python-based AI agent that takes natural language prompts, translates them into Kubernetes operations, executes them safely, verifies results, and explains what it did in plain English.

Instead of this:
```bash
kubectl get pods --all-namespaces --field-selector=status.phase!=Running
kubectl describe pod payment-service-7d9f8b-xk2p9 -n production
kubectl logs payment-service-7d9f8b-xk2p9 -n production --previous
```

You type this:

> Why is my payment service down

And the agent does the rest.

## Features

- **Pod health diagnosis** — detects CrashLoopBackOff, OOMKilled, Pending, and ImagePullBackOff states with root cause analysis
- **Log analysis** — reads and summarises container logs intelligently
- **Intelligent scaling** — scales deployments safely with pre-checks and confirmation
- **Runbook generation** — auto-generates incident documentation after resolution
- **Dry-run mode** — shows what it would do before doing it
- **Audit logging** — records every action with reasoning for regulated environments

## Architecture

User prompt (plain English)
↓
Claude (reasoning layer via Anthropic API)
↓
Tool selection (kubectl, logs, events, metrics)
↓
Safe execution (dry-run first, then apply)
↓
Result verification
↓
Plain English explanation

## Tech Stack

- **Python 3.10+**
- **Claude API** (Anthropic) — LLM reasoning layer
- **kubectl** — Kubernetes operations via subprocess
- **Rich** — terminal output formatting
- **Docker** — containerised demo environment
- **Minikube** — local Kubernetes cluster

## Project Status

🚧 **Active development** — core agent loop and pod health checker in progress.

## Getting Started

Coming soon. Watch this repo for updates.

## Author

**Santosh Mahale** — AVP DevOps and Infrastructure Engineering
- GitHub: [@santosh7676](https://github.com/santosh7676)
- LinkedIn: [linkedin.com/in/santosh-mahale](https://linkedin.com/in/santosh-mahale-31722718b)
- HackerNoon: [hackernoon.com/u/santoshmahale](https://hackernoon.com/u/santoshmahale)

## License

MIT
