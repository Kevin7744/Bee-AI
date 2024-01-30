import openai
from pydantic import BaseModel, Field
from typing import Type
import os
from langchain.tools import BaseTool

openai.api_key = os.environ.get("OPENAI_API_KEY")

def extract_information(user_input: str):
    prompt = f"""
    USER_INPUT: {user_input}
    ---
    Above is a user input about what he/she wants to accomplish; Your goal is to identify and extract information needed to make a complete transaction:
    1. The amount the user wants to send.
    2. The account number or till number the user wants to send to.

    Example:
    user_input = "I want to pay 100 to this till number 174379"
    ANSWER = "amount: 100
              till number: 174379"
    user_input = "pay hundred shillings to this till number 174379"
    ANSWER = "amount: 100
              till number: 174379"

    If all info above is collected, return the amount and account number, else return NO; (RETURN ONLY THE 'AMOUNT' AND 'ACCOUNT' NUMBER IN INTEGER TYPE ELSE NO).

    ANSWER
    """

    extract_info = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},

        ]
    )
    extract_info_result = extract_info
    return extract_info_result

class ExtractInformationInput(BaseModel):
    user_input: str = Field(description="the user input")


class ExtractInformationTool(BaseTool):
    name = "extract_information"
    description = "use this to extract key information from user input and return result. Can only be amount and Till number or account number IN INTEGER TYPE"
    args_schema: Type[BaseModel] = ExtractInformationInput  

    def _run(self, user_input: str):
        return extract_information(user_input)

    def _arun(self, url: str):
        raise NotImplementedError(
            "Get_stock_performance does not support async"
        )
    
    
# class PaymentDetails(BaseModel):
#     amount: int
#     account_number: int

# payment: PaymentDetails = openai.chat.completions.create(
#     model="gpt-3.5-turbo",
#     response_model=PaymentDetails,
#     messages=[
#         {"role": "user", "content": "{user_input}"},
#     ]
# )