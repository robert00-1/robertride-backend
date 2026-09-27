from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user import User
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.ride import Ride
from app.models.ride_request import RideRequest
driver_bp = Blueprint(
    "driver",
    __name__,
    url_prefix="/api/drivers"
)


@driver_bp.route("/register", methods=["POST"])
def register_driver():

    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    license_number = data.get("license_number")

    make = data.get("make")
    model = data.get("model")
    color = data.get("color")
    plate_number = data.get("plate_number")

    if not all([
        name,
        email,
        phone,
        password,
        license_number,
        make,
        model,
        color,
        plate_number
    ]):
        return {
            "message": "All fields are required"
        }, 400
    
    existing_user = User.query.filter(
        (User.phone == phone) |
        (User.email == email)
    ). first()

    if existing_user:
        return {
            "message": "User with email or phone already exists"
        }, 409
    
    existing_license = Driver.query.filter_by(
        license_number=license_number
    ).first()

    if existing_license:
        return {
            "message": "License number already registered"
        }, 409
    
    existing_plate = Vehicle.query.filter_by(
        plate_number=plate_number
    ).first()

    if existing_plate:
        return {
            "message": "Vehicle plate number already registered"
        }, 409
    
    password_hash = generate_password_hash(password)

    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=password_hash,
        role="driver"
    )

    db.session.add(user)
    db.session.flush()

    driver = Driver(
        user_id=user.id,
        stage_name="Town",
        stage_latitude=0.5143,
        stage_longitude=35.2698,
        license_number=license_number,
        status="offline"
        
    )

    db.session.add(driver)
    db.session.flush()

    vehicle = Vehicle(
        driver_id=driver.id,
        make=make,
        model=model,
        color=color,
        plate_number=plate_number

    )

    db.session.add(vehicle)

    db.session.commit()

    return {
        "message": "Driver registration successful",
        "driver": {
            "id": driver.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "license_number": driver.license_number,
            "status": driver.status,
            "vehicle": {
                "id": vehicle.id,
                "make": vehicle.make,
                "model": vehicle.model,
                "color": vehicle.color,
                "plate_number": vehicle.plate_number
            }

        }
    }, 201

@driver_bp.route("/status", methods=["PATCH"])
@jwt_required()
def update_driver_status():

    user_id = get_jwt_identity()

    driver = Driver.query.filter_by(
        user_id=int(user_id)
    ). first()

    if not driver:
        return {
            "message": "Driver not found"
        }, 404
    
    active_ride = Ride.query.filter(
        Ride.driver_id == driver.id,
        Ride.status.in_(["accepted", "arriving", "started"])
    ).first()

    if active_ride:
        return {
            "message": "You already have an active ride. Complete it before accepting another ride."
        }, 400
    
    
    data = request.get_json() or {}

    status = data.get("status")

    if status not in ["online", "offline"]:
        return {
            "message": "Status must be online or offline"
        }, 400
    
    driver.status = status

    db.session.commit()

    return {
        "message": "Driver status updated successfully",
        "driver": {
            "id": driver.id,
            "user_id": driver.user_id,
            "status": driver.status
        }
    }, 200
@driver_bp.route("/available", methods=["GET"])
@jwt_required()
def get_available_drivers():

    drivers = Driver.query.filter_by(
        status="online"
    ).all()

    result = []

    for driver in drivers:
        active_ride = Ride.query.filter(
            Ride.driver_id == driver.id,
            Ride.status.in_(["accepted", "arriving", "started"])
        ).first()

        user = User.query.get(driver.user_id)

        vehicle = Vehicle.query.filter_by(
            driver_id=driver.id
        ).first()
        if active_ride:
            continue
        user = User.query.get(driver.user_id)

        vehicle = Vehicle.query.filter_by(
            driver_id=driver.id
        ).first()

        if not user or not vehicle:
            continue

        result.append({
            "driver_id": driver.id,
            "name": user.name,
            "phone": user.phone,
            "status": driver.status,

            "stage": {
                "name": driver.stage_name,
                "latitude": driver.stage_latitude,
                "longitude": driver.stage_longitude
            },

            "current_location": {
                "latitude": driver.current_latitude,
                "longitude": driver.current_longitude
            },
            "vehicle": {
                "id": vehicle.id,
                "make": vehicle.make,
                "model": vehicle.model,
                "color": vehicle.color,
                "plate_number": vehicle.plate_number
            }
        })

    return {
        "message": "Available drivers retrieved successfully",
        "drivers": result
    }, 200

@driver_bp.route("/ride-requests", methods=["GET"])
@jwt_required()
def get_ride_requests():

    user_id = get_jwt_identity()

    driver = Driver.query.filter_by(
        user_id=int(user_id)
    ).first()

    if not driver:
        return {
            "message": "Driver not found"
        }, 404

    ride_requests = RideRequest.query.filter_by(
        driver_id=driver.id,
        status="pending"
    ).all()

    result = []

    for ride_request in ride_requests:

        ride = Ride.query.get(ride_request.ride_id)

        if not ride:
            continue

        result.append({
            "request_id": ride_request.id,
            "ride_id": ride.id,
            "pickup_location": ride.pickup_location,
            "destination": ride.destination,
            "distance_km": ride.distance_km,
            "fare": ride.fare,
            "ride_status": ride.status,
            "request_status": ride_request.status
        })

    return {
        "message": "Ride requests retrieved successfully",
        "requests": result
    }, 200

