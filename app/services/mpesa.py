import os
import base64
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

def get_mpesa_access_token():
    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")

    credentials = f"{consumer_key}:{consumer_secret}"

    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    response = requests.get(
        "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {encoded_credentials}"
        }

    )

    response.raise_for_status()

    return response.json()["access_token"]

def stk_push(phone, amount, account_reference):
    access_token = get_mpesa_access_token()

    shortcode = os.getenv("MPESA_SHORTCODE")
    passkey = os.getenv("MPESA_PASSKEY")
    callback_url = os.getenv("MPESA_CALLBACK_URL")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password_string = f"{shortcode}{passkey}{timestamp}"

    password = base64.b64encode(
        password_string.encode()
    ).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": "RobertRide payment"
    }

    response = requests.post(
         "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
         json=payload,
         headers={
             "Authorization": f"Bearer {access_token}",
             "Content-Type": "application/json"
         }
    )

    if not response.ok:
        print("M-PESA STATUS:", response.status_code)
        print("M-PESA RESPONSE:", response.text)

        raise Exception(
           f"M-PESA error {response.status_code}: {response.text}"
       )

    return response.json()