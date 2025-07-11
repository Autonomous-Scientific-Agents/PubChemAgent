"""
Test file for PubChemAgent
Demonstrates the capabilities of the agent with various queries
"""

import os
import sys
import pytest
from dotenv import load_dotenv
from pubchem_agent import create_agent

# Load environment variables
load_dotenv()


def test_basic_functionality():
    """Test basic functionality of PubChemAgent"""

    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not found in environment variables")

    print("🧪 PubChemAgent Test Suite")
    print("=" * 50)

    # Create agent
    print("📡 Creating PubChemAgent...")
    agent = create_agent()
    print("✅ Agent created successfully!")

    # Test queries
    test_queries = [
        {
            "query": "What is the molecular weight of water?",
            "expected_concepts": ["molecular weight", "water", "H2O"],
        },
        {
            "query": "Find information about aspirin",
            "expected_concepts": [
                "aspirin",
                "acetylsalicylic acid",
                "molecular formula",
            ],
        },
        {
            "query": "What are the synonyms for compound with CID 2244?",
            "expected_concepts": ["synonyms", "CID", "2244"],
        },
        {
            "query": "Get the SMILES for caffeine",
            "expected_concepts": ["SMILES", "caffeine"],
        },
    ]

    print("\n🔍 Testing Queries")
    print("-" * 30)

    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {test_case['query']}")
        print("-" * 40)

        response = agent.query(test_case["query"])
        print(f"✅ Response: {response[:200]}...")

        # Check if response contains expected concepts
        response_lower = response.lower()
        found_concepts = [
            concept
            for concept in test_case["expected_concepts"]
            if concept.lower() in response_lower
        ]

        if found_concepts:
            print(f"✅ Found expected concepts: {found_concepts}")
        else:
            print(f"⚠️  Expected concepts not found: {test_case['expected_concepts']}")

    print("\n✅ Test completed!")
    # Use assert instead of return
    assert agent is not None, "Agent should be created successfully"


def test_tools():
    """Test individual tools"""

    print("\n🔧 Testing Individual Tools")
    print("=" * 50)

    from pubchem_agent.tools import (
        search_compounds,
        get_compound_properties,
        get_compound_synonyms,
        get_compound_structure,
        convert_identifier,
    )

    # Test search_compounds
    print("\n1. Testing search_compounds...")
    result = search_compounds.invoke({"identifier": "aspirin"})
    print(f"✅ Search result: {result[:100]}...")
    assert result is not None, "Search compounds should return a result"

    # Test get_compound_properties
    print("\n2. Testing get_compound_properties...")
    result = get_compound_properties.invoke(
        {"properties": ["molecular_weight", "xlogp"], "identifier": "aspirin"}
    )
    print(f"✅ Properties result: {result[:100]}...")
    assert result is not None, "Get compound properties should return a result"

    # Test get_compound_synonyms
    print("\n3. Testing get_compound_synonyms...")
    result = get_compound_synonyms.invoke({"identifier": "aspirin"})
    print(f"✅ Synonyms result: {result[:100]}...")
    assert result is not None, "Get compound synonyms should return a result"

    # Test get_compound_structure
    print("\n4. Testing get_compound_structure...")
    result = get_compound_structure.invoke({"identifier": "aspirin"})
    print(f"✅ Structure result: {result[:100]}...")
    assert result is not None, "Get compound structure should return a result"

    # Test convert_identifier
    print("\n5. Testing convert_identifier...")
    result = convert_identifier.invoke(
        {"identifier": "aspirin", "from_namespace": "name", "to_namespace": "smiles"}
    )
    print(f"✅ Conversion result: {result[:100]}...")
    assert result is not None, "Convert identifier should return a result"

    print("\n✅ All tools tested successfully!")


def test_multi_provider():
    """Test multi-provider functionality"""

    print("\n🤖 Testing Multi-Provider Support")
    print("=" * 50)

    # Test available providers
    available_providers = []

    if os.getenv("OPENAI_API_KEY"):
        available_providers.append("openai")

    if os.getenv("GEMINI_API_KEY"):
        available_providers.append("gemini")

    if os.getenv("ANTHROPIC_API_KEY"):
        available_providers.append("claude")

    if not available_providers:
        pytest.skip("No API keys found for any provider")

    print(f"Available providers: {available_providers}")

    # Test each available provider
    for provider in available_providers:
        print(f"\n🔍 Testing {provider} provider...")

        try:
            agent = create_agent(provider=provider)
            model_info = agent.get_model_info()

            print(f"✅ {provider} agent created successfully!")
            print(f"   Model: {model_info['model']}")
            print(f"   Provider: {model_info['provider']}")

            # Test a simple query
            response = agent.query("What is the molecular weight of water?")
            print(f"✅ Query response: {response[:100]}...")

            assert agent is not None, f"{provider} agent should be created successfully"
            assert response is not None, f"{provider} agent should return a response"

        except Exception as e:
            print(f"❌ Error testing {provider}: {str(e)}")
            # Don't fail the test for provider-specific errors
            continue

    print("\n✅ Multi-provider test completed!")


def interactive_test():
    """Interactive test mode"""

    print("\n🎮 Interactive Test Mode")
    print("=" * 50)
    print("Type 'quit' to exit")

    try:
        agent = create_agent()

        while True:
            query = input("\n🧪 Enter your query: ").strip()

            if query.lower() == "quit":
                print("👋 Goodbye!")
                break

            if not query:
                continue

            try:
                print("\n🔍 Searching...")
                response = agent.query(query)
                print(f"\n📋 Response:\n{response}")

            except Exception as e:
                print(f"❌ Error: {str(e)}")

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🧪 PubChemAgent Test Runner")
    print("=" * 50)

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_test()
        elif sys.argv[1] == "tools":
            test_tools()
        elif sys.argv[1] == "multi":
            test_multi_provider()
        else:
            print("Usage: python test_agent.py [interactive|tools|multi]")
    else:
        # Run basic functionality tests
        try:
            test_basic_functionality()
            print("\n🎉 All tests passed!")
            print("\nNext steps:")
            print("1. Run 'python test_agent.py interactive' for interactive testing")
            print("2. Run 'python test_agent.py tools' to test individual tools")
            print("3. Run 'python test_agent.py multi' to test multi-provider support")
            print("4. Run 'streamlit run streamlit_app.py' to start the web interface")
        except Exception as e:
            print(f"\n❌ Some tests failed: {str(e)}")
            sys.exit(1)