@driver_bp.route("/active-ride", methods=["GET"])
@jwt_required()
def get_active_ride():

    user_id = get_jwt_identity()

    driver = Driver.query.filter_by(
        user_id=int(user_id)
    ).first()

    if not driver:
        return {
            "message": "Driver not found"
        }, 404
    
    ride = Ride.query.filter(
        Ride.driver_id == driver.id,
        Ride.status.in_([
            "accepted",
            "arriving",
            "started"
        ])
    ).first()

    if not ride:
        return {
            "message": "No active ride"
        }, 404
    
    return {
        "message": "Active ride retrived successfully",
        "ride": {
            "id": ride.id,
            "driver_id": ride.driver_id,
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
    }, 200

@driver_bp.route(
    "/ride-requests/<int:request_id>/accept",
    methods=["PATCH"]
)
@jwt_required()
def accept_ride_request(request_id):

    user_id = get_jwt_identity()

    driver = Driver.query.filter_by(
        user_id=int(user_id)

    ). first()

    if not driver:
        return {
            "message": "Driver not found"
        }, 404
    
    ride_request = RideRequest.query.filter_by(
        id=request_id,
        driver_id=driver.id

    ).first()

    if not ride_request:
        return {
            "message": "Ride request not found"
        }, 404
    
    if ride_request.status != "pending":
        return {
            "message": "Ride request is no longer available"
        }, 400
    
    ride = Ride.query.get(ride_request.ride_id)

    if not ride:
        return {
            "message": "Ride not found"
        }, 404
    if ride.status != "requested":
        return {
            "message": "Ride has already been accepted"
        }, 400
    ride.driver_id = driver.id
    ride.status = "accepted"

    ride_request.status = "accepted"

    if (
        driver.current_latitude is not None
        and driver.current_longitude is not None
    ):
        start_latitude = driver.current_latitude
        start_longitude = driver.current_longitude
        start_location = "current"

    else:
        start_latitude = driver.stage_latitude
        start_longitude = driver.stage_longitude
        start_location = "stage"    

    db.session.commit()

    return {
        "message": "Ride accepted successfully",
        "ride": {
            "id": ride.id,
            "driver_id": ride.driver_id,
            "pickup_location": ride.pickup_location,
            "destination": ride.destination,
            "fare": ride.fare,
            "status": ride.status,
            "payment_status": ride.payment_status,

            "start_location": start_location,
            "start_latitude": start_latitude,
            "start_longitude": start_longitude

        },
        "request": {
            "id": ride_request.id,
            "status": ride_request.status
        }
    }, 200

@driver_bp.route("/location", methods=["PATCH"])
@jwt_required()
def update_driver_location():

    user_id = get_jwt_identity()

    driver = Driver.query.filter_by(
        user_id=int(user_id)
    ).first()

    if not driver:
        return {
            "message": "Driver not found"
        }, 404
    data = request.get_json() or []

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return {
            "message": "Latitude and longitude are required"
        }, 400
    
    if latitude < -90 or latitude > 90:
        return {
            "message": "Invalid latitude"
        }, 400
    
    if longitude < -180 or longitude > 180:
        return {
            "message": "Invalid longitude"
        }, 400
    
    driver.current_latitude = latitude
    driver.current_longitude = longitude

    db.session.commit()

    return {
        "message": "Driver location updated successfully",
        "driver": {
            "id": driver.id,
            "latitude": driver.current_latitude,
            "longitude": driver.current_longitude
        }
    }, 200

@driver_bp.route("/rides/<int:ride_id>/status", methods=["PATCH"])
@jwt_required()
def update_ride_status(ride_id):

    user_id = get_jwt_identity()

    driver = Driver.query.filter_by(
        user_id=int(user_id)
    ). first()

    if not driver:
        return {
            "message": "Driver not found"
        }, 404
    ride = Ride.query.filter_by(
        id=ride_id,
        driver_id=driver.id
    ). first()
    if not ride:
        return {
            "message": "Ride not found or not assigned to you"
        }, 404
    
    data = request.get_json() or {}

    new_status = data.get("status")

    allowed_statuses = [
        "arriving",
        "started",
        "completed"
    ]

    if new_status not in allowed_statuses:
        return {
            "message": "Status must be arriving, started, or completed"
        }, 400
    
    if ride.status == "accepted" and new_status != "arriving":
        return {
            "message": "Ride must be marked as arriving first"
        }, 400
    
    if ride.status == "arriving" and new_status != "started":
        return {
            "message": "Ride must be started after arriving"
        }, 400
    
    if ride.status == "started" and new_status != "completed":
        return {
            "message": "Ride must be completed after it has started"
        }, 400
    
    ride.status = new_status

    if  new_status == "completed":

        if (
            ride.destination_latitude is not None
            and ride.destination_longitude is not None
        ):
            driver.current_latitude = ride.destination_latitude
            driver.current_longitude = ride.destination_longitude

    db.session.commit()

    return {
        "message": "Ride status updated successfully",
        "ride": {
            "id": ride.id,
            "driver_id": ride.driver_id,
            "status": ride.status,
            "payment_status": ride.payment_status
        }
    }, 200


