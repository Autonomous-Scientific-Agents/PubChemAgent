#!/usr/bin/env python3
"""
Command Line Interface for PubChemAgent
Supports configuration-based setup with config.toml files
Supports multiple model providers: OpenAI, Google Gemini, and Anthropic Claude
"""

import argparse
import os
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich.status import Status
from rich.columns import Columns
from rich.rule import Rule
from rich import box

from .agent import create_agent
from .config import get_config_manager

# Initialize rich console
console = Console()


def check_configuration(config_path: Optional[str] = None) -> bool:
    """Check if configuration is valid and has at least one provider configured."""
    try:
        config_manager = get_config_manager(config_path)
        available_providers = config_manager.get_available_providers()

        if not available_providers:
            error_panel = Panel(
                "[red]No providers configured with valid API keys[/red]\n\n"
                "Please configure at least one provider in config.toml:\n"
                "1. Create a config.toml file (see config.toml for example)\n"
                "2. Set the api_key for your desired provider:\n"
                "   • [blue]OpenAI[/blue]: Set openai.api_key\n"
                "   • [green]Google Gemini[/green]: Set gemini.api_key\n"
                "   • [purple]Anthropic Claude[/purple]: Set claude.api_key\n\n"
                f"Config file location: [dim]{config_manager.config_path or 'not found'}[/dim]",
                title="❌ Configuration Error",
                border_style="red",
            )
            console.print(error_panel)
            return False

        # Create a table for available providers
        provider_table = Table(title="Available Providers", box=box.ROUNDED)
        provider_table.add_column("Provider", style="cyan")
        provider_table.add_column("Status", justify="center")

        for provider in available_providers:
            status = "✅ [green]Ready[/green]"
            provider_table.add_row(provider.title(), status)

        console.print(provider_table)

        if config_manager.config_path:
            console.print(
                f"✅ Using config file: [blue]{config_manager.config_path}[/blue]"
            )
        return True

    except Exception as e:
        error_panel = Panel(
            f"[red]{str(e)}[/red]", title="❌ Configuration Error", border_style="red"
        )
        console.print(error_panel)
        return False


def single_query(
    query: str, provider: str = None, model: str = None, config_path: str = None
) -> None:
    """Execute a single query"""
    try:
        config_manager = get_config_manager(config_path)

        # Use provider from config if not specified
        if not provider:
            provider = config_manager.get_default_provider()

        # Get model from config if not specified
        if not model:
            provider_config = config_manager.get_provider_config(provider)
            model = provider_config.get("model")

        # Create query info panel
        query_panel = Panel(
            f"[bold blue]Query:[/bold blue] {query}\n"
            f"[bold green]Provider:[/bold green] {provider.title()}\n"
            f"[bold yellow]Model:[/bold yellow] {model}",
            title="🧪 PubChemAgent Query",
            border_style="blue",
        )
        console.print(query_panel)

        agent = create_agent(provider=provider, model=model, config_path=config_path)

        with Status("[bold green]Searching PubChem database...", spinner="dots"):
            response = agent.query(query)

        # Display response in a styled panel
        response_panel = Panel(
            response, title="📋 Response", border_style="green", padding=(1, 2)
        )
        console.print(response_panel)

    except Exception as e:
        error_panel = Panel(
            f"[red]{str(e)}[/red]", title="❌ Error", border_style="red"
        )
        console.print(error_panel)
        sys.exit(1)


