import os
import json
from flask import Flask, request, jsonify
from datetime import datetime
import base64
import requests
from pydantic import BaseModel, Field
from typing import Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Replace 'OPENAI_API_KEY' with your actual OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

class StkPushRequest(BaseModel):
    amount: Union[int, str] = Field(..., title='Amount', description='Amount for STK push (integer or string)')
    business_short_code: int = Field(..., title='Business Short Code', description='6-digit Business Short Code')

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
        return {'access_token': access_token}
    except requests.exceptions.RequestException as e:
        return {'error': 'Access token not found.'}

def initiate_stk_push(request_data: StkPushRequest):
    access_token_response = get_access_token()
    
    if isinstance(access_token_response, dict):
        access_token = access_token_response.get('access_token')

        if access_token:
            process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            callback_url = 'http://yourcustomurl.local/'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
            password = base64.b64encode((str(request_data.business_short_code) + passkey + timestamp).encode()).decode()
            party_a = "254719321423"
            party_b = str(request_data.business_short_code)
            account_reference = 'Test'
            transaction_desc = 'stkpush test'
            
            stk_push_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            } 
            
            stk_push_payload = {
                'BusinessShortCode': str(request_data.business_short_code),
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': str(request_data.amount),
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
                    return jsonify({'CheckoutRequestID': checkout_request_id, 'ResponseCode': response_code})
                else:
                    return jsonify({'error': f'STK push failed. Response Code: {response_code}'}), 500
            except requests.exceptions.RequestException as e:
                return jsonify({'error': f'Error: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Access token not found.'}), 500
    else:
        return jsonify({'error': 'Failed to retrieve access token.'}), 500

def openai_chat(message):
    openai_endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "messages": [{"role": "system", "content": "You are a helpful assistant."},
                     {"role": "user", "content": message}]
    }

    try:
        response = requests.post(openai_endpoint, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f'Error in OpenAI request: {str(e)}'

@app.route('/initiate_stk_push', methods=['POST'])
def handle_stk_push_request():
    try:
        request_data = StkPushRequest.parse_obj(request.json)
        response = initiate_stk_push(request_data)
        return response
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def handle_chat_request():
    try:
        user_message = request.json.get('message', '')
        ai_response = openai_chat(user_message)
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': f'Error processing chat request: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
