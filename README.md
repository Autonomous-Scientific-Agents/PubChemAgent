# PubChemAgent

A modern LangChain application using LangGraph agents for natural language access to the PubChem database. PubChemAgent supports multiple AI providers (OpenAI, Google Gemini, and Anthropic Claude) with configuration-based setup for easy customization.

## Features

- **Natural Language Interface**: Ask questions about chemical compounds in plain English
- **Configuration-Based Setup**: Easy configuration with `config.toml` files
- **Multiple AI Providers**: Support for OpenAI, Google Gemini, and Anthropic Claude
- **Comprehensive Database**: Access to millions of chemical compounds from PubChem
- **Multiple Search Methods**: Search by name, CID, SMILES, InChI, molecular formula, and more
- **Rich Chemical Properties**: Get molecular weight, XLogP, TPSA, and many other properties
- **Structural Information**: Retrieve SMILES strings, InChI identifiers, and molecular formulas
- **Advanced Search**: Perform substructure and similarity searches
- **Identifier Conversion**: Convert between different chemical identifier formats
- **Multiple Interfaces**: CLI, web interface, and programmatic API

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/PubChemAgent.git
cd PubChemAgent

# Install the package
pip install -e .

# Or install with optional dependencies
pip install -e .[gemini,claude]
```

## Configuration

PubChemAgent uses a `config.toml` file for configuration. Create a configuration file in one of these locations:

1. Current directory: `./config.toml`
2. User home directory: `~/.pubchem_agent/config.toml`
3. User home directory: `~/config.toml`

### Create Sample Configuration

```bash
# Create a sample config file
pubchem-agent --create-config
```

This creates a `config.toml` file with the following structure:

```toml
[general]
default_provider = "openai"
temperature = 0.1
streaming = true
timeout = 30

[openai]
api_key = "your_openai_api_key_here"
model = "gpt-3.5-turbo"
base_url = "https://api.openai.com/v1"
temperature = 0.1
max_tokens = 1000
streaming = true

[gemini]
api_key = "your_gemini_api_key_here"
model = "gemini-pro"
temperature = 0.1
max_tokens = 1000
streaming = true

[claude]
api_key = "your_anthropic_api_key_here"
model = "claude-3-haiku-20240307"
temperature = 0.1
max_tokens = 1000
streaming = true

[pubchem]
base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
timeout = 10
max_retries = 3

[web]
port = 8501
host = "localhost"
page_title = "PubChemAgent"
page_icon = "🧪"

[logging]
level = "INFO"
file = ""
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### API Key Setup

PubChemAgent supports two methods for providing API keys:

1. **Configuration File (Recommended)**: Set API keys in `config.toml`
2. **Environment Variables (Fallback)**: Set environment variables if not provided in config

#### Method 1: Configuration File

Update the `api_key` values in your `config.toml` file:

```toml
[openai]
api_key = "sk-your-actual-openai-key"

[gemini]
api_key = "your-actual-gemini-key"

[claude]
api_key = "your-actual-anthropic-key"
```

#### Method 2: Environment Variables (Fallback)

If API keys are not set in the config file (or are set to placeholder values), PubChemAgent will automatically fall back to reading from environment variables:

```bash
# Set environment variables
export OPENAI_API_KEY="sk-your-actual-openai-key"
export GEMINI_API_KEY="your-actual-gemini-key"
export ANTHROPIC_API_KEY="your-actual-anthropic-key"
```

#### Priority Order

The system uses the following priority order for API keys:

1. **Config file values** (if not empty or placeholder)
2. **Environment variables** (fallback)
3. **Empty/placeholder values** (will show as unavailable)

#### Get API Keys

