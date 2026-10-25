
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.ride import Ride
from app.services.fare_service import calculate_fare
from app.models.driver import Driver
from app.models.ride_request import RideRequest
from app.models.user import User
from app.models.vehicle import Vehicle
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

ride_bp = Blueprint(
    "ride",
    __name__,
    url_prefix="/api/rides"
)


@ride_bp.route("/estimate", methods=["POST"])
@jwt_required()
def estimate_fare():
    data = request.get_json() or {}

    pickup_location = data.get("pickup_location")
    destination = data.get("destination")

    pickup_latitude = data.get("pickup_latitude")
    pickup_longitude = data.get("pickup_longitude")
    destination_latitude = data.get("destination_latitude")
    destination_longitude = data.get("destination_longitude")

    if not pickup_location or not destination:
        return {
            "message": "Pickup location and destination are required"
        }, 400

    if (
        pickup_latitude is None
        or pickup_longitude is None
        or destination_latitude is None
        or destination_longitude is None
    ):
        return {
            "message": "Pickup and destination coordinates are required"
        }, 400

    result = calculate_fare(
        pickup_latitude,
        pickup_longitude,
        destination_latitude,
        destination_longitude
    )

    return {
        "pickup_location": pickup_location,
        "destination": destination,
        "distance_km": result["distance_km"],
        "fare": result["fare"]
    }, 200


@ride_bp.route("/", methods=["POST"])
@jwt_required()
def create_ride():
    data = request.get_json() or {}

    pickup_location = data.get("pickup_location")
    pickup_latitude = data.get("pickup_latitude")
    pickup_longitude = data.get("pickup_longitude")

    destination = data.get("destination")
    destination_latitude = data.get("destination_latitude")
    destination_longitude = data.get("destination_longitude")

    if not pickup_location or not destination:
        return {
            "message": "Pickup location and destination are required"
        }, 400

    if (
        pickup_latitude is None
        or pickup_longitude is None
        or destination_latitude is None
        or destination_longitude is None
    ):
        return {
            "message": "Pickup and destination coordinates are required"
        }, 400

    result = calculate_fare(
        pickup_latitude,
        pickup_longitude,
        destination_latitude,
        destination_longitude
    )

    passenger_id = get_jwt_identity()

    ride = Ride(
        passenger_id=int(passenger_id),
        pickup_location=pickup_location,
        pickup_latitude=pickup_latitude,
        pickup_longitude=pickup_longitude,
        destination=destination,
        destination_latitude=destination_latitude,
        destination_longitude=destination_longitude,
        distance_km=result["distance_km"],
        fare=result["fare"],
        status="requested",
        payment_status="pending"
    )

    db.session.add(ride)
    db.session.commit()

    return {
        "message": "Ride created successfully",
        "ride": {
            "id": ride.id,
            "pickup_location": ride.pickup_location,
            "pickup_latitude": ride.pickup_latitude,
            "pickup_longitude": ride.pickup_longitude,
            "destination": ride.destination,
            "destination_latitude": ride.destination_latitude,
            "destination_longitude": ride.destination_longitude,
            "distance_km": ride.distance_km,
            "fare": ride.fare,
            "status": ride.status,
            "payment_status": ride.payment_status
        }
    }, 201


@ride_bp.route("/<int:ride_id>/request", methods=["POST"])
@jwt_required()
def request_driver(ride_id):
    passenger_id = get_jwt_identity()

    ride = Ride.query.filter_by(
        id=ride_id,
        passenger_id=int(passenger_id)
    ).first()

    if not ride:
        return {
            "message": "Ride not found"
        }, 404

    if ride.status != "requested":
        return {
            "message": "This ride is no longer available"
        }, 400

    data = request.get_json() or {}
    driver_id = data.get("driver_id")

    if not driver_id:
        return {
            "message": "Driver ID is required"
        }, 400

    driver = Driver.query.filter_by(
        id=driver_id,
        status="online",
        is_blocked=False
    ).first()

    if not driver:
        return {
            "message": "Driver is not available"
        }, 404

    existing_request = RideRequest.query.filter_by(
        ride_id=ride.id,
        driver_id=driver.id
    ).first()

    if existing_request:
        return {
            "message": "You have already requested this driver"
        }, 409

    ride_request = RideRequest(
        ride_id=ride.id,
        driver_id=driver.id,
        status="pending"
    )

    db.session.add(ride_request)
    db.session.commit()

    return {
        "message": "Ride request sent successfully",
        "request": {
            "id": ride_request.id,
            "ride_id": ride_request.ride_id,
            "driver_id": ride_request.driver_id,
            "status": ride_request.status
        }
    }, 201


