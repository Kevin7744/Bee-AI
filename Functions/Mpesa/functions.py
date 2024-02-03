import re
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import base64
from dotenv import load_dotenv
from pydantic import BaseModel, Field, constr
from typing import Optional, Type
from langchain.tools import BaseTool

load_dotenv()


def get_access_token():
    consumer_key = "eiDkD79ICeFRE1FDiHgCbDMiOvXgp3cj"
    consumer_secret = "BfFwVt1uGLt7Mki3"
    access_token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)

    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status()
        result = response.json()
        access_token = result.get('access_token')
        return AccessTokenOutput(access_token=access_token, error_message=None)
    except requests.exceptions.RequestException as e:
        return AccessTokenOutput(access_token=None, error_message=str(e))


class AccessTokenOutput(BaseModel):
    access_token: Optional[str] = Field(description="Generated access token")
    error_message: Optional[str] = Field(description="Error message in case of failure")


class AccessTokenTool(BaseTool):
    name = "get_access_token"
    description = "Use this to generate an access token for authentication"

    def _run(self):
        return get_access_token()

class PaymentTillInput(BaseModel):
    amount: float = Field(description="The amount to be paid to the till or account number")
    business_short_code: str = Field(description="The till or account number to be paid to")
    party_a: str = Field(description="The phone number sending money")
    transaction_type: str = Field(description="Transaction type. Use 'CustomerPayBillOnline' for Paybill numbers or 'CustomerBuyGoodsOnline' for till.")
    account_reference: str = Field(description="Account reference for the transaction")

class PaymentTillOutput(BaseModel):
    checkout_request_id: Optional[str] = Field(description="ID for the initiated initiate payment push request")
    response_code: Optional[str] = Field(description="Response code from the initiate payment push request")
    error_message: Optional[str] = Field(description="Error message in case of failure")

def initiate_payment(amount: float, business_short_code: str, party_a: float, transaction_type: str, account_reference: str):
    # Calling the get_access_token method to obtain the access token
    access_token_response = get_access_token()

    if isinstance(access_token_response, AccessTokenOutput):
        access_token = access_token_response.access_token
        if access_token:
            # Rest of the code for STK push with the obtained access token
            process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            callback_url = 'http://yourcustomurl.local/'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
            password = base64.b64encode((str(business_short_code) + passkey + timestamp).encode()).decode()
            party_b = business_short_code
            transaction_desc = 'PaymentTill test'

            stk_push_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }

            stk_push_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': transaction_type,
                'Amount': amount,
                'PartyA': party_a,
                'PartyB': party_b,
                'PhoneNumber': party_a,
                'CallBackURL': callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }

            try:
                response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                response.raise_for_status()
                response_data = response.json()
                checkout_request_id = response_data.get('CheckoutRequestID')
                response_code = response_data.get('ResponseCode')

                if response_code == "0":
                    return PaymentTillOutput(checkout_request_id=checkout_request_id, response_code=response_code, error_message=None)
                else:
                    return PaymentTillOutput(checkout_request_id=None, response_code=None, error_message=f'STK push failed. Response Code: {response_code}')
            except requests.exceptions.RequestException as e:
                return PaymentTillOutput(checkout_request_id=None, response_code=None, error_message=f'Error: {str(e)}')
        else:
            return PaymentTillOutput(checkout_request_id=None, response_code=None, error_message='Access token not found.')
    else:
        return PaymentTillOutput(checkout_request_id=None, response_code=None, error_message='Failed to retrieve access token.')

class PaymentTillTool(BaseTool):
    name = "initiate_payment"
    description = "Use this to initiate a payment, takes in amount and till/account number as parameters"
    args_schema: Type[BaseModel] = PaymentTillInput

    def _run(self, amount: float, business_short_code: str, party_a: float, transaction_type: str, account_reference: str):
        return initiate_payment(amount, business_short_code, party_a, transaction_type, account_reference)


class QrCodeInput(BaseModel):
    merchant_name: str = Field(description="Name of the Company/M-Pesa Merchant Name")
    ref_no: str = Field(description="Transaction Reference")
    amount: float = Field(description="The total amount for the sale/transaction")
    trx_code: str = Field(description="Transaction Type", enum=["BG", "WA", "PB", "SM", "SB"])
    cpi: str = Field(description="Credit Party Identifier. Can be a Mobile Number, Business Number, Agent Till, Paybill or Business number, or Merchant Buy Goods")
    size: str = Field(description="Size of the QR code image in pixels. QR code image will always be a square image")

