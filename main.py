from utils.display import (
    print_banner, print_user_prompt,
    print_error, print_audit_log, print_help
)
from utils.audit_logger import get_audit_log
from agent.core import run_agent

def main():
    print_banner()
    while True:
        try:
            user_input = print_user_prompt()
            if not user_input.strip():
                continue
            if user_input.lower() == "exit":
                print("\nGoodbye! Stay on-call, stay sharp.\n")
                break
            elif user_input.lower() == "audit":
                entries = get_audit_log()
                if entries:
                    print_audit_log(entries)
                else:
                    print("No audit entries yet.")
            elif user_input.lower() == "help":
                print_help()
            else:
                run_agent(user_input)
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type exit to quit.\n")
        except Exception as e:
            print_error(str(e))

if __name__ == "__main__":
    main()
