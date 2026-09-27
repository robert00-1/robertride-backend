from datetime import datetime

from app.extensions import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ride_id = db.Column(
        db.Integer,
        db.ForeignKey("rides.id"),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    checkout_request_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True

    )

    merchant_request_id = db.Column(
        db.String(100),
        nullable=True
    )

    mpesa_receipt = db.Column(
        db.String(100),
        unique=True,
        nullable=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
