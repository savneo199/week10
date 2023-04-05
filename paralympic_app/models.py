from datetime import datetime, timedelta
import jwt
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
from paralympic_app import db


class Region(db.Model):
    """NOC region"""

    __tablename__ = "region"
    NOC = db.Column(db.Text, primary_key=True)
    region = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    events = db.relationship("Event", back_populates="region")

    def __repr__(self):
        """
        Returns the attributes of the region as a string
        :returns str
        """
        clsname = self.__class__.__name__
        return f"{clsname}: <{self.NOC}, {self.region}, {self.notes}>"


class Event(db.Model):
    """Paralympic event"""

    __tablename__ = "event"
    event_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    location = db.Column(db.Text, nullable=False)
    lat = db.Column(db.Text)
    lon = db.Column(db.Text)
    NOC = db.Column(db.Text, db.ForeignKey("region.NOC"), nullable=False)
    start = db.Column(db.Text, nullable=False)
    end = db.Column(db.Text, nullable=False)
    disabilities_included = db.Column(db.Text, nullable=False)
    events = db.Column(db.Text, nullable=False)
    sports = db.Column(db.Text, nullable=False)
    countries = db.Column(db.Integer, nullable=False)
    male = db.Column(db.Integer, nullable=False)
    female = db.Column(db.Integer, nullable=False)
    participants = db.Column(db.Integer, nullable=False)
    highlights = db.Column(db.Text)
    region = db.relationship("Region", back_populates="events")

    def __repr__(self):
        """
        Returns the attributes of the event as a string
        :returns str
        """
        clsname = self.__class__.__name__
        return f"<{clsname}: {self.type},{self.type}, {self.year}, {self.location}, {self.lat}, {self.lon}, {self.NOC}, {self.start}, {self.end}, {self.disabilities_included}, {self.events}, {self.sports}, {self.countries}, {self.male}, {self.female}, {self.participants}, {self.highlights}>"


class User(db.Model):
    """User model for use with login"""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password)

    def __repr__(self):
        """
        Returns the attributes of a User as a string, except for the password
        :returns str
        """
        clsname = self.__class__.__name__
        return f"{clsname}: <{self.id}, {self.email}>"

    def check_password(self, password):
        """Checks the text matches the hashed password.

        :return: Boolean
        """
        return check_password_hash(self.password, password)

    def encode_auth_token(self, user_id):
        """Generates the auth token
        :return: string
        """
        payload = {
            "exp": datetime.utcnow() + timedelta(minutes=5),
            "iat": datetime.utcnow(),
            "sub": user_id,
        }
        print(payload, file=sys.stderr)
        try:
            return jwt.encode(
                payload, app.config.get("SECRET_KEY"), algorithm="HS256"
            )
        except Exception as err:
            return err

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token.

        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get("SECRET_KEY"))
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return "Token expired. Please log in again."
        except jwt.InvalidTokenError:
            return "Invalid token. Please log in again."
