from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__,url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")


    if not name or not phone or not password:

        return {
            "message": "Name, phone and password are required"
        }, 400
    
    existing_user = User.query.filter(
        (User.phone == phone) | (User.email == email)
    ).first()

    if existing_user:
        return {
            "message": "User with this email or phone already exists"
        }, 409
    
    password_hash = generate_password_hash(password)

    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=password_hash,
        role="passenger"
    )

    db.session.add(user)
    db.session.commit()

    return {
        "message": "Registration succesful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role
        }
    }, 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    phone = data.get("phone")
    password = data.get("password")

    if not phone or  not password:
        return {
            "message": "Phone and password are required"
        }, 400
    
    user = User.query.filter_by(phone=phone).first()

    if not user:
        return {
            "message": "Invalid phone or password"
        }, 401
    
    if not check_password_hash(user.password_hash, password):
        return {
            "message": "Invalid phone or password"
        }, 401
    access_token = create_access_token(
        identity=str(user.id)
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role
        }
    }, 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return {
            "message": "User not found"


        }, 404
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role
        }
    }, 200