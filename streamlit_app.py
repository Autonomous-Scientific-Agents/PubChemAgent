"""
Streamlit Web Application for PubChemAgent
Supports configuration-based setup with config.toml files
Supports multiple model providers: OpenAI, Google Gemini, and Anthropic Claude
"""

import streamlit as st
import os
from typing import Dict, Any, Optional
import json
from pubchem_agent import create_agent, get_config_manager


# Configure the page
st.set_page_config(
    page_title="PubChemAgent",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_config():
    """Get configuration manager and handle errors."""
    try:
        return get_config_manager()
    except Exception as e:
        st.error(f"Configuration error: {e}")
        return None


def check_available_providers(config_manager):
    """Check which providers have valid API keys configured."""
    if not config_manager:
        return {}

    available_providers = {}
    for provider in ["openai", "gemini", "claude"]:
        try:
            provider_config = config_manager.get_provider_config(provider)
            if provider_config.get("api_key") and provider_config["api_key"] not in [
                "",
                "your_openai_api_key_here",
                "your_gemini_api_key_here",
                "your_anthropic_api_key_here",
            ]:
                available_providers[provider] = provider.title()
        except Exception:
            continue

    return available_providers


def get_model_options(provider: str) -> Dict[str, str]:
    """Get available model options for each provider."""
    models = {
        "openai": {
            "gpt-3.5-turbo": "GPT-3.5 Turbo (Fast & Economical)",
            "gpt-4": "GPT-4 (Advanced)",
            "gpt-4-turbo": "GPT-4 Turbo (Latest)",
        },
        "gemini": {
            "gemini-pro": "Gemini Pro (Recommended)",
            "gemini-1.5-pro": "Gemini 1.5 Pro (Advanced)",
        },
        "claude": {
            "claude-3-haiku-20240307": "Claude 3 Haiku (Fast)",
            "claude-3-sonnet-20240229": "Claude 3 Sonnet (Balanced)",
            "claude-3-opus-20240229": "Claude 3 Opus (Most Capable)",
        },
    }
    return models.get(provider, {})


@st.cache_resource
def load_agent(provider: str, model: str = None, config_path: str = None):
    """Load the PubChemAgent (cached for performance)"""
    return create_agent(provider=provider, model=model, config_path=config_path)


def main():
    """Main Streamlit application"""

    # Title and description
    st.title("🧪 PubChemAgent")
    st.markdown(
        """
    **Natural Language Access to PubChem Database**

    PubChemAgent is an AI-powered assistant that helps you search and retrieve chemical information from the PubChem database using natural language queries.
    Supports multiple AI providers: OpenAI, Google Gemini, and Anthropic Claude.
    """
    )

    # Get configuration
    config_manager = get_config()
    if not config_manager:
        st.stop()

    # Sidebar with configuration and information
    with st.sidebar:
        st.header("🤖 Model Configuration")

        # Show config file information
        if config_manager.config_path:
            st.success(
                f"✅ Using config: {os.path.basename(config_manager.config_path)}"
            )
        else:
            st.info("ℹ️ Using default configuration")

        # Check available providers
        available_providers = check_available_providers(config_manager)

        if not available_providers:
            st.error("❌ No providers configured with valid API keys")
            st.markdown(
                """
            **Configuration Required:**

            1. Create a `config.toml` file in your project directory
            2. Add your API keys:
            ```toml
            [openai]
            api_key = "your_openai_api_key_here"

            [gemini]
            api_key = "your_gemini_api_key_here"

            [claude]
            api_key = "your_anthropic_api_key_here"
            ```
            3. Restart the application

            **Or use the CLI to create a sample config:**
            ```bash
            pubchem-agent --create-config
            ```
            """
            )
            st.stop()

        # Provider selection
        provider_names = list(available_providers.keys())
        provider_labels = [available_providers[p] for p in provider_names]

        # Get default provider from config
        default_provider = config_manager.get_default_provider()
        default_index = 0
        if default_provider in provider_names:
            default_index = provider_names.index(default_provider)

        selected_provider_label = st.selectbox(
            "Select AI Provider",
            provider_labels,
            index=default_index,
            help="Choose which AI provider to use",
        )

        # Get the actual provider key
        selected_provider = provider_names[
            provider_labels.index(selected_provider_label)
        ]

        # Get provider config
        provider_config = config_manager.get_provider_config(selected_provider)

        # Model selection
        model_options = get_model_options(selected_provider)
        if model_options:
            model_keys = list(model_options.keys())
            model_labels = list(model_options.values())

            # Find default model from config
            default_model = provider_config.get("model", model_keys[0])
            default_model_index = 0
            if default_model in model_keys:
                default_model_index = model_keys.index(default_model)

            selected_model_label = st.selectbox(
                "Select Model",
                model_labels,
                index=default_model_index,
                help="Choose which specific model to use",
            )

            selected_model = model_keys[model_labels.index(selected_model_label)]
        else:
            selected_model = provider_config.get("model", "default")

        # Show current configuration
        st.markdown("**Current Configuration:**")
        st.markdown(f"- Provider: {selected_provider_label}")
        st.markdown(f"- Model: {selected_model}")
        st.markdown(f"- Temperature: {provider_config.get('temperature', 0.1)}")
        st.markdown(f"- Streaming: {provider_config.get('streaming', True)}")

        st.header("🔧 Agent Capabilities")
        st.markdown(
            """
        - **Search compounds** by name, CID, SMILES, InChI, or formula
        - **Get molecular properties** (molecular weight, XLogP, TPSA, etc.)
        - **Retrieve structural information** (SMILES, InChI, molecular formula)
        - **Find synonyms** and alternative names
        - **Convert identifiers** between different formats
        - **Perform advanced searches** (substructure, similarity)
        """
        )

        st.header("📝 Example Queries")
        example_queries = [
            "What is the molecular weight of aspirin?",
            "Find information about caffeine",
            "Convert the SMILES 'CC(=O)OC1=CC=CC=C1C(=O)O' to InChI",
            "What are the synonyms for compound with CID 2244?",
            "Get the structure of ibuprofen",
            "What is the TPSA of morphine?",
            "Find compounds similar to benzene",
            "What is the molecular formula of vitamin C?",
        ]

        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}", use_container_width=True):
                st.session_state.example_query = query

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Check if we need to reload the agent due to provider/model change
    if (
        "agent" not in st.session_state
        or st.session_state.get("current_provider") != selected_provider
        or st.session_state.get("current_model") != selected_model
    ):

        with st.spinner(f"Loading {selected_provider_label} agent..."):
            try:
                st.session_state.agent = load_agent(selected_provider, selected_model)
                st.session_state.current_provider = selected_provider
                st.session_state.current_model = selected_model

                # Show model info
                model_info = st.session_state.agent.get_model_info()
                st.success(
                    f"✅ {selected_provider_label} agent loaded successfully! Model: {model_info['model']}"
                )

            except Exception as e:
                st.error(f"❌ Failed to load agent: {str(e)}")
                st.stop()

    # Handle example query
    if "example_query" in st.session_state:
        st.session_state.messages.append(
            {"role": "user", "content": st.session_state.example_query}
        )
        del st.session_state.example_query

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(
        "Ask about chemical compounds, properties, or structures..."
    ):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Searching PubChem database..."):
                try:
                    response = st.session_state.agent.query(prompt)
                    st.markdown(response)

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )

                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_message}
                    )

    # Footer with additional information
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔍 Search Types")
        st.markdown(
            """
        - **Name**: Common or IUPAC names
        - **CID**: PubChem Compound ID
        - **SMILES**: Simplified molecular input
        - **InChI**: International Chemical Identifier
        - **Formula**: Molecular formula
        """
        )

    with col2:
        st.markdown("### 📊 Available Properties")
        st.markdown(
            """
        - Molecular weight and formula
        - XLogP (partition coefficient)
        - TPSA (topological polar surface area)
        - Hydrogen bond donors/acceptors
        - Rotatable bonds
        - Complexity score
        """
        )

    with col3:
        st.markdown("### 🔬 Advanced Features")
        st.markdown(
            """
        - Substructure searches
        - Similarity searches
        - Identifier conversions
        - Synonym lookup
        - Structural information
        - 3D properties
        """
        )

    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


