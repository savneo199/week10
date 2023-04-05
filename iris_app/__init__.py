from pathlib import Path
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# Iris app folder
PROJECT_ROOT = Path(__file__).parent

# Create a global SQLAlchemy object
db = SQLAlchemy()

# Create Flask-Login
login_manager = LoginManager()


# Custom error routes
def internal_server_error(e):
    return render_template("500.html"), 500


def page_not_found(e):
    return render_template("404.html"), 404


def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "saULPgD9XU8vzLVk7kyLBw"
    # configure the SQLite database location
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(
        PROJECT_ROOT.joinpath("data", "iris.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False

    # Register error handlers
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(404, page_not_found)

    # Bind the Flask-SQLAlchemy instance to the Flask app
    db.init_app(app)

    # Register the login manager and set the default view for login
    login_manager.login_view = "login"
    login_manager.init_app(app)

    # Include the routes from routes.py
    with app.app_context():
        from . import routes

        # Create the tables in the database if they do not already exist
        from .models import Iris

        db.create_all()

    return app
