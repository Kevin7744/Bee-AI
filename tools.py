# Import the necessary packages
import os
from dotenv import load_dotenv, find_dotenv
import openai

from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from pydantic import BaseModel, Field
from main import extract_payment_details

load_dotenv(find_dotenv())
openai.api_key = os.environ.get("OPENAI_API_KEY")
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")


# Take user input

# Extract information from text 

# Call the necessary functions to initiate transaction

# Return output/response

