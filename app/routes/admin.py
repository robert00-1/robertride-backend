
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.driver import Driver
from app.models.vehicle import Vehicle

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


def get_admin_user():
    """Return the authenticated admin, or None for other users."""
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None

    user = db.session.get(User, user_id)

    if not user or user.role != "admin":
        return None

    return user


@admin_bp.route("/drivers", methods=["GET"])
@jwt_required()
def list_drivers():
    admin = get_admin_user()

    if not admin:
        return {"message": "Admin access required"}, 403

    drivers = Driver.query.order_by(Driver.id.desc()).all()
    result = []

    for driver in drivers:
        user = db.session.get(User, driver.user_id)
        vehicle = Vehicle.query.filter_by(
            driver_id=driver.id
        ).first()

        if not user:
            continue

        result.append({
            "driver_id": driver.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "license_number": driver.license_number,
            "status": driver.status,
            "is_blocked": driver.is_blocked,
            "vehicle": {
                "make": vehicle.make,
                "model": vehicle.model,
                "color": vehicle.color,
                "plate_number": vehicle.plate_number
            } if vehicle else None,
            "created_at": driver.created_at.isoformat()
            if driver.created_at else None
        })

    return {"drivers": result}, 200


@admin_bp.route(
    "/drivers/<int:driver_id>/block",
    methods=["PATCH"]
)
@jwt_required()
def block_driver(driver_id):
    admin = get_admin_user()

    if not admin:
        return {"message": "Admin access required"}, 403

    driver = db.session.get(Driver, driver_id)

    if not driver:
        return {"message": "Driver not found"}, 404

    driver.is_blocked = True
    driver.status = "offline"
    db.session.commit()

    return {
        "message": "Driver blocked successfully",
        "driver": {
            "id": driver.id,
            "is_blocked": driver.is_blocked,
            "status": driver.status
        }
    }, 200


@admin_bp.route(
    "/drivers/<int:driver_id>/unblock",
    methods=["PATCH"]
)
@jwt_required()
def unblock_driver(driver_id):
    admin = get_admin_user()

    if not admin:
        return {"message": "Admin access required"}, 403

    driver = db.session.get(Driver, driver_id)

    if not driver:
        return {"message": "Driver not found"}, 404

    driver.is_blocked = False
    # Keep the driver offline until they choose to go online.
    driver.status = "offline"
    db.session.commit()

    return {
        "message": "Driver unblocked successfully",
        "driver": {
            "id": driver.id,
            "is_blocked": driver.is_blocked,
            "status": driver.status
        }
    }, 200
