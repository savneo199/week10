from datetime import datetime, timedelta
import jwt
from functools import wraps
from flask import (
    request,
    make_response,
    jsonify,
    Blueprint,
    current_app as app,
)
from paralympic_app.models import User
from paralympic_app import db
from paralympic_app.models import Region, Event
from paralympic_app.schemas import RegionSchema, EventSchema
from paralympic_app.utilities import get_event, get_events


# Blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")


# Schemas
regions_schema = RegionSchema(many=True)
region_schema = RegionSchema()
events_schema = EventSchema(many=True)
event_schema = EventSchema()


# Custom decorator
def token_required(f):
    """Require valid jwt for a route

    Decorator to protect routes using jwt
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            response = {"message": "Token invalid"}
            return make_response(response, 401)
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            user = db.session.execute(
                db.select(User).filter_by(email=data.get("email"))
            ).scalar_one_or_none()
        except Exception as err:
            response = {"message": "Token invalid"}
            return make_response(response, 401)
        return f(user, *args, **kwargs)

    return decorator


# API Routes
@api_bp.get("/noc")
def noc():
    """Returns a response that conatins a list of NOC region codes and their details in JSON.

    A success response status code is 200 OK.
    """

    # Query using the syntax in the Flask-SQLAlchemy 3.x documentation
    # https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/queries/#select
    all_regions = db.session.execute(db.select(Region)).scalars()
    # Get the data using Marshmallow schema
    result = regions_schema.dump(all_regions)
    response = make_response(result, 200)
    response.headers["Content-Type"] = "application/json"
    return response


@api_bp.get("/noc/<code>")
def noc_code(code):
    """Returns the details for a given region code."""
    # Return a 404 code if the region is not found in the database
    region = db.session.execute(
        db.select(User).filter_by(NOC=code)
    ).one_or_none()
    if region:
        result = region_schema.dump(region)
        response = make_response(result, 200)
        response.headers["Content-Type"] = "application/json"
    else:
        message = jsonify(
            {
                "status": 404,
                "error": "Not found",
                "message": "Invalid resource URI",
            }
        )
        response = make_response(message, 404)
    return response


@api_bp.post("/noc")
def noc_add():
    """Adds a new NOC record to the dataset."""
    NOC = request.json.get("NOC", "")
    region = request.json.get("region", "")
    notes = request.json.get("notes", "")
    region = Region(NOC=NOC, region=region, notes=notes)
    db.session.add(region)
    db.session.commit()
    result = region_schema.jsonify(region)
    response = make_response(result, 201)
    response.headers["Content-type"] = "application/json"
    return response


@api_bp.patch("/noc/<code>")
def noc_update(code):
    """Updates changed fields for the NOC record"""
    # https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/queries/#insert-update-delete
    # Find the current region in the database
    existing_region = db.one_or_404(db.select(Region).filter_by(NOC=code))
    # Get the updated details from the json sent in the HTTP patch request
    region_json = request.get_json()
    # Use Marshmallow to update the existing records with the changes in the json
    region_schema.load(region_json, instance=existing_region, partial=True)
    # Commit the changes to the database
    db.session.commit()
    # Return json showing the updated record
    existing_region = db.one_or_404(db.select(Region).filter_by(NOC=code))
    result = region_schema.jsonify(existing_region)
    response = make_response(result, 200)
    response.headers["Content-Type"] = "application/json"
    return response


@api_bp.delete("/noc/<code>")
@token_required
def noc_delete(code):
    """Removes a NOC record from the dataset."""
    region = db.one_or_404(db.select(Region).filter_by(NOC=code))
    db.session.delete(region)
    db.session.commit()
    # This example returns a custom HTTP response using flask make_response
    # https://flask.palletsprojects.com/en/2.2.x/api/?highlight=make_response#flask.make_response
    text = jsonify({"Successfully deleted": region.NOC})
    response = make_response(text, 200)
    response.headers["Content-type"] = "application/json"
    return response


@api_bp.get("/event")
def event():
    """Returns the details for all events"""
    result = get_events()
    response = make_response(result, 200)
    response.headers["Content-Type"] = "application/json"
    return response


@api_bp.get("/event/<int:event_id>")
def event_id(event_id):
    """Returns the details for a specified event"""
    result = get_event(event_id)
    if result:
        response = make_response(result, 200)
        response.headers["Content-Type"] = "application/json"
    else:
        message = jsonify(
            {
                "status": 404,
                "error": "Not found",
                "message": "Invalid resource URI",
            }
        )
        response = make_response(message, 404)
    return response


@api_bp.post("/event")
def event_add():
    """Adds a new event record to the dataset."""
    type = request.json.get("type")
    year = request.json.get("year")
    location = request.json.get("location")
    lat = request.json.get("lat")
    lon = request.json.get("lon")
    NOC = request.json.get("NOC")
    start = request.json.get("start")
    end = request.json.get("end")
    disabilities_included = request.json.get("disabilities_included")
    events = request.json.get("events")
    sports = request.json.get("sports")
    countries = request.json.get("countries")
    male = request.json.get("male")
    female = request.json.get("female")
    participants = request.json.get("participants")
    highlights = request.json.get("highlights")

    event = Event(
        type=type,
        year=year,
        location=location,
        lat=lat,
        lon=lon,
        NOC=NOC,
        start=start,
        end=end,
        disabilities_included=disabilities_included,
        events=events,
        sports=sports,
        countries=countries,
        male=male,
        female=female,
        participants=participants,
        highlights=highlights,
    )
    db.session.add(event)
    db.session.commit()
    result = event_schema.jsonify(event)
    response = make_response(result, 201)
    response.headers["Content-Type"] = "application/json"
    return response


@api_bp.patch("/event/<event_id>")
def event_update(event_id):
    """Updates changed fields for the event
    TODO: does not handle a partial update despite partial=True
    """
    # Find the current event in the database
    existing_event = db.session.execute(
        db.select(User).filter_by(event_id=event_id)
    ).one_or_none()

    if existing_event:
        # Get the updated details from the json sent in the HTTP patch request
        event_json = request.get_json()
        # Use Marshmallow to update the existing records with the changes in the json
        event_schema.load(event_json, instance=existing_event, partial=True)
        # Commit the changes to the database
        db.session.commit()
        # Return json showing the updated record
        updated_event = db.session.execute(
            db.select(User).filter_by(event_id=event_id)
        ).one_or_none()
        result = event_schema.jsonify(updated_event)
        response = make_response(result, 200)
        response.headers["Content-Type"] = "application/json"
    else:
        message = jsonify(
            {
                "status": 404,
                "error": "Not found",
                "message": "Invalid resource URI",
            }
        )
        response = make_response(message, 404)
    return response


@api_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user for the REST API"""
    # Get the JSON data from the request
    post_data = request.get_json()
    # Check if user already exists, returns None if the user does not exist
    user = db.session.execute(
        db.select(User).filter_by(email=post_data.get("email"))
    ).scalar_one_or_none()
    if not user:
        try:
            user = User(
                email=post_data.get("email"),
                password=post_data.get("password"),
            )
            # Add user to the database
            db.session.add(user)
            db.session.commit()
            # Return success message
            response = {
                "status": "success",
                "message": "Successfully registered.",
            }
            return make_response(jsonify(response)), 201
        except Exception as err:
            response = {
                "status": "fail",
                "message": "An error occurred. Please try again.",
            }
            return make_response(jsonify(response)), 401
    else:
        response = {
            "status": "fail",
            "message": "User already exists. Please Log in.",
        }
        return make_response(jsonify(response)), 202


@api_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login for the REST API"""
    # Get the request JSON data
    data = request.get_json()
    try:
        # Get the user data
        email = data.get("email")
        password = data.get("password")
        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()
        if user and user.check_password(password):
            payload = {
                "exp": datetime.utcnow() + timedelta(minutes=5),
                "iat": datetime.utcnow(),
                "sub": user.id,
            }
            auth_token = jwt.encode(
                payload, app.config.get("SECRET_KEY"), algorithm="HS256"
            )
            # auth_token = user.encode_auth_token(user.id)
            if auth_token:
                response = {
                    "status": "success",
                    "message": "Successfully logged in.",
                }
                return make_response(jsonify(response)), 200
    except Exception as err:
        print(err)
        response = {"status": "fail", "message": "Try again"}
        return make_response(jsonify(response)), 500
