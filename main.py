import sys
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.markdown import Markdown
except ImportError:
    print("Required: 'rich' library. Run: pip install rich")
    sys.exit(1)

from chatbot.engine import NexSupportBot


console = Console()


def print_bot_message(content: str):
    md = Markdown(content or "")
    console.print(Panel(md, title="NexSupport", title_align="left",
                        border_style="bright_blue", padding=(1, 2)))


def print_user_message(content: str):
    console.print(f"[bold green]You:[/bold green] {content}")


def main():
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")

    if not api_key or api_key == "your-api-key-here":
        console.print("[bold red]ERROR:[/bold red] OPENROUTER_API_KEY not set in .env file.")
        console.print("Edit the [bold].env[/bold] file and add your OpenRouter API key.")
        sys.exit(1)

    console.print("[bold bright_blue]╔══════════════════════════════════════════════╗[/]")
    console.print("[bold bright_blue]║           NexSupport AI Assistant           ║[/]")
    console.print("[bold bright_blue]║     Customer Service & SME Support Bot     ║[/]")
    console.print(f"[bold bright_blue]║     Model: {model:<36s}║[/]")
    console.print("[bold bright_blue]╚══════════════════════════════════════════════╝[/]")
    console.print("[dim]Type [bold]'quit'[/bold], [bold]'exit'[/bold], or press Ctrl+C to end the session.[/dim]")
    console.print()

    def status_callback(msg: str):
        console.print(f"[bold yellow]⚠️  {msg}[/bold yellow]")

    bot = NexSupportBot(api_key=api_key, model=model, status_callback=status_callback)

    greeting = bot.get_greeting()
    print_bot_message(greeting)

    while True:
        try:
            user_input = Prompt.ask("[bold green]You")
        except (KeyboardInterrupt, EOFError):
            console.print()
            print_bot_message(bot.get_closing())
            sys.exit(0)

        if user_input.lower().strip() in ("quit", "exit", "bye", "goodbye"):
            print_bot_message(bot.get_closing())
            break

        if not user_input.strip():
            continue

        print_user_message(user_input)
        response = bot.chat(user_input)
        print_bot_message(response)


if __name__ == "__main__":
    main()
