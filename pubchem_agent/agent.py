"""
PubChem Agent using LangGraph for natural language queries to PubChem database.
Supports multiple LLM providers: OpenAI, Google Gemini, and Anthropic Claude.
"""

import logging
from typing import Dict, List, Optional, TypedDict, Union
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .config import get_config_manager
from .tools import (
    search_compounds,
    get_compound_properties,
    get_compound_synonyms,
    get_compound_structure,
    get_compound_properties_detailed,
    convert_identifier,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PubChemState(TypedDict):
    """State for PubChem agent conversation."""

    messages: List[BaseMessage]
    tools_called: List[str]
    results: Dict[str, str]


class PubChemAgent:
    """A conversational agent for PubChem database queries using LangGraph.

    Supports multiple LLM providers:
    - OpenAI (gpt-3.5-turbo, gpt-4, gpt-4-turbo, etc.)
    - Google Gemini (gemini-pro, gemini-1.5-pro, etc.)
    - Anthropic Claude (claude-3-haiku, claude-3-sonnet, claude-3-opus, etc.)
    """

    def __init__(
        self, provider: str = None, model: str = None, config_path: str = None, **kwargs
    ):
        """Initialize the PubChem agent with configuration-based setup.

        Args:
            provider: Model provider ("openai", "gemini", "claude"). If None, uses config default.
            model: Specific model name. If None, uses config default for provider.
            config_path: Path to config.toml file. If None, searches for config file.
            **kwargs: Additional arguments passed to the model (override config settings)
        """
        self.config_manager = get_config_manager(config_path)

        # Determine provider
        self.provider = provider or self.config_manager.get_default_provider()

        # Get provider configuration
        self.provider_config = self.config_manager.get_provider_config(self.provider)

        # Override with kwargs if provided
        for key, value in kwargs.items():
            self.provider_config[key] = value

        # Override model if provided
        if model:
            self.provider_config["model"] = model

        self.tools = [
            search_compounds,
            get_compound_properties,
            get_compound_synonyms,
            get_compound_structure,
            get_compound_properties_detailed,
            convert_identifier,
        ]

        # Initialize the appropriate model based on provider
        self.llm = self._initialize_model()

        # Bind tools to model
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Create tool node for execution
        self.tool_node = ToolNode(self.tools)

        # Build the graph
        self.graph = self._build_graph()

    def _initialize_model(self) -> BaseChatModel:
        """Initialize the appropriate language model based on provider."""

        config = self.provider_config

        if self.provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                raise ImportError(
                    "OpenAI support requires: pip install langchain-openai"
                )

            # Check for API key
            if (
                not config.get("api_key")
                or config["api_key"] == "your_openai_api_key_here"
            ):
                raise ValueError(
                    "OpenAI API key not configured. Please set api_key in config.toml"
                )

            return ChatOpenAI(
                api_key=config["api_key"],
                model=config["model"],
                base_url=config.get("base_url"),
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_tokens", 1000),
                streaming=config.get("streaming", True),
                timeout=config.get("timeout", 30),
            )

        elif self.provider == "gemini":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError:
                raise ImportError(
                    "Gemini support requires: pip install langchain-google-genai"
                )

            # Check for API key
            if (
                not config.get("api_key")
                or config["api_key"] == "your_gemini_api_key_here"
            ):
                raise ValueError(
                    "Google API key not configured. Please set api_key in config.toml"
                )

            return ChatGoogleGenerativeAI(
                google_api_key=config["api_key"],
                model=config["model"],
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_tokens", 1000),
                streaming=config.get("streaming", True),
            )

        elif self.provider == "claude":
            try:
                from langchain_anthropic import ChatAnthropic
            except ImportError:
                raise ImportError(
                    "Claude support requires: pip install langchain-anthropic"
                )

            # Check for API key
            if (
                not config.get("api_key")
                or config["api_key"] == "your_anthropic_api_key_here"
            ):
                raise ValueError(
                    "Anthropic API key not configured. Please set api_key in config.toml"
                )

            return ChatAnthropic(
                anthropic_api_key=config["api_key"],
                model=config["model"],
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_tokens", 1000),
                streaming=config.get("streaming", True),
            )

        else:
            raise ValueError(
                f"Unsupported provider: {self.provider}. "
                "Supported providers: 'openai', 'gemini', 'claude'"
            )

    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Define the graph
        workflow = StateGraph(PubChemState)

        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self._call_tools)

        # Set entry point
        workflow.set_entry_point("agent")

        # Add conditional edges
        workflow.add_conditional_edges(
            "agent", self._should_continue, {"continue": "tools", "end": END}
        )

        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def _call_model(self, state: PubChemState) -> PubChemState:
        """Call the language model with current state."""
        try:
            messages = state.get("messages", [])

            # Add system message if first call
            if not messages or not any(
                isinstance(msg, SystemMessage) for msg in messages
            ):
                system_msg = SystemMessage(
                    content=f"""You are a helpful chemical information assistant with access to PubChem database tools.
                
You can help users by:
- Searching for chemical compounds by name, CID, SMILES, InChI, or molecular formula
- Getting molecular properties like molecular weight, XLogP, TPSA
- Finding synonyms and alternative names for compounds
- Retrieving structural information (SMILES, InChI, molecular formula)
- Converting between different chemical identifiers
- Providing detailed molecular descriptors and properties

Always use the available tools to get accurate, up-to-date information from PubChem.
Format your responses in a clear, helpful way for the user.

Current model: {self.provider} ({self.provider_config.get('model', 'default')})"""
                )
                messages = [system_msg] + messages

            # Call the model
            response = self.llm_with_tools.invoke(messages)

            # Return updated state
            return {**state, "messages": messages + [response]}

        except Exception as e:
            logger.error(f"Error in model call: {e}")
            error_msg = AIMessage(content=f"I encountered an error: {str(e)}")
            return {**state, "messages": state.get("messages", []) + [error_msg]}

    def _call_tools(self, state: PubChemState) -> PubChemState:
        """Execute tools using ToolNode."""
        try:
            # Get the messages from state
            messages = state.get("messages", [])

            # Create a temporary state for tool execution
            tool_state = {"messages": messages}

            # Use ToolNode to execute tools
            result = self.tool_node.invoke(tool_state)

            # Extract tool messages from result
            tool_messages = result.get("messages", [])

            # Update tools_called if needed
            tools_called = state.get("tools_called", [])
            for msg in tool_messages:
                if isinstance(msg, ToolMessage):
                    tools_called.append(msg.name if hasattr(msg, "name") else "unknown")

            return {
                **state,
                "messages": messages + tool_messages,
                "tools_called": tools_called,
            }

        except Exception as e:
            logger.error(f"Error in tool execution: {e}")
            error_msg = ToolMessage(
                content=f"Tool execution failed: {str(e)}", tool_call_id="error"
            )
            return {**state, "messages": state.get("messages", []) + [error_msg]}

    def _should_continue(self, state: PubChemState) -> str:
        """Determine whether to continue with tools or end."""
        try:
            messages = state.get("messages", [])
            if not messages:
                return "end"

            last_message = messages[-1]

            # Check if the last message has tool calls
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "continue"
            else:
                return "end"

        except Exception as e:
            logger.error(f"Error in should_continue: {e}")
            return "end"

    def query(self, user_input: str) -> str:
        """Process a user query and return response.

        Args:
            user_input: User's question or request

        Returns:
            String response from the agent
        """
        try:
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "tools_called": [],
                "results": {},
            }

            # Run the graph
            result = self.graph.invoke(initial_state)

            # Extract final response
            messages = result.get("messages", [])
            if messages:
                # Get the last AI message
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage):
                        return msg.content

            return "I apologize, but I couldn't generate a response."

        except Exception as e:
            logger.error(f"Error in query processing: {e}")
            return f"I encountered an error while processing your request: {str(e)}"

    def stream_query(self, user_input: str):
        """Stream the agent's response to a user query.

        Args:
            user_input: User's question or request

        Yields:
            Chunks of the response as they become available
        """
        try:
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "tools_called": [],
                "results": {},
            }

            # Stream the graph execution
            for chunk in self.graph.stream(initial_state):
                if "messages" in chunk:
                    for message in chunk["messages"]:
                        if isinstance(message, AIMessage):
                            yield message.content
                        elif isinstance(message, ToolMessage):
                            yield f"Tool executed: {message.name}"

        except Exception as e:
            logger.error(f"Error in stream query: {e}")
            yield f"Error: {str(e)}"

    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model configuration."""
        return {
            "provider": self.provider,
            "model": self.provider_config.get("model", "unknown"),
            "temperature": str(self.provider_config.get("temperature", "unknown")),
            "streaming": str(self.provider_config.get("streaming", "unknown")),
            "config_path": self.config_manager.config_path or "default",
        }

    def get_config(self) -> Dict[str, str]:
        """Get the current configuration."""
        return {
            "provider": self.provider,
            "config_path": self.config_manager.config_path or "default",
            "available_providers": self.config_manager.get_available_providers(),
            "default_provider": self.config_manager.get_default_provider(),
        }


def create_agent(
    provider: str = None, model: str = None, config_path: str = None, **kwargs
) -> PubChemAgent:
    """Create a new PubChem agent instance using configuration-based setup.

    Args:
        provider: Model provider ("openai", "gemini", "claude"). If None, uses config default.
        model: Specific model name. If None, uses config default for provider.
        config_path: Path to config.toml file. If None, searches for config file.
        **kwargs: Additional arguments passed to the model (override config settings)

    Returns:
        Configured PubChemAgent instance

    Examples:
        # Use default configuration
        agent = create_agent()

        # Override provider
        agent = create_agent(provider="gemini")

        # Override model
        agent = create_agent(provider="openai", model="gpt-4")

        # Use custom config file
        agent = create_agent(config_path="my_config.toml")

        # Override temperature
        agent = create_agent(temperature=0.5)
    """
    return PubChemAgent(
        provider=provider, model=model, config_path=config_path, **kwargs
    )
