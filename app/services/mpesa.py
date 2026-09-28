import os
import base64
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

def get_mpesa_access_token():

    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")

    if not consumer_key:
        raise Exception(
            "MPESA_CONSUMER_KEY is missing"
        )

    if not consumer_secret:
        raise Exception(
            "MPESA_CONSUMER_SECRET is missing"
        )

    credentials = (
        f"{consumer_key}:{consumer_secret}"
    )

    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    response = requests.get(
        "https://sandbox.safaricom.co.ke/oauth/v1/generate"
        "?grant_type=client_credentials",

        headers={
            "Authorization": (
                f"Basic {encoded_credentials}"
            )
        },

        timeout=30
    )

    print(
        "M-PESA TOKEN STATUS:",
        response.status_code
    )

    print(
        "M-PESA TOKEN RESPONSE:",
        response.text
    )

    response.raise_for_status()

    data = response.json()

    if "access_token" not in data:
        raise Exception(
            f"M-Pesa access token missing: {data}"
        )

    return data["access_token"]


def stk_push(phone, amount, account_reference):

    access_token = get_mpesa_access_token()

    shortcode = os.getenv("MPESA_SHORTCODE")
    passkey = os.getenv("MPESA_PASSKEY")
    callback_url = os.getenv("MPESA_CALLBACK_URL")

    if not shortcode:
        raise Exception(
            "MPESA_SHORTCODE is missing"
        )

    if not passkey:
        raise Exception(
            "MPESA_PASSKEY is missing"
        )

    if not callback_url:
        raise Exception(
            "MPESA_CALLBACK_URL is missing"
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    password_string = (
        f"{shortcode}{passkey}{timestamp}"
    )

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
        "https://sandbox.safaricom.co.ke/"
        "mpesa/stkpush/v1/processrequest",

        json=payload,

        headers={
            "Authorization": (
                f"Bearer {access_token}"
            ),
            "Content-Type": "application/json"
        },

        timeout=30
    )

    print(
        "M-PESA STK STATUS:",
        response.status_code
    )

    print(
        "M-PESA STK RESPONSE:",
        response.text
    )

    if not response.ok:
        raise Exception(
            f"M-PESA error "
            f"{response.status_code}: "
            f"{response.text}"
        )

    return response.json()
