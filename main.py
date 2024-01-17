import re
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import base64
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

def extract_payment_details(user_input):
    # Use regex to extract amount and business code
    match = re.search(r'(\d+)\s+to\s+(\d{6})', user_input)
    if match:
        amount = match.group(1)
        business_short_code = match.group(2)
        return amount, business_short_code
    else:
        return None, None

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
        user_input = request.json['user_input']

        # Extract payment details using regex
        amount, business_short_code = extract_payment_details(user_input)

        if amount is not None and business_short_code is not None:
            # Use the extracted details to initiate STK push
            response = initiate_stk_push(amount, business_short_code)
            return response
        else:
            return jsonify({'error': 'Invalid user input format. Please provide amount and business code.'}), 400

    except Exception as e:
        return json.dumps({'error': f'Error processing request: {str(e)}'})


@app.route('/register_c2b_urls', methods=['POST'])
def register_c2b_urls():
    # Extract data from the request
    data = request.json
    short_code = data.get('ShortCode')
    response_type = data.get('ResponseType')
    confirmation_url = data.get('ConfirmationURL')
    validation_url = data.get('ValidationURL')

    # Prepare the request body for C2B URL registration
    registration_data = {
        "ShortCode": short_code,
        "ResponseType": response_type,
        "ConfirmationURL": confirmation_url,
        "ValidationURL": validation_url
    }

    # Make a POST request to the C2B URL registration endpoint
    c2b_registration_url = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'
    headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN", "Content-Type": "application/json"}
    
    registration_response = requests.post(c2b_registration_url, json=registration_data, headers=headers).json()

    # Return the response from the C2B URL registration
    return jsonify(registration_response)


@app.route('/generate_dynamic_qr', methods=['POST'])
def generate_dynamic_qr():
    # Get data from the request
    data = request.json

    # Update the URL for the dynamic QR code generation API
    dynamic_qr_url = 'https://sandbox.safaricom.co.ke/mpesa/qrcode/v1/generate'

    # Send a POST request to generate the dynamic QR code
    dynamic_qr_response = requests.post(dynamic_qr_url, json=data).json()

    # Print the response from the dynamic QR code generation
    print(dynamic_qr_response)

    # Return the response from the dynamic QR code generation
    return jsonify(dynamic_qr_response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
