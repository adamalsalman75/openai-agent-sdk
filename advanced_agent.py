#!/usr/bin/env python3
"""
Advanced OpenAI Agent Example

This script demonstrates a more advanced implementation of an agent using the OpenAI Agent SDK.
It creates an agent that can respond to different types of queries with appropriate responses.
This version uses tools and agent capabilities more effectively.

Before running this script, make sure to:
1. Install the required packages: pip install -r requirements.txt
2. Set your OpenAI API key as an environment variable: export OPENAI_API_KEY=your-api-key
"""

import os
import asyncio
import sys
from typing import Dict, List, Tuple, Any

try:
    # Import the OpenAI Agents SDK
    from agents import Agent, Runner, Tool, function_tool
    from agents.run_context import RunContextWrapper
except ImportError:
    print("Error: Required packages not found. Please install them using:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Knowledge base for the agent
KNOWLEDGE_BASE = {
    "greeting": "Hello! I'm an advanced OpenAI agent. How can I help you today?",
    "weather": "I don't have real-time weather data, but I can help you find weather information.",
    "help": "I can help with greetings, weather queries, and general information. Just ask!",
    "default": "I'm not sure how to respond to that. Try asking about weather, or say hello!"
}

# Create a classifier agent
classifier_agent = Agent(
    name="Query Classifier",
    instructions="""You are a query classification assistant. 
    Your task is to analyze the user's query and classify it into the most appropriate category.

    You will be given:
    1. The user's query
    2. A list of available categories with descriptions

    Respond ONLY with the category name that best matches the query. 
    Do not include any explanations or additional text in your response.
    """
)

@function_tool(
    name_override="classify_query",
    description_override="Classifies a user query into one of the predefined categories: greeting, weather, help, or default."
)
async def classify_query_tool(context: RunContextWrapper[Any], query: str) -> str:
    """
    Classifies a user query into one of the predefined categories.

    Args:
        context: The run context wrapper
        query: The user's input query

    Returns:
        The category of the query: one of greeting, weather, help, or default
    """
    # Format the categories for the prompt
    categories_text = "\n".join([f"- {category}: {description}" for category, description in KNOWLEDGE_BASE.items()])

    # Create the classification prompt
    classification_prompt = f"""User query: "{query}"

Available categories:
{categories_text}

Classify this query into exactly one of the above categories. Respond with ONLY the category name."""

    # Run the classifier agent
    result = await Runner.run(classifier_agent, classification_prompt)

    # Get the classification result (should be just the category name)
    classification = result.final_output.strip().lower()

    # Ensure the classification is valid (fallback to default if not)
    if classification not in KNOWLEDGE_BASE:
        print(f"[DEBUG] Invalid classification '{classification}', falling back to 'default'")
        return "default"

    print(f"[DEBUG] Query classified as: {classification}")
    return classification

@function_tool(
    name_override="get_response_template",
    description_override="Gets the response template for a given query type from the knowledge base."
)
async def get_response_template_tool(context: RunContextWrapper[Any], query_type: str) -> str:
    """
    Gets the response template for a given query type from the knowledge base.

    Args:
        context: The run context wrapper
        query_type: The type of query (greeting, weather, help, or default)

    Returns:
        The response template from the knowledge base
    """
    if query_type not in KNOWLEDGE_BASE:
        print(f"[DEBUG] Invalid query type '{query_type}', falling back to 'default'")
        query_type = "default"

    response_template = KNOWLEDGE_BASE[query_type]
    print(f"[DEBUG] Using knowledge base response: {response_template}")
    return response_template

async def main():
    """Run the Advanced agent with interactive messaging."""
    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it with: export OPENAI_API_KEY=your-api-key")
        return

    print("Starting Advanced Agent...")
    print("Type 'exit' to quit the conversation.")

    # Create the main agent with tools
    agent = Agent(
        name="Advanced Assistant",
        instructions="""You are an advanced assistant that can handle different types of queries.

        You have access to tools that can:
        1. Classify the user's query into a category
        2. Get a response template based on the query category

        Your workflow should be:
        1. Use the classify_query tool to determine the type of query
        2. Use the get_response_template tool to get the appropriate response template
        3. Generate a helpful response that incorporates the template
        4. Ensure your response directly addresses the user's query

        Always be polite, helpful, and concise in your responses.
        """,
        tools=[classify_query_tool, get_response_template_tool]
    )

    # Interactive conversation loop
    while True:
        # Get user input
        user_input = input("\nYou: ")

        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nGoodbye! Thanks for chatting.")
            break

        try:
            # Run the agent with the user's message
            result = await Runner.run(agent, user_input)

            # Print the agent's response
            print(f"Agent: {result.final_output}")
        except Exception as e:
            print(f"Error: {e}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