from pydantic import BaseModel, Field

class QrCodeOutput(BaseModel):
    response_code: str = Field(description="Used to return the Transaction Type")
    request_id: str = Field(description="An alpha-numeric string of fewer than 20 characters")
    response_description: str = Field(description="This is a response describing the status of the transaction")
    qr_code: str = Field(description="QR Code Image/Data/String")

def generate_dynamic_qr(data):
    access_token_response = get_access_token()
    if 'access_token' in access_token_response:
        access_token = access_token_response['access_token']
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        dynamic_qr_url = 'https://sandbox.safaricom.co.ke/mpesa/qrcode/v1/generate'
        response = requests.post(dynamic_qr_url, json=data, headers=headers)
        return response.json()
    else:
        return access_token_response

class QrCodeTool(BaseTool):
    name = "generate_dynamic_qr"
    description = "Tool for generating dynamic QR code"
    args_schema = QrCodeInput
    result_schema = QrCodeOutput

    def _run(self, data: QrCodeInput):
        return generate_dynamic_qr(data)



# def reverse_transaction():
#     try:
#         # Extract data from the request
#         data = request.json
#         initiator = data.get('Initiator')
#         security_credential = data.get('SecurityCredential')
#         command_id = data.get('CommandID')
#         transaction_id = data.get('TransactionID')
#         amount = data.get('Amount')
#         receiver_party = data.get('ReceiverParty')
#         receiver_identifier_type = data.get('ReceiverIdentifierType')
#         result_url = data.get('ResultURL')
#         queue_timeout_url = data.get('QueueTimeOutURL')
#         remarks = data.get('Remarks')
#         occasion = data.get('Occasion')

#         # Obtain the access token
#         access_token = get_access_token()
        
#         if access_token:
#             # Prepare the request body for the transaction reversal
#             reversal_data = {
#                 "Initiator": initiator,
#                 "SecurityCredential": security_credential,
#                 "CommandID": command_id,
#                 "TransactionID": transaction_id,
#                 "Amount": amount,
#                 "ReceiverParty": receiver_party,
#                 "RecieverIdentifierType": receiver_identifier_type,
#                 "ResultURL": result_url,
#                 "QueueTimeOutURL": queue_timeout_url,
#                 "Remarks": remarks,
#                 "Occasion": occasion
#             }

#             # Make a POST request to the reversal endpoint
#             reversal_url = 'https://sandbox.safaricom.co.ke/mpesa/reversal/v1/request'
#             headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

#             reversal_response = requests.post(reversal_url, json=reversal_data, headers=headers).json()

#             # Return the response from the transaction reversal
#             return jsonify(reversal_response)
#         else:
#             return jsonify({'error': 'Failed to retrieve access token.'}), 500

#     except Exception as e:
#         return json.dumps({'error': f'Error processing request: {str(e)}'})


# def check_transaction_status():
#     try:
#         # Get data from the request
#         data = request.json

#         # Update the URL for checking transaction status
#         transaction_status_url = 'https://sandbox.safaricom.co.ke/mpesa/transactionstatus/v1/query'

#         # Get the access token
#         access_token_response = get_access_token()
#         if isinstance(access_token_response, dict):
#             access_token = access_token_response.get('access_token')
#             if access_token:
#                 # Update headers with the access token
#                 headers = {
#                     'Content-Type': 'application/json',
#                     'Authorization': 'Bearer ' + access_token
#                 }

#                 # Send a POST request to check transaction status
#                 transaction_status_response = requests.post(transaction_status_url, json=data, headers=headers).json()

#                 # Print the response from checking transaction status
#                 print(transaction_status_response)

#                 # Return the response from checking transaction status
#                 return jsonify(transaction_status_response)
#             else:
#                 return jsonify({'error': 'Access token not found.'}), 500
#         else:
#             return jsonify({'error': 'Failed to retrieve access token.'}), 500

#     except Exception as e:
#         return json.dumps({'error': f'Error processing request: {str(e)}'})