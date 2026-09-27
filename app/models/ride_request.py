from datetime import datetime

from app.extensions import db

class RideRequest(db.Model):
    __tablename__ = "ride_requests"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    ride_id = db.Column(
        db.Integer,
        db.ForeignKey("rides.id"),
        nullable=False
    )

    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("drivers.id"),
        nullable=False
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