def interactive_mode(
    provider: str = None, model: str = None, config_path: str = None
) -> None:
    """Interactive chat mode"""
    try:
        config_manager = get_config_manager(config_path)

        # Use provider from config if not specified
        if not provider:
            provider = config_manager.get_default_provider()

        # Get model from config if not specified
        if not model:
            provider_config = config_manager.get_provider_config(provider)
            model = provider_config.get("model")

        # Welcome header
        welcome_text = Text("PubChemAgent - Interactive Mode", style="bold blue")
        console.print(Panel(welcome_text, padding=(1, 2)))

        console.print(
            "[dim]Ask questions about chemical compounds in natural language.[/dim]"
        )
        console.print(f"[bold green]Provider:[/bold green] {provider.title()}")
        console.print(f"[bold yellow]Model:[/bold yellow] {model}")
        console.print("[dim]Type 'help' for examples, 'quit' to exit.[/dim]\n")

        agent = create_agent(provider=provider, model=model, config_path=config_path)

        # Show model info
        model_info = agent.get_model_info()
        console.print(
            f"✅ [green]Agent loaded successfully![/green] Model: [blue]{model_info['model']}[/blue]\n"
        )

        while True:
            try:
                query = Prompt.ask("\n[bold cyan]🧪[/bold cyan]", default="").strip()

                if not query:
                    continue

                if query.lower() in ["quit", "exit", "q"]:
                    console.print("[bold yellow]👋 Goodbye![/bold yellow]")
                    break

                if query.lower() == "help":
                    show_help()
                    continue

                if query.lower() == "config":
                    show_config(agent)
                    continue

                with Status("[bold green]Searching...", spinner="dots"):
                    response = agent.query(query)

                response_panel = Panel(
                    response, title="📋 Response", border_style="green", padding=(1, 1)
                )
                console.print(response_panel)

            except KeyboardInterrupt:
                console.print("\n[bold yellow]👋 Goodbye![/bold yellow]")
                break

    except Exception as e:
        error_panel = Panel(
            f"[red]{str(e)}[/red]", title="❌ Error", border_style="red"
        )
        console.print(error_panel)
        sys.exit(1)


def show_help() -> None:
    """Show help information with rich formatting"""
    examples = [
        "What is the molecular weight of aspirin?",
        "Find information about caffeine",
        "Convert the SMILES 'CC(=O)OC1=CC=CC=C1C(=O)O' to InChI",
        "What are the synonyms for compound with CID 2244?",
        "Get the structure of ibuprofen",
        "What is the TPSA of morphine?",
        "Find compounds similar to benzene",
        "What is the molecular formula of vitamin C?",
        "Get detailed properties for acetaminophen",
        "Find the InChI for paracetamol",
    ]

    # Create examples table
    examples_table = Table(title="📚 Example Queries", box=box.ROUNDED)
    examples_table.add_column("#", style="dim", width=3)
    examples_table.add_column("Query", style="cyan")

    for i, example in enumerate(examples, 1):
        examples_table.add_row(str(i), example)

    console.print(examples_table)

    # Commands panel
    commands_panel = Panel(
        "[bold blue]config[/bold blue] - Show current configuration\n"
        "[bold blue]help[/bold blue] - Show this help message\n"
        "[bold blue]quit[/bold blue] or [bold blue]exit[/bold blue] - Exit interactive mode",
        title="📋 Additional Commands",
        border_style="blue",
    )
    console.print(commands_panel)


def show_config(agent):
    """Show current configuration with rich formatting"""
    config = agent.get_config()
    model_info = agent.get_model_info()

    # Create configuration table
    config_table = Table(title="⚙️ Current Configuration", box=box.ROUNDED)
    config_table.add_column("Setting", style="cyan", width=20)
    config_table.add_column("Value", style="green")

    config_table.add_row("Provider", config["provider"])
    config_table.add_row("Model", model_info["model"])
    config_table.add_row("Temperature", str(model_info["temperature"]))
    config_table.add_row("Streaming", str(model_info["streaming"]))
    config_table.add_row("Config File", config["config_path"] or "Not found")
    config_table.add_row(
        "Available Providers", ", ".join(config["available_providers"])
    )
    config_table.add_row("Default Provider", config["default_provider"])

    console.print(config_table)


def show_examples(
    provider: str = None, model: str = None, config_path: str = None
) -> None:
    """Show example queries and their responses with rich formatting"""
    try:
        config_manager = get_config_manager(config_path)

        # Use provider from config if not specified
        if not provider:
            provider = config_manager.get_default_provider()

        # Get model from config if not specified
        if not model:
            provider_config = config_manager.get_provider_config(provider)
            model = provider_config.get("model")

        # Header
        header_panel = Panel(
            f"[bold blue]Provider:[/bold blue] {provider.title()}\n"
            f"[bold yellow]Model:[/bold yellow] {model}",
            title="🧪 PubChemAgent - Examples",
            border_style="blue",
        )
        console.print(header_panel)

        examples = [
            "What is the molecular weight of water?",
            "Find the SMILES for caffeine",
            "Get properties for aspirin",
        ]

        agent = create_agent(provider=provider, model=model, config_path=config_path)

        for i, query in enumerate(examples, 1):
            console.print(f"\n[bold cyan]{i}. Query:[/bold cyan] {query}")
            console.print(Rule(style="dim"))

            try:
                with Status(f"[bold green]Processing query {i}...", spinner="dots"):
                    response = agent.query(query)

                response_panel = Panel(
                    response,
                    title=f"Response {i}",
                    border_style="green",
                    padding=(1, 1),
                )
                console.print(response_panel)

            except Exception as e:
                error_panel = Panel(
                    f"[red]{str(e)}[/red]",
                    title=f"❌ Error in Query {i}",
                    border_style="red",
                )
                console.print(error_panel)

    except Exception as e:
        error_panel = Panel(
            f"[red]{str(e)}[/red]", title="❌ Error", border_style="red"
        )
        console.print(error_panel)
        sys.exit(1)


