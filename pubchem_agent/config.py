"""
Configuration management for PubChemAgent.
Handles loading and validation of config.toml files.
"""

import os
import toml
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging


class ConfigManager:
    """Manages configuration loading and validation for PubChemAgent."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager.

        Args:
            config_path: Path to the config.toml file. If None, searches for config files.
        """
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        self._apply_env_fallbacks()
        self._validate_config()

    def _find_config_file(self) -> Optional[str]:
        """Find the configuration file in common locations."""
        # Search locations in order of priority
        search_paths = [
            os.path.join(os.getcwd(), "config.toml"),
            os.path.join(os.path.expanduser("~"), ".pubchem_agent", "config.toml"),
            os.path.join(os.path.expanduser("~"), "config.toml"),
            os.path.join(Path(__file__).parent.parent, "config.toml"),
        ]

        for path in search_paths:
            if os.path.exists(path):
                return path

        return None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        if not self.config_path:
            # Return default configuration
            return self._get_default_config()

        try:
            with open(self.config_path, "r") as f:
                config = toml.load(f)
            return config
        except Exception as e:
            logging.warning(f"Failed to load config from {self.config_path}: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when no config file is found."""
        return {
            "general": {
                "default_provider": "openai",
                "temperature": 0.1,
                "streaming": True,
                "timeout": 30,
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "model": "gpt-3.5-turbo",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.1,
                "max_tokens": 1000,
                "streaming": True,
            },
            "gemini": {
                "api_key": os.getenv("GEMINI_API_KEY", ""),
                "model": "gemini-pro",
                "temperature": 0.1,
                "max_tokens": 1000,
                "streaming": True,
            },
            "claude": {
                "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                "model": "claude-3-haiku-20240307",
                "temperature": 0.1,
                "max_tokens": 1000,
                "streaming": True,
            },
            "pubchem": {
                "base_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug",
                "timeout": 10,
                "max_retries": 3,
            },
            "web": {
                "port": 8501,
                "host": "localhost",
                "page_title": "PubChemAgent",
                "page_icon": "🧪",
            },
            "logging": {
                "level": "INFO",
                "file": "",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

    def _apply_env_fallbacks(self) -> None:
        """Apply environment variable fallbacks for API keys."""
        # Define placeholder values that should trigger fallback to env vars
        placeholder_values = [
            "",
            "your_openai_api_key_here",
            "your_gemini_api_key_here",
            "your_anthropic_api_key_here",
        ]

        # Environment variable mappings
        env_mappings = {
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
        }

        for provider, env_var in env_mappings.items():
            if provider in self.config:
                current_key = self.config[provider].get("api_key", "")

                # If the current key is empty or a placeholder, try environment variable
                if current_key in placeholder_values:
                    env_key = os.getenv(env_var, "")
                    if env_key:
                        self.config[provider]["api_key"] = env_key
                        logging.info(
                            f"Using {env_var} environment variable for {provider} API key"
                        )

    def _validate_config(self) -> None:
        """Validate the loaded configuration."""
        # Check required sections
        required_sections = ["general", "openai", "gemini", "claude", "pubchem"]
        for section in required_sections:
            if section not in self.config:
                self.config[section] = self._get_default_config()[section]

        # Validate temperature values
        for provider in ["openai", "gemini", "claude"]:
            if provider in self.config:
                temp = self.config[provider].get("temperature", 0.1)
                if not (0.0 <= temp <= 2.0):
                    logging.warning(
                        f"Invalid temperature {temp} for {provider}, using 0.1"
                    )
                    self.config[provider]["temperature"] = 0.1

        # Validate general temperature
        general_temp = self.config["general"].get("temperature", 0.1)
        if not (0.0 <= general_temp <= 2.0):
            logging.warning(f"Invalid general temperature {general_temp}, using 0.1")
            self.config["general"]["temperature"] = 0.1

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider.

        Args:
            provider: The provider name (openai, gemini, claude)

        Returns:
            Configuration dictionary for the provider
        """
        if provider not in self.config:
            raise ValueError(f"Unknown provider: {provider}")

        provider_config = self.config[provider].copy()

        # Use general settings as defaults if not specified in provider config
        general_config = self.config.get("general", {})

        # Apply general defaults
        for key in ["temperature", "streaming", "timeout"]:
            if key not in provider_config and key in general_config:
                provider_config[key] = general_config[key]

        return provider_config

    def get_general_config(self) -> Dict[str, Any]:
        """Get general configuration."""
        return self.config.get("general", {})

    def get_pubchem_config(self) -> Dict[str, Any]:
        """Get PubChem API configuration."""
        return self.config.get("pubchem", {})

    def get_web_config(self) -> Dict[str, Any]:
        """Get web interface configuration."""
        return self.config.get("web", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config.get("logging", {})

    def get_available_providers(self) -> List[str]:
        """Get list of providers with valid API keys."""
        providers = []
        placeholder_values = [
            "",
            "your_openai_api_key_here",
            "your_gemini_api_key_here",
            "your_anthropic_api_key_here",
        ]

        for provider in ["openai", "gemini", "claude"]:
            config = self.get_provider_config(provider)
            api_key = config.get("api_key", "")
            if api_key and api_key not in placeholder_values:
                providers.append(provider)
        return providers

    def get_default_provider(self) -> str:
        """Get the default provider."""
        return self.config.get("general", {}).get("default_provider", "openai")

    def create_sample_config(self, path: str) -> None:
        """Create a sample configuration file.

        Args:
            path: Path where to create the config file
        """
        sample_config = {
            "general": {
                "default_provider": "openai",
                "temperature": 0.1,
                "streaming": True,
                "timeout": 30,
            },
            "openai": {
                "api_key": "your_openai_api_key_here",
                "model": "gpt-3.5-turbo",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.1,
                "max_tokens": 1000,
                "streaming": True,
            },
            "gemini": {
                "api_key": "your_gemini_api_key_here",
                "model": "gemini-pro",
                "temperature": 0.1,
                "max_tokens": 1000,
                "streaming": True,
            },
            "claude": {
                "api_key": "your_anthropic_api_key_here",
                "model": "claude-3-haiku-20240307",
                "temperature": 0.1,
                "max_tokens": 1000,
                "streaming": True,
            },
            "pubchem": {
                "base_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug",
                "timeout": 10,
                "max_retries": 3,
            },
            "web": {
                "port": 8501,
                "host": "localhost",
                "page_title": "PubChemAgent",
                "page_icon": "🧪",
            },
            "logging": {
                "level": "INFO",
                "file": "",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

        with open(path, "w") as f:
            toml.dump(sample_config, f)


# Global configuration instance
_config_manager = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None or config_path is not None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def reload_config(config_path: Optional[str] = None) -> ConfigManager:
    """Reload the configuration from file."""
    global _config_manager
    _config_manager = ConfigManager(config_path)
    return _config_manager
