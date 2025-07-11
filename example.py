#!/usr/bin/env python3
"""
Example usage of PubChemAgent with configuration-based setup.
Demonstrates how to use the agent with different providers and models.
"""

import os
from pubchem_agent import create_agent, get_config_manager


def check_configuration():
    """Check if configuration is properly set up."""
    config_manager = get_config_manager()

    print("Configuration Status:")
    print(f"Config file: {config_manager.config_path or 'default'}")
    print(f"Available providers: {config_manager.get_available_providers()}")
    print(f"Default provider: {config_manager.get_default_provider()}")
    print()

    return config_manager


def example_queries():
    """Example queries that demonstrate the agent's capabilities."""
    return [
        "What is the molecular weight of aspirin?",
        "Find the SMILES string for caffeine",
        "Convert this SMILES to InChI: CC(=O)OC1=CC=CC=C1C(=O)O",
        "What are the synonyms for compound with CID 2244?",
        "Get the structure of ibuprofen",
        "What is the TPSA of morphine?",
    ]


def demonstrate_basic_usage():
    """Demonstrate basic usage with default configuration."""
    print("=== Basic Usage (Default Configuration) ===")

    config_manager = check_configuration()

    # Check if we have any providers available
    available_providers = config_manager.get_available_providers()
    if not available_providers:
        print("❌ No providers configured with valid API keys")
        print("Please set up your config.toml file with API keys")
        return

    try:
        # Create agent with default configuration
        agent = create_agent()

        # Show model info
        model_info = agent.get_model_info()
        print(f"✅ Agent loaded successfully!")
        print(f"Provider: {model_info['provider']}")
        print(f"Model: {model_info['model']}")
        print(f"Temperature: {model_info['temperature']}")
        print()

        # Test query
        query = "What is the molecular weight of water?"
        print(f"Query: {query}")
        print("Response:", agent.query(query))

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50 + "\n")


def demonstrate_provider_override():
    """Demonstrate usage with provider override."""
    print("=== Provider Override ===")

    config_manager = check_configuration()
    available_providers = config_manager.get_available_providers()

    if not available_providers:
        print("❌ No providers configured")
        return

    for provider in available_providers:
        print(f"\n--- Testing {provider.upper()} ---")

        try:
            # Create agent with specific provider
            agent = create_agent(provider=provider)

            # Show model info
            model_info = agent.get_model_info()
            print(f"✅ {provider.title()} agent loaded successfully!")
            print(f"Model: {model_info['model']}")
            print(f"Temperature: {model_info['temperature']}")

            # Test query
            query = "What is caffeine?"
            print(f"Query: {query}")
            response = agent.query(query)
            print(f"Response: {response[:100]}..." if len(response) > 100 else response)

        except Exception as e:
            print(f"❌ Error with {provider}: {e}")

    print("\n" + "=" * 50 + "\n")


def demonstrate_model_override():
    """Demonstrate usage with model override."""
    print("=== Model Override ===")

    config_manager = check_configuration()
    available_providers = config_manager.get_available_providers()

    if "openai" in available_providers:
        print("--- Testing OpenAI with different models ---")

        models = ["gpt-3.5-turbo", "gpt-4"]

        for model in models:
            print(f"\nTesting {model}:")

            try:
                # Create agent with specific model
                agent = create_agent(provider="openai", model=model)

                # Show model info
                model_info = agent.get_model_info()
                print(f"✅ Agent loaded with {model}")
                print(f"Actual model: {model_info['model']}")

                # Test query
                query = "What is the molecular formula of aspirin?"
                print(f"Query: {query}")
                response = agent.query(query)
                print(
                    f"Response: {response[:100]}..."
                    if len(response) > 100
                    else response
                )

            except Exception as e:
                print(f"❌ Error with {model}: {e}")

    print("\n" + "=" * 50 + "\n")


def demonstrate_configuration_override():
    """Demonstrate usage with configuration parameter override."""
    print("=== Configuration Override ===")

    config_manager = check_configuration()
    available_providers = config_manager.get_available_providers()

    if not available_providers:
        print("❌ No providers configured")
        return

    provider = available_providers[0]
    print(f"--- Testing {provider.upper()} with custom temperature ---")

    try:
        # Create agent with custom temperature
        agent = create_agent(provider=provider, temperature=0.7)

        # Show model info
        model_info = agent.get_model_info()
        print(f"✅ Agent loaded with custom temperature")
        print(f"Provider: {model_info['provider']}")
        print(f"Model: {model_info['model']}")
        print(f"Temperature: {model_info['temperature']}")

        # Test query
        query = "Tell me about benzene"
        print(f"Query: {query}")
        response = agent.query(query)
        print(f"Response: {response[:150]}..." if len(response) > 150 else response)

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50 + "\n")


def demonstrate_config_file():
    """Demonstrate usage with custom config file."""
    print("=== Custom Config File ===")

    # Create a temporary config file
    temp_config = """
[general]
default_provider = "openai"
temperature = 0.2

[openai]
api_key = "sk-test-key-placeholder"
model = "gpt-3.5-turbo"
temperature = 0.2
"""

    temp_config_path = "temp_config.toml"

    try:
        with open(temp_config_path, "w") as f:
            f.write(temp_config)

        # Create config manager with custom file
        config_manager = get_config_manager(temp_config_path)

        print(f"✅ Custom config loaded from: {temp_config_path}")
        print(f"Default provider: {config_manager.get_default_provider()}")
        print(
            f"General temperature: {config_manager.get_general_config().get('temperature')}"
        )

        # Show provider config
        if "openai" in config_manager.config:
            openai_config = config_manager.get_provider_config("openai")
            print(f"OpenAI model: {openai_config.get('model')}")
            print(f"OpenAI temperature: {openai_config.get('temperature')}")

    except Exception as e:
        print(f"❌ Error with custom config: {e}")

    finally:
        # Clean up
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)

    print("\n" + "=" * 50 + "\n")