@ride_bp.route("/<int:ride_id>/driver", methods=["GET"])
@jwt_required()
def get_ride_driver(ride_id):
    user_id = get_jwt_identity()

    ride = Ride.query.filter_by(
        id=ride_id,
        passenger_id=int(user_id)
    ).first()

    if not ride:
        return {
            "message": "Ride not found"
        }, 404

    if not ride.driver_id:
        return {
            "message": "No driver has been assigned yet",
            "ride": {
                "id": ride.id,
                "status": ride.status,
                "payment_status": ride.payment_status
            },
            "driver": None
        }, 200

    driver = Driver.query.get(ride.driver_id)

    if not driver:
        return {
            "message": "Assigned driver not found",
            "ride": {
                "id": ride.id,
                "status": ride.status,
                "payment_status": ride.payment_status
            },
            "driver": None
        }, 200

    user = User.query.get(driver.user_id)

    vehicle = Vehicle.query.filter_by(
        driver_id=driver.id
    ).first()

    return {
        "message": "Driver details retrieved successfully",
        "ride": {
            "id": ride.id,
            "pickup_location": ride.pickup_location,
            "destination": ride.destination,
            "distance_km": ride.distance_km,
            "fare": ride.fare,
            "status": ride.status,
            "payment_status": ride.payment_status
        },
        "driver": {
            "id": driver.id,
            "name": user.name if user else None,
            "phone": user.phone if user else None,
            "status": driver.status,
            "license_number": driver.license_number,
            "latitude": driver.current_latitude,
            "longitude": driver.current_longitude,
            "location_available": (
                driver.current_latitude is not None
                and driver.current_longitude is not None
            ),
            "vehicle": {
                "id": vehicle.id if vehicle else None,
                "make": vehicle.make if vehicle else None,
                "model": vehicle.model if vehicle else None,
                "color": vehicle.color if vehicle else None,
                "plate_number": vehicle.plate_number if vehicle else None
            }
        }
    }, 200


@ride_bp.route("/<int:ride_id>/driver/location", methods=["GET"])
@jwt_required()
def get_driver_location(ride_id):
    user_id = get_jwt_identity()

    ride = Ride.query.filter_by(
        id=ride_id,
        passenger_id=int(user_id)
    ).first()

    if not ride:
        return {
            "message": "Ride not found"
        }, 404

    if not ride.driver_id:
        return {
            "message": "No driver has been assigned to this ride"
        }, 404

    driver = Driver.query.get(ride.driver_id)

    if not driver:
        return {
            "message": "Driver not found"
        }, 404

    if (
        driver.current_latitude is None
        or driver.current_longitude is None
    ):
        return {
            "message": "Driver location is not available yet"
        }, 404

    return {
        "message": "Driver location retrieved successfully",
        "location": {
            "latitude": driver.current_latitude,
            "longitude": driver.current_longitude
        }
    }, 200


