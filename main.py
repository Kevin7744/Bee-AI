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
from agent_tools import extract_information


load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

system_message = SystemMessage(
    content="""
    You are a helpful customer assistant for a Mobile Money Service called "MPesa",
    which enables its user to send money in the following ways: 
                - businesses to individuals 
                - individuals to businesses
                - businesses to businesses
    Your goal is to handle all user input and try to capture their intentions and categorise them to facilitate a seamless process of payments.
    """
)

tools = [
    extract_information(),
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


test_input = """
Pay 1000 shillings to this till number 174379
"""
agent({"input": test_input})
