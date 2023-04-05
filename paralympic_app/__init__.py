from pathlib import Path
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from paralympic_app.paralympic_dash_app.paralympics_dash_app import (
    create_dash_app,
)

# Sets the project root folder
PROJECT_ROOT = Path(__file__).parent

# Create a global SQLAlchemy object
db = SQLAlchemy()
# Create a global Flask-Marshmallow object
ma = Marshmallow()


def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "YY3R4fQ5OmlmVKOSlsVHew"
    # configure the SQLite database location
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(
        PROJECT_ROOT.joinpath("data", "paralympics.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True

    # Uses a helper function to initialise extensions
    initialize_extensions(app)

    # Creates the User table in the database
    with app.app_context():
        from paralympic_app.models import User

        db.create_all()

    # Include the routes from api_routes.py and main_routes.py
    from paralympic_app.api_routes import api_bp
    from paralympic_app.main_routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app


def initialize_extensions(app):
    """Binds extensions to the Flask application instance (app)"""
    # Flask-SQLAlchemy
    db.init_app(app)
    # Flask-Marshmallow
    ma.init_app(app)
    # Dash app
    create_dash_app(app)
