from datetime import datetime

from app.extensions import db

class Driver(db.Model):
    __tablename__ = "drivers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )
    stage_name = db.Column(
        db.String(100),
        nullable=False,
        default="Town"
    )

    stage_latitude = db.Column(
        db.Float,
        nullable=True
    )
    stage_longitude = db.Column(
        db.Float,
        nullable=True
    )

    license_number = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="offline"
    )

    current_latitude = db.Column(
        db.Float,
        nullable=True
    )
    current_longitude = db.Column(
        db.Float,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False

    )