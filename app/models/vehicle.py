from datetime import datetime

from app.extensions import db

class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("drivers.id"),
        nullable=False,
        unique=True
    )

    make = db.Column(
        db.String(50),
        nullable=False
    )
    model = db.Column(
        db.String(50),
        nullable=False
    )
    model = db.Column(
        db.String(50),
        nullable=False
    )
    color = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )
    plate_number = db.Column(
        db.String(20),
        nullable=False,
        unique=True

    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
