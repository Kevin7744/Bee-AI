# Import the necessary packages
import os
from dotenv import load_dotenv, find_dotenv
import openai

from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from agent_tools import ExtractInformationTool
from tools import PaymentTillTool


load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

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


tools = [
    ExtractInformationTool(),
    PaymentTillTool(),
]

agent_kwargs = {
    "extra_prompt_nessage": [MessagesPlaceholder(variable_name="memory")],
    "system_message": system_message,
}

memory = ConversationSummaryBufferMemory(
    memory_key="memory", return_messages=True, llm=llm, max_token_limit=250
)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory,
)


# Updated code with a function name without spaces
test_input = """
pay 1000 shillings to this till number 174379
"""
agent = agent({"input": test_input})


