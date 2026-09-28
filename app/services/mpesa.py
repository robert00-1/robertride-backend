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