def demonstrate_env_fallback():
    """Demonstrate environment variable fallback for API keys."""
    print("=== Environment Variable Fallback ===")

    # Create a temporary config file with placeholder API keys
    temp_config = """
[general]
default_provider = "openai"
temperature = 0.2

[openai]
api_key = "your_openai_api_key_here"
model = "gpt-3.5-turbo"

[gemini]
api_key = ""
model = "gemini-pro"

[claude]
api_key = "your_anthropic_api_key_here"
model = "claude-3-haiku-20240307"
"""

    temp_config_path = "temp_env_fallback_config.toml"

    try:
        # Save original environment variables
        original_openai_key = os.environ.get("OPENAI_API_KEY")
        original_gemini_key = os.environ.get("GEMINI_API_KEY")

        # Set test environment variables
        os.environ["OPENAI_API_KEY"] = "env-openai-key-example"
        os.environ["GEMINI_API_KEY"] = "env-gemini-key-example"

        with open(temp_config_path, "w") as f:
            f.write(temp_config)

        # Create config manager with fallback behavior
        config_manager = get_config_manager(temp_config_path)

        print(f"✅ Config loaded from: {temp_config_path}")
        print("✅ Testing environment variable fallback:")

        # Show fallback behavior for each provider
        providers = ["openai", "gemini", "claude"]
        for provider in providers:
            provider_config = config_manager.get_provider_config(provider)
            api_key = provider_config.get("api_key", "")

            if api_key.startswith("env-"):
                print(f"  ✅ {provider}: Using environment variable fallback")
            elif api_key in [
                "",
                "your_openai_api_key_here",
                "your_gemini_api_key_here",
                "your_anthropic_api_key_here",
            ]:
                print(f"  ⚠️  {provider}: No API key available (placeholder/empty)")
            else:
                print(f"  ✅ {provider}: Using config file value")

        print(
            f"\nAvailable providers with valid keys: {config_manager.get_available_providers()}"
        )

    except Exception as e:
        print(f"❌ Error testing environment fallback: {e}")

    finally:
        # Restore original environment variables
        if original_openai_key is not None:
            os.environ["OPENAI_API_KEY"] = original_openai_key
        else:
            os.environ.pop("OPENAI_API_KEY", None)

        if original_gemini_key is not None:
            os.environ["GEMINI_API_KEY"] = original_gemini_key
        else:
            os.environ.pop("GEMINI_API_KEY", None)

        # Clean up
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)

    print("\n" + "=" * 50 + "\n")


def demonstrate_comprehensive_example():
    """Demonstrate comprehensive usage with multiple queries."""
    print("=== Comprehensive Example ===")

    config_manager = check_configuration()
    available_providers = config_manager.get_available_providers()

    if not available_providers:
        print("❌ No providers configured")
        return

    # Use the first available provider
    provider = available_providers[0]

    try:
        # Create agent
        agent = create_agent(provider=provider)

        # Show model info
        model_info = agent.get_model_info()
        print(f"✅ Agent loaded successfully!")
        print(f"Provider: {model_info['provider']}")
        print(f"Model: {model_info['model']}")
        print()

        # Run multiple queries
        queries = example_queries()

        for i, query in enumerate(queries, 1):
            print(f"{i}. Query: {query}")
            try:
                response = agent.query(query)
                print(
                    f"   Response: {response[:100]}..."
                    if len(response) > 100
                    else response
                )
            except Exception as e:
                print(f"   Error: {e}")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")

    print("=" * 50 + "\n")


def main():
    """Main function to run all examples."""
    print("PubChemAgent Configuration-Based Examples")
    print("=" * 50)
    print()

    # Check overall configuration
    config_manager = get_config_manager()

    if config_manager.config_path:
        print(f"✅ Using configuration file: {config_manager.config_path}")
    else:
        print("ℹ️ Using default configuration (with environment variables)")

    print(f"Available providers: {config_manager.get_available_providers()}")
    print(f"Default provider: {config_manager.get_default_provider()}")
    print()

    # Run demonstrations
    demonstrate_basic_usage()
    demonstrate_provider_override()
    demonstrate_model_override()
    demonstrate_configuration_override()
    demonstrate_config_file()
    demonstrate_env_fallback()
    demonstrate_comprehensive_example()

    print("🎉 All examples completed!")
    print("\nConfiguration Tips:")
    print("  1. API keys in config.toml take priority")
    print("  2. Environment variables are used as fallback")
    print("  3. Use --create-config to generate sample configuration")
    print("\nTo create a sample config file, run:")
    print("  pubchem-agent --create-config")
    print("\nTo run the CLI, use:")
    print("  pubchem-agent")
    print("\nTo run the web interface, use:")
    print("  streamlit run streamlit_app.py")


if __name__ == "__main__":
    main()
