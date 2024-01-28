import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from agent_tools import ExtractInformationTool
from tools import PaymentTillTool

load_dotenv()

# Initialize ChatOpenAI with the specified model
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

# Define the system message
system_message = SystemMessage(
    content="""
    "Welcome to the MPesa Customer Assistant!",
    "As a helpful assistant for MPesa, you play a crucial role in facilitating mobile money transactions.",
    "Your main tasks include assisting users in various transaction scenarios:",
    "- Businesses sending money to individuals",
    "- Individuals sending money to businesses",
    "- Businesses conducting transactions with other businesses",
    "Your goal is to interpret user input, understand their intentions, and categorize them to streamline the payment process.",
    "You are capable of initiating transactions and making payments to provided account numbers or till numbers with specified amounts.",
    "For instance, if a user inputs: 'pay 1000 shillings to 174379',",
    "you will utilize the ExtractInformationTool to gather key details needed for the PaymentTillTool.",
    "In this example, you will initiate payment 1000 with shortcode 174379 to complete the transaction.",
    "In case of any issues during a transaction, please specify the tool that encountered the problem."
    """
)

# Define the tools and agent settings
tools = [ExtractInformationTool(), PaymentTillTool()]
agent_kwargs = {
    "extra_prompt_message": [MessagesPlaceholder(variable_name="memory")],
    "system_message": system_message,
}

memory = ConversationSummaryBufferMemory(
    memory_key="memory",
    return_messages=True,
    llm=llm,
    max_token_limit=250,
)

# Create the agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory,
)

# Memory structure to maintain
conversation_memory = []

# Continuous conversation loop
while True:
    user_input = input("User: ")
    if user_input.lower() == "end":
        print("Thank you for using the MPesa Customer Assistant! If you have any further questions or need assistance in the future, feel free to ask. Have a great day!")
        break

    # Input the user message into the agent
    agent_response = agent({"input": user_input, "memory": conversation_memory})
    assistant_messages = agent_response.get("choices", [])

    # Update memory with assistant messages
    if assistant_messages:
        assistant_memory_messages = assistant_messages[0].get("message", {}).get("messages", [])
        conversation_memory.extend(assistant_memory_messages)

    # Print the assistant's response content
    print("Assistant:", agent_response.get("message", {}).get("content", "No response from the assistant."))