1. **OpenAI**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Google Gemini**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Anthropic Claude**: Get your API key from [Anthropic Console](https://console.anthropic.com/)

This hybrid approach provides maximum flexibility - you can use config files for development and environment variables for production deployments.

## Usage

### Command Line Interface

PubChemAgent features a modern, visually-enhanced CLI powered by the [Rich](https://github.com/Textualize/rich) library, providing:
- 🎨 **Beautiful formatted output** with colors and styling
- 📊 **Structured tables** for configuration and provider status  
- 🎯 **Progress indicators** for long-running queries
- ⚡ **Interactive prompts** with improved user experience
- 🔍 **Organized panels** for responses and error messages

```bash
# Interactive mode (uses default provider from config)
pubchem-agent

# Single query
pubchem-agent -q "What is the molecular weight of aspirin?"

# Use specific provider
pubchem-agent --provider gemini -q "Find information about caffeine"

# Use specific model
pubchem-agent --provider openai --model gpt-4 -q "Convert this SMILES to InChI: CC(=O)OC1=CC=CC=C1C(=O)O"

# Use custom config file
pubchem-agent --config my_config.toml

# Show examples
pubchem-agent --examples

# Show help
pubchem-agent --help
```

### Web Interface

```bash
# Start the Streamlit web interface
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501` to use the web interface.

### Programmatic Usage

```python
from pubchem_agent import create_agent

# Use default configuration
agent = create_agent()

# Use specific provider
agent = create_agent(provider="gemini")

# Use specific model
agent = create_agent(provider="openai", model="gpt-4")

# Use custom config file
agent = create_agent(config_path="my_config.toml")

# Override configuration parameters
agent = create_agent(provider="claude", temperature=0.5)

# Query the agent
response = agent.query("What is the molecular weight of caffeine?")
print(response)
```

## Supported AI Providers

### OpenAI Models
- `gpt-3.5-turbo` - Fast and economical
- `gpt-4` - Advanced reasoning capabilities
- `gpt-4-turbo` - Latest with enhanced capabilities

### Google Gemini Models
- `gemini-pro` - Recommended for most tasks
- `gemini-1.5-pro` - Advanced with larger context window

### Anthropic Claude Models
- `claude-3-haiku-20240307` - Fast responses
- `claude-3-sonnet-20240229` - Balanced performance
- `claude-3-opus-20240229` - Most capable

## Example Queries

- "What is the molecular weight of aspirin?"
- "Find information about caffeine"
- "Convert this SMILES to InChI: CC(=O)OC1=CC=CC=C1C(=O)O"
- "What are the synonyms for compound with CID 2244?"
- "Get the structure of ibuprofen"
- "What is the TPSA of morphine?"
- "Find compounds similar to benzene"
- "What is the molecular formula of vitamin C?"
- "Get detailed properties for acetaminophen"
- "Find the InChI for paracetamol"

## Available Tools

The agent has access to the following PubChem tools:

- **search_compounds**: Search for compounds by name, CID, SMILES, InChI, or formula
- **get_compound_properties**: Get basic molecular properties
- **get_compound_synonyms**: Find alternative names and synonyms
- **get_compound_structure**: Get structural information (SMILES, InChI, formula)
- **get_compound_properties_detailed**: Get detailed molecular descriptors
- **convert_identifier**: Convert between different chemical identifier formats

## Configuration Reference

### General Settings
- `default_provider`: Default AI provider to use ("openai", "gemini", "claude")
- `temperature`: Global temperature setting (0.0-2.0)
- `streaming`: Enable streaming responses
- `timeout`: API request timeout in seconds

### Provider-Specific Settings
Each provider section supports:
- `api_key`: API key for the provider
- `model`: Model to use
- `temperature`: Temperature for this provider (overrides global)
- `max_tokens`: Maximum tokens for responses
- `streaming`: Enable streaming for this provider

### PubChem Settings
- `base_url`: PubChem API base URL
- `timeout`: Request timeout for PubChem API calls
- `max_retries`: Maximum number of retries for failed requests

### Web Interface Settings
- `port`: Port for Streamlit web interface
- `host`: Host for web interface
- `page_title`: Title for web interface
- `page_icon`: Icon for web interface

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=pubchem_agent

# Run specific test
pytest tests/test_agent.py::test_basic_functionality
```

### Project Structure

```
PubChemAgent/
├── pubchem_agent/
│   ├── __init__.py
│   ├── agent.py          # Main agent implementation
│   ├── tools.py          # PubChem tools
│   ├── config.py         # Configuration management
│   └── cli.py            # Command line interface
├── tests/
│   ├── __init__.py
│   └── test_agent.py     # Agent tests
├── config.toml           # Sample configuration
├── streamlit_app.py      # Web interface
├── example.py            # Usage examples
├── pyproject.toml        # Package configuration
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [LangChain](https://langchain.com/) for the agent framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) for state management
- [PubChem](https://pubchem.ncbi.nlm.nih.gov/) for chemical data
- [Streamlit](https://streamlit.io/) for the web interface
- OpenAI, Google, and Anthropic for AI model APIs

## Support

For support, please:
1. Check the documentation above
2. Review example usage in `example.py`
3. Open an issue on GitHub
4. Use the `--help` flag for CLI options

## Changelog

### Version 0.1.0
- Initial release with configuration-based setup
- Support for OpenAI, Google Gemini, and Anthropic Claude
- CLI, web interface, and programmatic API
- Comprehensive PubChem database access
- Multi-provider support with easy switching 