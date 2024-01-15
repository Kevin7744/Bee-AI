import requests
from flask import Flask, request, jsonify
from datetime import datetime
import base64
import json

app = Flask(__name__)

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
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            party_a = "254719321423"
            party_b = business_short_code
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
                    return json.dumps({'CheckoutRequestID': checkout_request_id, 'ResponseCode': response_code})
                else:
                    return json.dumps({'error': f'STK push failed. Response Code: {response_code}'})
            except requests.exceptions.RequestException as e:
                return json.dumps({'error': f'Error: {str(e)}'})
        else:
            return json.dumps({'error': 'Access token not found.'})
    else:
        return json.dumps({'error': 'Failed to retrieve access token.'})

@app.route('/initiate_stk_push', methods=['GET', 'POST'])
def handle_stk_push_request():
    try:
        amount = request.form['amount']
        business_short_code = request.form['business_short_code']
        
        response = initiate_stk_push(amount, business_short_code)
        return response
    except Exception as e:
        return json.dumps({'error': f'Error processing request: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
