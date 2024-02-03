import openai
from pydantic import BaseModel, Field
from typing import Type
import os
from langchain.tools import BaseTool

openai.api_key = os.environ.get("OPENAI_API_KEY")

def extract_till_information(user_input: str):
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

class ExtractTillInformationInput(BaseModel):
    user_input: str = Field(description="the user input")


class ExtractTillInformationTool(BaseTool):
    name = "extract_information"
    description = "use this to extract key information from user input and return result. Can only be amount and Till number or account number IN INTEGER TYPE"
    args_schema: Type[BaseModel] = ExtractTillInformationInput  

    def _run(self, user_input: str):
        return extract_till_information(user_input)

    def _arun(self, url: str):
        raise NotImplementedError(
            "Get_stock_performance does not support async"
        )
    
    
def extract_qr_code_information(user_input: str):
    prompt = f"""
    USER_INPUT: {user_input}
    ---
    Above is a user input about what he/she wants to accomplish; Your goal is to identify and extract information needed to generate a QR code:
    1. The merchant name. <required> NOTE: Ask user to provide one if not provided.
    2. The reference number. <optional> NOTE: Use invoice test when not provided.
    3. The amount to be included in the QR code. <required> NOTE: Ask user to enter amount if not provided 
    4. The transaction code (trx_code). <required> NOTE: BG: Pay Merchant (Buy Goods).
                                                         WA: Withdraw Cash at Agent Till.
                                                         PB: Paybill or Business number.
                                                         SM: Send Money(Mobile number)
                                                         SB: Sent to Business. Business".
    5. The credit party identifier (cpi). <required> NOTE: Can be a Mobile Number, Business Number, Agent Till, Paybill or Business number, or Merchant Buy Goods
    6. The size of the QR code. <optional> NOTE: use a default of "300" when not provided. Size of the QR code image in pixels.

    Example:
    user_input = "Generate a QR code for Test Merchant with reference number 123456 for an amount of 100.0"
    ANSWER = {
        "merchant_name": "Test Merchant",
        "ref_no": "123456",
        "amount": 100.0,
        "trx_code": "BG",
        "cpi": "373132",
        "size": "300"
    }

    If all info above is collected, return the dictionary with the extracted information, else return an empty dictionary.

    ANSWER
    """

    extract_info = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )

    return extract_info

class ExtractQrCodeInformationInput(BaseModel):
    user_input: str = Field(description="The user input")

class ExtractQrCodeInformationOutput(BaseModel):
    merchant_name: str = Field(description="Name of the Company/M-Pesa Merchant Name")
    ref_no: str = Field(description="Transaction Reference")
    amount: float = Field(description="The total amount for the sale/transaction")
    trx_code: str = Field(description="Transaction Type. Supported types: BG, WA, PB, SM, SB")
    cpi: str = Field(description="Credit Party Identifier. Can be a Mobile Number, Business Number, Agent Till, Paybill or Business number, or Merchant Buy Goods.")
    size: str = Field(description="Size of the QR code image in pixels. QR code image will always be a square image")

class ExtractQrCodeInformationTool(BaseTool):
    name = "extract_qr_code_information"
    description = "Use this to extract key information from user input for generating a QR code and return the result"
    args_schema: Type[BaseModel] = ExtractQrCodeInformationInput

    def _run(self, user_input: str):
        return extract_qr_code_information(user_input)