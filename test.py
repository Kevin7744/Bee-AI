import requests
import json

# Update this URL based on where your Flask app is running
base_url = 'http://127.0.0.1:5000'

# Example user input
user_input = "pay 1 to 174379"

# Sending user input to initiate STK push directly (without OpenAI)
stk_push_response = requests.post(f'{base_url}/initiate_stk_push', json={'user_input': user_input}).json()

# Print the STK push response
print("STK Push Response:")
print(stk_push_response)
