import requests
from flask import Flask, request, jsonify
from datetime import datetime
import base64
from pydantic import BaseModel
from typing import Union

app = Flask(__name__)

class StkPushRequest(BaseModel):
    amount: Union[int, str]
    business_short_code: int

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

def initiate_stk_push(amount, business_short_code):
    access_token_response = get_access_token()
    if isinstance(access_token_response, dict):
        access_token = access_token_response.get('access_token')
        if access_token:
            process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            callback_url = 'http://yourcustomurl.local/'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
            password = base64.b64encode((str(business_short_code) + passkey + timestamp).encode()).decode()
            party_a = "254719321423"
            party_b = str(business_short_code)
            account_reference = 'Test'
            transaction_desc = 'stkpush test'
            
            stk_push_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            } 
            
            stk_push_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
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
                    return jsonify({'CheckoutRequestID': checkout_request_id, 'ResponseCode': response_code})
                else:
                    return jsonify({'error': f'STK push failed. Response Code: {response_code}'}), 500
            except requests.exceptions.RequestException as e:
                return jsonify({'error': f'Error: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Access token not found.'}), 500
    else:
        return jsonify({'error': 'Failed to retrieve access token.'}), 500

@app.route('/initiate_stk_push', methods=['POST'])
def handle_stk_push_request():
    try:
        data = request.get_json()
        stk_request = StkPushRequest(**data)
        response = initiate_stk_push(stk_request.amount, stk_request.business_short_code)
        return response
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