@ride_bp.route("/<int:ride_id>/tracking", methods=["GET"])
@jwt_required()
def get_ride_tracking(ride_id):
    user_id = get_jwt_identity()

    ride = Ride.query.filter_by(
        id=ride_id,
        passenger_id=int(user_id)
    ).first()

    if not ride:
        return {
            "message": "Ride not found"
        }, 404

    # Return the ride status even before a driver accepts.
    if not ride.driver_id:
        return {
            "message": "Waiting for a driver to accept this ride",
            "ride": {
                "id": ride.id,
                "status": ride.status,
                "pickup": {
                    "location": ride.pickup_location,
                    "latitude": ride.pickup_latitude,
                    "longitude": ride.pickup_longitude
                },
                "destination": {
                    "location": ride.destination,
                    "latitude": ride.destination_latitude,
                    "longitude": ride.destination_longitude
                }
            },
            "driver": None
        }, 200

    driver = Driver.query.get(ride.driver_id)

    if not driver:
        return {
            "message": "Assigned driver not found",
            "ride": {
                "id": ride.id,
                "status": ride.status
            },
            "driver": None
        }, 200

    user = User.query.get(driver.user_id)

    vehicle = Vehicle.query.filter_by(
        driver_id=driver.id
    ).first()

    # GPS may not be available immediately after acceptance.
    location_available = (
        driver.current_latitude is not None
        and driver.current_longitude is not None
    )

    return {
        "message": "Ride tracking information retrieved successfully",
        "ride": {
            "id": ride.id,
            "status": ride.status,
            "pickup": {
                "location": ride.pickup_location,
                "latitude": ride.pickup_latitude,
                "longitude": ride.pickup_longitude
            },
            "destination": {
                "location": ride.destination,
                "latitude": ride.destination_latitude,
                "longitude": ride.destination_longitude
            }
        },
        "driver": {
            "id": driver.id,
            "name": user.name if user else None,
            "phone": user.phone if user else None,
            "latitude": driver.current_latitude,
            "longitude": driver.current_longitude,
            "location_available": location_available,
            "vehicle": {
                "make": vehicle.make if vehicle else None,
                "model": vehicle.model if vehicle else None,
                "color": vehicle.color if vehicle else None,
                "plate_number": vehicle.plate_number if vehicle else None
            }
        }
    }, 200
def get_ride_share_serializer():
    return URLSafeTimedSerializer(
        current_app.config["JWT_SECRET_KEY"],
        salt="robertride-live-share-v1"
    )


@ride_bp.route("/<int:ride_id>/share-link", methods=["POST"])
@jwt_required()
def create_ride_share_link(ride_id):
    user_id = int(get_jwt_identity())

    ride = Ride.query.filter_by(
        id=ride_id,
        passenger_id=user_id
    ).first()

    if not ride:
        return {"message": "Ride not found"}, 404

    if ride.status == "completed":
        return {"message": "This ride has already been completed"}, 400

    token = get_ride_share_serializer().dumps({
        "ride_id": ride.id,
        "passenger_id": ride.passenger_id
    })

    return {
        "message": "Share link created successfully",
        "token": token,
        "expires_in_seconds": 86400
    }, 200


@ride_bp.route("/shared/<string:token>", methods=["GET"])
def get_shared_ride_tracking(token):
    try:
        data = get_ride_share_serializer().loads(
            token,
            max_age=86400
        )
    except SignatureExpired:
        return {"message": "This ride-sharing link has expired"}, 410
    except BadSignature:
        return {"message": "Invalid ride-sharing link"}, 404

    ride = Ride.query.filter_by(
        id=data.get("ride_id"),
        passenger_id=data.get("passenger_id")
    ).first()

    if not ride:
        return {"message": "Ride not found"}, 404

    driver_data = None

    if ride.driver_id:
        driver = Driver.query.get(ride.driver_id)

        if driver:
            driver_data = {
                "latitude": driver.current_latitude,
                "longitude": driver.current_longitude,
                "location_available": (
                    driver.current_latitude is not None
                    and driver.current_longitude is not None
                )
            }

    return {
        "ride": {
            "id": ride.id,
            "status": ride.status,
            "pickup": {
                "location": ride.pickup_location,
                "latitude": ride.pickup_latitude,
                "longitude": ride.pickup_longitude
            },
            "destination": {
                "location": ride.destination,
                "latitude": ride.destination_latitude,
                "longitude": ride.destination_longitude
            }
        },
        "driver": driver_data
    }, 200