from flask import Flask
from flask_cors import CORS

from config import Config
from app.extensions import db, migrate, jwt

# Models
from app.models.user import User
from app.models.ride import Ride
from app.models.payment import Payment
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.ride_request import RideRequest

# Routes
from app.routes.auth import auth_bp
from app.routes.ride import ride_bp
from app.routes.payment import payment_bp
from app.routes.driver import driver_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # Enable CORS
    CORS(
        app,
        origins=["http://localhost:5173",
        "https://robertride-frontend.vercel.app"         
                 ]
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(ride_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(driver_bp)

    @app.route("/")
    def home():
        return {
            "message": "RobertRide API is running"
        }

    return app