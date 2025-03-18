# utils/digikey_tools.py
import json
import requests
from urllib.parse import quote
import os

TOKEN_FILE = os.path.join(os.path.dirname(__file__), '../digikey_token.json')

def load_token():
    with open(TOKEN_FILE) as f:
        return json.load(f)

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f)

def use_refresh_token():
    token = load_token()
    url = 'https://api.digikey.com/v1/oauth2/token'
    url_data = {
        'refresh_token': token['refresh_token'],
        'client_id': token['client_id'],
        'client_secret': token['client_secret'],
        'redirect_uri': 'https://localhost',
        'grant_type': 'refresh_token'
    }
    response = requests.post(url, data=url_data)
    if response.status_code == 200:
        token.update(response.json())
        save_token(token)
        return token
    else:
        print("Refresh failed. Use auth code manually.")
        return None

def get_product_details(part_number, token):
    part_number = quote(part_number)
    url = f'https://api.digikey.com/Search/v3/Products/{part_number}'
    headers = {
        'x-digikey-locale': 'en',
        'X-DIGIKEY-Locale-Site': 'US',
        'X-DIGIKEY-Locale-Currency': 'USD',
        'Authorization': f"{token['token_type']} {token['access_token']}",
        'X-DIGIKEY-Client-Id': token['client_id']
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        token = use_refresh_token()
        if not token: return None
        headers['Authorization'] = f"{token['token_type']} {token['access_token']}"
        response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
