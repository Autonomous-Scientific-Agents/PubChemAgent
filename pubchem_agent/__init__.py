"""
PubChemAgent - A modern LangChain application using LangGraph agents for natural language access to PubChem database.

This package provides tools and agents for interacting with the PubChem database using natural language queries.
"""

from .agent import PubChemAgent, create_agent
from .tools import PUBCHEM_TOOLS
from .config import get_config_manager, reload_config, ConfigManager

__version__ = "0.1.0"
__author__ = "PubChemAgent Contributors"
__email__ = "your-email@example.com"
__license__ = "MIT"

__all__ = [
    "PubChemAgent",
    "create_agent",
    "PUBCHEM_TOOLS",
    "get_config_manager",
    "reload_config",
    "ConfigManager",
]
