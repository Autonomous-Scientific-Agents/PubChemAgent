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

from .agent import create_agent
from .config import get_config_manager


def check_configuration(config_path: Optional[str] = None) -> bool:
    """Check if configuration is valid and has at least one provider configured."""
    try:
        config_manager = get_config_manager(config_path)
        available_providers = config_manager.get_available_providers()

        if not available_providers:
            print("❌ No providers configured with valid API keys")
            print("\nPlease configure at least one provider in config.toml:")
            print("1. Create a config.toml file (see config.toml for example)")
            print("2. Set the api_key for your desired provider:")
            print("   - OpenAI: Set openai.api_key")
            print("   - Google Gemini: Set gemini.api_key")
            print("   - Anthropic Claude: Set claude.api_key")
            print(
                f"\nConfig file location: {config_manager.config_path or 'not found'}"
            )
            return False

        print(f"✅ Available providers: {', '.join(available_providers)}")
        if config_manager.config_path:
            print(f"✅ Using config file: {config_manager.config_path}")
        return True

    except Exception as e:
        print(f"❌ Configuration error: {e}")
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

        print(f"🧪 Query: {query}")
        print(f"🤖 Using: {provider.title()} {model}")
        print("🔍 Searching PubChem database...")

        agent = create_agent(provider=provider, model=model, config_path=config_path)
        response = agent.query(query)

        print("\n📋 Response:")
        print("-" * 50)
        print(response)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
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

        print("🧪 PubChemAgent - Interactive Mode")
        print("=" * 50)
        print("Ask questions about chemical compounds in natural language.")
        print(f"🤖 Using: {provider.title()} {model}")
        print("Type 'help' for examples, 'quit' to exit.")
        print()

        agent = create_agent(provider=provider, model=model, config_path=config_path)

        # Show model info
        model_info = agent.get_model_info()
        print(f"✅ Agent loaded successfully! Model: {model_info['model']}")

        while True:
            try:
                query = input("\n🧪 > ").strip()

                if not query:
                    continue

                if query.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if query.lower() == "help":
                    show_help()
                    continue

                if query.lower() == "config":
                    show_config(agent)
                    continue

                print("🔍 Searching...")
                response = agent.query(query)
                print(f"\n📋 {response}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def show_help() -> None:
    """Show help information"""
    print("\n📚 Help - Example Queries:")
    print("-" * 30)
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

    for i, example in enumerate(examples, 1):
        print(f"{i:2d}. {example}")

    print("\n📋 Additional Commands:")
    print("- 'config' - Show current configuration")
    print("- 'help' - Show this help message")
    print("- 'quit' or 'exit' - Exit interactive mode")


def show_config(agent):
    """Show current configuration"""
    print("\n⚙️ Current Configuration:")
    print("-" * 30)

    config = agent.get_config()
    model_info = agent.get_model_info()

    print(f"Provider: {config['provider']}")
    print(f"Model: {model_info['model']}")
    print(f"Temperature: {model_info['temperature']}")
    print(f"Streaming: {model_info['streaming']}")
    print(f"Config file: {config['config_path']}")
    print(f"Available providers: {', '.join(config['available_providers'])}")
    print(f"Default provider: {config['default_provider']}")


def show_examples(
    provider: str = None, model: str = None, config_path: str = None
) -> None:
    """Show example queries and their responses"""
    try:
        config_manager = get_config_manager(config_path)

        # Use provider from config if not specified
        if not provider:
            provider = config_manager.get_default_provider()

        # Get model from config if not specified
        if not model:
            provider_config = config_manager.get_provider_config(provider)
            model = provider_config.get("model")

        print("🧪 PubChemAgent - Examples")
        print("=" * 50)
        print(f"🤖 Using: {provider.title()} {model}")

        examples = [
            "What is the molecular weight of water?",
            "Find the SMILES for caffeine",
            "Get properties for aspirin",
        ]

        agent = create_agent(provider=provider, model=model, config_path=config_path)

        for i, query in enumerate(examples, 1):
            print(f"\n{i}. Query: {query}")
            print("-" * 40)

            try:
                response = agent.query(query)
                print(f"Response: {response}")

            except Exception as e:
                print(f"Error: {str(e)}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def create_sample_config(path: str = None) -> None:
    """Create a sample configuration file"""
    if not path:
        path = os.path.join(os.getcwd(), "config.toml")

    try:
        config_manager = get_config_manager()
        config_manager.create_sample_config(path)
        print(f"✅ Sample configuration created at: {path}")
        print("📝 Please edit the file and add your API keys")

    except Exception as e:
        print(f"❌ Error creating config file: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI function"""
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
        print("\n💡 Tip: Use --create-config to create a sample configuration file")
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
