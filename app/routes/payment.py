from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.ride import Ride
from app.models.payment import Payment
from app.services.mpesa import stk_push


payment_bp = Blueprint(
    "payment",
    __name__,
    url_prefix="/api/payments"
)


@payment_bp.route("/initiate", methods=["POST"])
@jwt_required()
def initiate_payment():

    data = request.get_json() or {}

    ride_id = data.get("ride_id")
    phone = data.get("phone")

    if not ride_id or not phone:
        return {
            "message": "Ride ID and phone are required"
        }, 400
    try:
        ride_id = int(ride_id)
    except (TypeError, ValueError):
        return {
            "message": "Ride ID must be a valid number"
        }, 400    

    user_id = int(get_jwt_identity())

    ride = Ride.query.filter_by(
        id=ride_id
        
    ).first()

    if not ride:
        return {
            "message": "Ride not found"
        }, 404
    if ride.passenger_id != user_id:
        return {
            "message": "You are not authorized for this ride"
        }, 403
    if ride.status != "completed":
        return {
            "message": "Payment can only be made after the ride is completed"
        }, 400
    

    if ride.payment_status == "paid":
        return {
            "message": "Ride has already been paid"
        }, 400

    existing_payment = Payment.query.filter_by(
        ride_id=ride.id,
        status="pending"
    ).first()

    if existing_payment:
        return {
            "message": "A payment is already pending for this ride",
            "payment": {
                "id": existing_payment.id,
                "amount": existing_payment.amount,
                "status": existing_payment.status
            }
        }, 400

    payment = Payment(
        ride_id=ride.id,
        phone=phone,
        amount=ride.fare,
        status="pending"
    )

    db.session.add(payment)
    db.session.commit()

    try:

        mpesa_response = stk_push(
            phone=phone,
            amount=ride.fare,
            account_reference=f"RIDE-{ride.id}"
        )

        payment.checkout_request_id = mpesa_response.get(
            "CheckoutRequestID"
        )

        payment.merchant_request_id = mpesa_response.get(
            "MerchantRequestID"
        )

        db.session.commit()

    except Exception as e:

        print("======== MPESA PAYMENT ERROR =========")
        print("ERROR TYPE:" ,type(e).__name__)
        print ("ERROR MESSAGE:", str(e))
        print("========================================")


        db.session.delete(payment)
        db.session.commit()

        return {
            "message": "Failed to initiate M-Pesa payment",
            "error": str(e)
        }, 500

    return {
        "message": "STK Push sent successfully",
        "payment": {
            "id": payment.id,
            "ride_id": payment.ride_id,
            "phone": payment.phone,
            "amount": payment.amount,
            "status": payment.status,
            "checkout_request_id": payment.checkout_request_id
        },
        "mpesa_response": mpesa_response
    }, 200

@payment_bp.route("/callback", methods=["POST"])
def mpesa_callback():

    data = request.get_json() or {}

    print("M-PESA CALLBACK:")
    print(data)

    try:
        stk_callback = data["Body"]["stkCallback"]

        checkout_request_id = stk_callback["CheckoutRequestID"]
        result_code = stk_callback["ResultCode"]
        result_description = stk_callback["ResultDesc"]

    except (KeyError, TypeError):
        return {
            "message": "Invalid M-Pesa callback"
        }, 400

    payment = Payment.query.filter_by(
        checkout_request_id=checkout_request_id
    ).first()

    if not payment:
        print(
            f"Payment not found for CheckoutRequestID: "
            f"{checkout_request_id}"
        )

        return {
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }, 200

    if result_code == 0:

        if payment.status == "paid":
            print(
                f"Payment {payment.id} has already been processed"
            )
            return {
                "ResultCode": 0,
                "ResultDesc": "Payment already processed"
            }, 200

        callback_metadata = stk_callback.get(
            "CallbackMetadata",
            {}
        )

        items = callback_metadata.get("Item", [])

        metadata = {}

        for item in items:
            name = item.get("Name")
            value = item.get("Value")

            metadata[name] = value

        mpesa_receipt = metadata.get("MpesaReceiptNumber")

        payment.status = "paid"
        payment.mpesa_receipt = mpesa_receipt

        ride = Ride.query.get(payment.ride_id)

        if ride:
            ride.payment_status = "paid"

        db.session.commit()

        print(
            f"Payment {payment.id} marked as PAID"
        )

    else:

        if payment.status == "paid":
            print(
                f"Payment {payment.id} is already paid"
            )

            return {
                "ResultCode": 0,
                "ResultDesc": "Payment already processed"
            }, 200

        payment.status = "failed"

        db.session.commit()

        print(
            f"Payment {payment.id} failed: "
            f"{result_description}"
        )

    return {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }, 200
@payment_bp.route("/ride/<int:ride_id>", methods=["GET"])
@jwt_required()
def get_ride_payment(ride_id):

    user_id = int(get_jwt_identity())

    ride = Ride.query.filter_by(
        id=ride_id,
        passenger_id=int(user_id)
    ). first()

    if not ride:
        return {
            "message": "Ride not found"
        }, 404
    
    payment = Payment.query.filter_by(
        ride_id=ride.id
    ).order_by(
        Payment.id.desc()
    ).first()

    if not payment:
        return {
            "message": "No payment found for this ride"
        }, 404
    
    return {
        "message": "Ride payment retrieved successfully",
        "payment": {
            "id": payment.id,
            "ride_id": payment.ride_id,
            "phone": payment.phone,
            "amount": payment.amount,
            "status": payment.status,
            "mpesa_receipt": payment.mpesa_receipt,
            "checkout_request_id": payment.checkout_request_id,
            "merchant_request_id": payment.merchant_request_id,
            "created_at": payment.created_at.isoformat()
                 if payment.created_at else None  
        }
    }, 200

@payment_bp.route("/<int:payment_id>", methods=["GET"])
@jwt_required()
def get_payment(payment_id):

    user_id = int(get_jwt_identity())

    payment = Payment.query.get(payment_id)

    if not payment:
        return {
            "message": "Payment not found"
        }, 404
    
    ride = Ride.query.get(payment.ride_id)

    if not ride:
        return {
            "message": "Ride not found"
        }, 404
    
    if ride.passenger_id != int(user_id):
        return {
            "message": "You are not authorized to view this payment"
        }, 403
    
    return {
        "message": "Payment retrieved successfully",
        "payment": {
            "id": payment.id,
            "ride_id": payment.ride_id,
            "phone": payment.phone,
            "amount": payment.amount,
            "status": payment.status,
            "mpesa_receipt": payment.mpesa_receipt,
            "checkout_request_id": payment.checkout_request_id,
            "merchant_request_id": payment.merchant_request_id,
            "created_at": payment.created_at.isoformat()
                 if payment.created_at else None

    
        }
    }, 200