def show_tools_page():
    """Show available tools and their descriptions"""
    st.title("🔧 Available Tools")

    # Get configuration
    config_manager = get_config()
    if not config_manager:
        st.stop()

    # Get available providers
    available_providers = check_available_providers(config_manager)
    if not available_providers:
        st.error("❌ No providers configured with valid API keys")
        st.stop()

    # Use the first available provider for tool display
    provider = list(available_providers.keys())[0]

    if "tools_agent" not in st.session_state:
        st.session_state.tools_agent = load_agent(provider)

    # Show tools from the agent
    from pubchem_agent.tools import (
        search_compounds,
        get_compound_properties,
        get_compound_synonyms,
        get_compound_structure,
        get_compound_properties_detailed,
        convert_identifier,
    )

    tools = [
        search_compounds,
        get_compound_properties,
        get_compound_synonyms,
        get_compound_structure,
        get_compound_properties_detailed,
        convert_identifier,
    ]

    for tool in tools:
        with st.expander(f"🛠️ {tool.name}"):
            st.markdown(f"**Description:** {tool.description}")
            if hasattr(tool, "args"):
                st.markdown("**Arguments:**")
                for arg_name, arg_info in tool.args.items():
                    st.markdown(f"- `{arg_name}`: {arg_info}")


def show_about_page():
    """Show information about PubChemAgent"""
    st.title("ℹ️ About PubChemAgent")

    st.markdown(
        """
    ## What is PubChemAgent?

    PubChemAgent is an AI-powered assistant that provides natural language access to the PubChem database.
    It combines the power of Large Language Models with the comprehensive chemical information available in PubChem.

    ## Key Features

    - **Natural Language Interface**: Ask questions in plain English
    - **Configuration-Based Setup**: Easy configuration with config.toml files
    - **Multiple AI Providers**: Support for OpenAI, Google Gemini, and Anthropic Claude
    - **Comprehensive Database**: Access to millions of chemical compounds
    - **Multiple Search Methods**: Search by name, CID, SMILES, InChI, formula, and more
    - **Rich Chemical Properties**: Get molecular weight, XLogP, TPSA, and many other properties
    - **Structural Information**: Retrieve SMILES strings, InChI identifiers, and molecular formulas
    - **Advanced Search**: Perform substructure and similarity searches
    - **Identifier Conversion**: Convert between different chemical identifier formats

    ## Configuration

    PubChemAgent uses a `config.toml` file for configuration. The application searches for config files in:
    1. Current directory (`./config.toml`)
    2. User home directory (`~/.pubchem_agent/config.toml`)
    3. User home directory (`~/config.toml`)
    4. Package directory

    ### Sample Configuration:
    ```toml
    [general]
    default_provider = "openai"
    temperature = 0.1

    [openai]
    api_key = "your_openai_api_key_here"
    model = "gpt-3.5-turbo"

    [gemini]
    api_key = "your_gemini_api_key_here"
    model = "gemini-pro"

    [claude]
    api_key = "your_anthropic_api_key_here"
    model = "claude-3-haiku-20240307"
    ```

    ## Supported AI Providers

    ### OpenAI
    - GPT-3.5 Turbo (Fast & Economical)
    - GPT-4 (Advanced reasoning)
    - GPT-4 Turbo (Latest with enhanced capabilities)

    ### Google Gemini
    - Gemini Pro (Recommended for most tasks)
    - Gemini 1.5 Pro (Advanced with larger context)

    ### Anthropic Claude
    - Claude 3 Haiku (Fast responses)
    - Claude 3 Sonnet (Balanced performance)
    - Claude 3 Opus (Most capable)

    ## Technology Stack

    - **LangChain**: Framework for building AI applications
    - **LangGraph**: State machine for complex agent workflows
    - **Multiple LLMs**: OpenAI GPT, Google Gemini, Anthropic Claude
    - **Streamlit**: Web interface framework
    - **PubChemPy**: Python interface to PubChem
    - **TOML**: Configuration file format

    ## Getting Started

    1. Create a `config.toml` file with your API keys
    2. Select your preferred AI provider and model
    3. Start asking questions about chemical compounds

    ## CLI Usage

    ```bash
    # Create sample config
    pubchem-agent --create-config

    # Interactive mode
    pubchem-agent

    # Single query
    pubchem-agent -q "What is the molecular weight of aspirin?"

    # Use specific provider
    pubchem-agent --provider gemini -q "Find caffeine"
    ```

    ## Example Queries

    - "What is the molecular weight of aspirin?"
    - "Find information about caffeine"
    - "Convert this SMILES to InChI: CC(=O)OC1=CC=CC=C1C(=O)O"
    - "What are the synonyms for CID 2244?"
    - "Get the structure of ibuprofen"
    """
    )


# Navigation
if __name__ == "__main__":
    # Add navigation in the sidebar
    page = st.sidebar.selectbox("Navigate", ["🧪 Chat", "🔧 Tools", "ℹ️ About"], index=0)

    if page == "🧪 Chat":
        main()
    elif page == "🔧 Tools":
        show_tools_page()
    elif page == "ℹ️ About":
        show_about_page()
