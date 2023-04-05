from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse, urljoin
import pickle
from flask import (
    render_template,
    current_app as app,
    request,
    flash,
    redirect,
    url_for,
    abort,
)
from flask_login import logout_user, login_required, login_user
import numpy as np
from sqlalchemy.exc import IntegrityError, NoResultFound
from iris_app.forms import LoginForm, PredictionForm, RegisterForm
from iris_app import db, login_manager
from iris_app.models import Iris, User


pickle_file = Path(__file__).parent.joinpath("data", "model_lr.pkl")
IRIS_MODEL = pickle.load(open(pickle_file, "rb"))


@app.route("/", methods=["GET", "POST"])
def index():
    """Create the homepage"""
    form = PredictionForm()

    if form.validate_on_submit():
        # Get all values from the form
        features_from_form = [
            form.sepal_length.data,
            form.sepal_width.data,
            form.petal_length.data,
            form.petal_width.data,
        ]

        # Make the prediction
        prediction = make_prediction(features_from_form)

        prediction_text = f"Predicted Iris type: {prediction}"

        return render_template(
            "index.html", form=form, prediction_text=prediction_text
        )
    return render_template("index.html", form=form)


# The predict route is no longer needed
@app.get("/predict")
def predict():
    """Predict iris species

    Takes the arguments sepal_length,sepal_width,petal_length,petal_width  from an HTTP request. Passes the arguments to the model and returns a prediction (classification of Iris species).

    Returns:
        species(str): A string of the iris species.
    """

    sepal_length = request.args.get("sep-len")
    sepal_width = request.args.get("sep-wid")
    petal_length = request.args.get("pet-len")
    petal_width = request.args.get("pet-wid")

    prediction = make_prediction(
        [sepal_length, sepal_width, petal_length, petal_width]
    )

    return prediction


def make_prediction(flower_values):
    """Takes the flower values, makes a model using the prediction and returns a string of the predicted flower variety

    Parameters:
    flower_values (List): List of sepal length, sepal width, petal length, petal width

    Returns:
    variety (str): Name of the predicted iris variety
    """

    # Convert to a 2D numpy array with float values, needed as input to the model
    input_values = np.asarray([flower_values], dtype=float)

    # Get a prediction from the model
    prediction = IRIS_MODEL.predict(input_values)

    # convert the prediction to the variety name
    varieties = {0: "iris-setosa", 1: "iris-versicolor", 2: "iris-virginica"}
    variety = np.vectorize(varieties.__getitem__)(prediction[0])

    return variety


@app.route("/iris")
def iris_list():
    """Render page with a list of all the iris entries from the database"""
    iris = db.session.execute(db.select(Iris)).scalars()
    return render_template("iris.html", iris_list=iris)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user (save to database)."""
    form = RegisterForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")
        new_user = User(email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            # Remove to replace with Flash message
            # text = f"<p>You are registered! {repr(new_user)}</p>"
            # return text
            text = f"You are registered! {repr(new_user)}"
            flash(text)
            return redirect(url_for("index"))
        except IntegrityError:
            text = "An account with that email exists!"
            flash(text)
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login the user if the password and email are valid."""
    login_form = LoginForm()

    if login_form.validate_on_submit():
        try:
            # Query if the user exists. If not raise a NoResultFound error and return to the login form
            user = db.session.execute(
                db.select(User).filter_by(email=login_form.email.data)
            ).scalar_one()

            if user and user.check_password(login_form.password.data):
                # If the user exists and their password is correct, login the user
                login_user(
                    user,
                    remember=login_form.remember.data,
                    duration=timedelta(minutes=1),
                )
                # If they came to login from another page, return them to that page after login, otherwise go to home
                next = request.args.get("next")
                if not is_safe_url(next):
                    return abort(400)
                return redirect(next or url_for("index"))
            else:
                # Message to show if the password was incorrect
                flash("Incorrect password")
        except NoResultFound:
            flash("Email address not found")
    return render_template("login.html", title="Login", form=login_form)


@app.route("/logout")
@login_required
def logout():
    """Logs out a user if logged in and redirects to the home page."""
    logout_user()
    return redirect(url_for("index"))


@login_manager.user_loader
def load_user(user_id):
    """Takes a user ID and returns a user object or None if the user does not exist"""
    if user_id is not None:
        user = db.get_or_404(User, user_id)
        return user
    return None


def is_safe_url(target):
    """Validate that the URL is from our app"""
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return (
        redirect_url.scheme in ("http", "https")
        and host_url.netloc == redirect_url.netloc
    )


def get_safe_redirect():
    """Safely redirect to another URL. If the URL is not safe, then return to home.

    Uses the is_safe_url function to check that the URL is in your app"""
    url = request.args.get("next")
    if url and is_safe_url(url):
        return url
    url = request.referrer
    if url and is_safe_url(url):
        return url
    return "/"
