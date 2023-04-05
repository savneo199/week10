from flask_wtf import FlaskForm
from wtforms import (
    DecimalField,
    StringField,
    EmailField,
    PasswordField,
    BooleanField,
)
from wtforms.validators import DataRequired, ValidationError
from iris_app.models import User
from iris_app import db


class PredictionForm(FlaskForm):
    """Fields to a form to input the values required for an iris species prediction"""

    # https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.DecimalField
    sepal_length = DecimalField(validators=[DataRequired()])
    sepal_width = DecimalField(validators=[DataRequired()])
    petal_length = DecimalField(validators=[DataRequired()])
    petal_width = DecimalField(validators=[DataRequired()])


class RegisterForm(FlaskForm):
    """Fields to a form to input the values required for adding a new user account"""

    email = EmailField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = EmailField(label="Email address", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    remember = BooleanField(label="Remember me")
