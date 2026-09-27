from datetime import datetime

from app.extensions import db

class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)

    passenger_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("drivers.id"),
        nullable=True
    )

    pickup_location = db.Column(
        db.String(255),
        nullable=False
    )
    pickup_latitude= db.Column(
        db.Float,
        nullable=True
    )
    pickup_longitude = db.Column(
        db.Float,
        nullable=True
    )

    destination = db.Column(
        db.String(255),
        nullable=False
    )
    destination_latitude = db.Column(
        db.Float,
        nullable=True
    )
    destination_longitude = db.Column(
        db.Float,
        nullable=True
    )

    distance_km = db.Column(
        db.Float,
        nullable=False
    )

    fare = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="requested"
    )
    payment_status = db.Column(
        db.String(30),
        nullable=False,
        default="pending"

    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
