# Installation Guide

## Quick Start

1. **Install the package:**
```bash
pip install -e ".[all]"
```

2. **Set up environment:**
```bash
cp env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Test the installation:**
```bash
python example.py
```

## Installation Options

### Core Package Only
```bash
pip install -e .
```

### With Web Interface
```bash
pip install -e ".[web]"
```

### With Development Tools
```bash
pip install -e ".[dev]"
```

### All Features
```bash
pip install -e ".[all]"
```

## Usage

### Command Line
```bash
# Interactive mode
pubchem-agent

# Single query
pubchem-agent -q "What is the molecular weight of aspirin?"
```

### Web Interface
```bash
streamlit run streamlit_app.py
```

### Python API
```python
from pubchem_agent import create_agent

agent = create_agent()
response = agent.chat("Find information about caffeine")
print(response)
```

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test
python tests/test_agent.py

# Run with coverage
pytest tests/ --cov=pubchem_agent
```

## Development

```bash
# Format code
black pubchem_agent/
isort pubchem_agent/

# Type checking
mypy pubchem_agent/

# Linting
flake8 pubchem_agent/
```

## Troubleshooting

### Common Issues

1. **Missing OpenAI API Key**
   - Set `OPENAI_API_KEY` in `.env` file
   - Or export as environment variable

2. **Import Errors**
   - Make sure you installed in development mode: `pip install -e .`
   - Check that you're in the project root directory

3. **PubChem API Errors**
   - Check internet connection
   - Verify compound names/identifiers
   - Try different search terms

### Getting Help

- Check the example.py file for usage examples
- Run `pubchem-agent --help` for CLI options
- Look at the tests for more examples 