def create_sample_config(path: str = None) -> None:
    """Create a sample configuration file with rich feedback"""
    if not path:
        path = os.path.join(os.getcwd(), "config.toml")

    try:
        config_manager = get_config_manager()
        config_manager.create_sample_config(path)

        success_panel = Panel(
            f"[green]Sample configuration created at:[/green]\n[blue]{path}[/blue]\n\n"
            "[yellow]📝 Please edit the file and add your API keys[/yellow]",
            title="✅ Config Created",
            border_style="green",
        )
        console.print(success_panel)

    except Exception as e:
        error_panel = Panel(
            f"[red]{str(e)}[/red]", title="❌ Error Creating Config", border_style="red"
        )
        console.print(error_panel)
        sys.exit(1)


def main() -> None:
    """Main CLI function with rich help formatting"""
    parser = argparse.ArgumentParser(
        description="PubChemAgent - Natural Language Access to PubChem Database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pubchem-agent                                    # Interactive mode (uses config)
  pubchem-agent -q "molecular weight of aspirin"  # Single query
  pubchem-agent --provider gemini -q "find caffeine"
  pubchem-agent --config my_config.toml
  pubchem-agent --create-config                   # Create sample config
  pubchem-agent --examples

Configuration:
  PubChemAgent uses config.toml for configuration. The tool searches for config files in:
  1. Current directory (./config.toml)
  2. User home directory (~/.pubchem_agent/config.toml)
  3. User home directory (~/config.toml)
  4. Package directory

  API Key Priority (per provider):
  1. Values set in config.toml (if not empty/placeholder)
  2. Environment variables (OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY)
  3. Empty/unavailable (provider will be disabled)

Supported Providers:
  openai    - OpenAI GPT models (gpt-3.5-turbo, gpt-4, etc.)
  gemini    - Google Gemini models (gemini-pro, gemini-1.5-pro, etc.)
  claude    - Anthropic Claude models (claude-3-haiku, claude-3-sonnet, claude-3-opus)
        """,
    )

    parser.add_argument("-q", "--query", type=str, help="Single query to execute")

    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode"
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "gemini", "claude"],
        help="Model provider to use (overrides config default)",
    )

    parser.add_argument(
        "--model", type=str, help="Specific model to use (overrides config default)"
    )

    parser.add_argument(
        "--config", type=str, help="Path to configuration file (default: auto-detect)"
    )

    parser.add_argument(
        "--create-config",
        type=str,
        nargs="?",
        const="",
        help="Create a sample configuration file (optionally specify path)",
    )

    parser.add_argument(
        "--examples", action="store_true", help="Show example queries and responses"
    )

    parser.add_argument(
        "--help-queries", action="store_true", help="Show example queries"
    )

    args = parser.parse_args()

    # Handle config creation first (before checking configuration)
    if args.create_config is not None:
        create_sample_config(args.create_config if args.create_config else None)
        return

    # Check configuration
    if not check_configuration(args.config):
        tip_panel = Panel(
            "[yellow]💡 Tip: Use --create-config to create a sample configuration file[/yellow]",
            border_style="yellow",
        )
        console.print(tip_panel)
        sys.exit(1)

    # Handle different modes
    if args.help_queries:
        show_help()
    elif args.examples:
        show_examples(args.provider, args.model, args.config)
    elif args.query:
        single_query(args.query, args.provider, args.model, args.config)
    elif args.interactive or len(sys.argv) == 1:
        interactive_mode(args.provider, args.model, args.config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
