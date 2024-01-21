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
        return access_token
    except requests.exceptions.RequestException as e:
        return None

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
    try:
        # Extract data from the request
        data = request.json
        short_code = data.get('ShortCode')
        response_type = data.get('ResponseType')
        confirmation_url = data.get('ConfirmationURL')
        validation_url = data.get('ValidationURL')

        # Obtain the access token
        access_token = get_access_token()
        
        if access_token:
            # Prepare the request body for C2B URL registration
            registration_data = {
                "ShortCode": short_code,
                "ResponseType": response_type,
                "ConfirmationURL": confirmation_url,
                "ValidationURL": validation_url
            }

            # Make a POST request to the C2B URL registration endpoint
            c2b_registration_url = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'
            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
            
            registration_response = requests.post(c2b_registration_url, json=registration_data, headers=headers).json()

            # Return the response from the C2B URL registration
            return jsonify(registration_response)
        else:
            return jsonify({'error': 'Failed to retrieve access token.'}), 500

    except Exception as e:
        return json.dumps({'error': f'Error processing request: {str(e)}'})

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

@app.route('/generate_dynamic_qr', methods=['POST'])
def generate_dynamic_qr_endpoint():
    try:
        data = request.json
        response = generate_dynamic_qr(data)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500


@app.route('/reverse_transaction', methods=['POST'])
def reverse_transaction():
    try:
        # Extract data from the request
        data = request.json
        initiator = data.get('Initiator')
        security_credential = data.get('SecurityCredential')
        command_id = data.get('CommandID')
        transaction_id = data.get('TransactionID')
        amount = data.get('Amount')
        receiver_party = data.get('ReceiverParty')
        receiver_identifier_type = data.get('ReceiverIdentifierType')
        result_url = data.get('ResultURL')
        queue_timeout_url = data.get('QueueTimeOutURL')
        remarks = data.get('Remarks')
        occasion = data.get('Occasion')

        # Obtain the access token
        access_token = get_access_token()
        
        if access_token:
            # Prepare the request body for the transaction reversal
            reversal_data = {
                "Initiator": initiator,
                "SecurityCredential": security_credential,
                "CommandID": command_id,
                "TransactionID": transaction_id,
                "Amount": amount,
                "ReceiverParty": receiver_party,
                "RecieverIdentifierType": receiver_identifier_type,
                "ResultURL": result_url,
                "QueueTimeOutURL": queue_timeout_url,
                "Remarks": remarks,
                "Occasion": occasion
            }

            # Make a POST request to the reversal endpoint
            reversal_url = 'https://sandbox.safaricom.co.ke/mpesa/reversal/v1/request'
            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

            reversal_response = requests.post(reversal_url, json=reversal_data, headers=headers).json()

            # Return the response from the transaction reversal
            return jsonify(reversal_response)
        else:
            return jsonify({'error': 'Failed to retrieve access token.'}), 500

    except Exception as e:
        return json.dumps({'error': f'Error processing request: {str(e)}'})


@app.route('/check_transaction_status', methods=['POST'])
def check_transaction_status():
    try:
        # Get data from the request
        data = request.json

        # Update the URL for checking transaction status
        transaction_status_url = 'https://sandbox.safaricom.co.ke/mpesa/transactionstatus/v1/query'

        # Get the access token
        access_token_response = get_access_token()
        if isinstance(access_token_response, dict):
            access_token = access_token_response.get('access_token')
            if access_token:
                # Update headers with the access token
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + access_token
                }

                # Send a POST request to check transaction status
                transaction_status_response = requests.post(transaction_status_url, json=data, headers=headers).json()

                # Print the response from checking transaction status
                print(transaction_status_response)

                # Return the response from checking transaction status
                return jsonify(transaction_status_response)
            else:
                return jsonify({'error': 'Access token not found.'}), 500
        else:
            return jsonify({'error': 'Failed to retrieve access token.'}), 500

    except Exception as e:
        return json.dumps({'error': f'Error processing request: {str(e)}'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
