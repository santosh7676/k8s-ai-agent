from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich import box

console = Console()


def print_banner():
    """Print the k8s-ai-agent welcome banner."""
    console.print(Panel.fit(
        "[bold green]k8s-ai-agent[/bold green] — CrashLoopBackOff at 2AM\n"
        "[dim]AI-powered Kubernetes diagnostics in plain English[/dim]\n"
        "[dim]Type 'exit' to quit | 'audit' to see action log | 'help' for commands[/dim]",
        border_style="green"
    ))


def print_user_prompt():
    """Print the user input prompt."""
    return console.input("\n[bold cyan]k8s>[/bold cyan] ")


def print_thinking():
    """Show thinking indicator."""
    console.print("[dim yellow]Analysing your cluster...[/dim yellow]")


def print_agent_response(response: str):
    """Print the agent response in a styled panel."""
    console.print(Panel(
        Markdown(response),
        title="[bold green]Agent[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))


def print_tool_call(tool_name: str, command: str):
    """Show what kubectl command the agent is running."""
    console.print(f"  [dim cyan]Running:[/dim cyan] [cyan]{command}[/cyan]")


def print_tool_result(result: str, success: bool = True):
    """Show the result of a kubectl command."""
    style = "dim green" if success else "dim red"
    icon = "✓" if success else "✗"
    lines = result.strip().split("\n")[:5]
    for line in lines:
        console.print(f"  [{style}]{icon} {line}[/{style}]")


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_audit_log(entries: list):
    """Print audit log as a table."""
    table = Table(title="Audit Log", box=box.ROUNDED, border_style="cyan")
    table.add_column("Timestamp", style="dim", width=22)
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Command", style="white", width=60)

    for entry in entries[-10:]:
        table.add_row(
            entry["timestamp"][:19],
            entry["action_type"],
            entry["command"][:60]
        )
    console.print(table)


def print_help():
    """Print available commands."""
    console.print(Panel(
        "[bold]Available commands:[/bold]\n\n"
        "[cyan]Natural language queries:[/cyan]\n"
        "  Why is my payment service down?\n"
        "  Show me all failing pods in prod-ns\n"
        "  Scale the frontend deployment to 3 replicas\n"
        "  Generate a runbook for the broken-app incident\n\n"
        "[cyan]Special commands:[/cyan]\n"
        "  [bold]audit[/bold]  — show recent action log\n"
        "  [bold]help[/bold]   — show this help\n"
        "  [bold]exit[/bold]   — quit the agent",
        title="Help",
        border_style="cyan"
    ))
