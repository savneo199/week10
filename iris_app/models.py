from iris_app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Iris(db.Model):
    """Iris class"""

    __tablename__ = "iris"
    rowid = db.Column(db.Integer, primary_key=True)
    sepal_length = db.Column(db.Float, nullable=False)
    sepal_width = db.Column(db.Float, nullable=False)
    petal_length = db.Column(db.Float, nullable=False)
    petal_width = db.Column(db.Float, nullable=False)
    species = db.Column(db.Text, nullable=False)

    def __repr__(self):
        """
        Returns the attributes of an iris as a string
        :returns str
        """
        clsname = self.__class__.__name__
        return f"{clsname}: <{self.sepal_length}, {self.sepal_width}, {self.petal_length}, {self.petal_width}, {self.species}>"


class User(UserMixin, db.Model):
    """Class to represent users who have created a login"""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

    def __init__(self, email: str, password: str):
        """
        Create a new User object hashing the plain text password.
        """
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check the plain text password matches the hashed password

        :return Boolean:
        """
        return check_password_hash(self.password, password)

    def __repr__(self):
        """
        Returns the attributes of a User as a string, except for the password
        :returns str
        """
        clsname = self.__class__.__name__
        return f"{clsname}: <{self.id}, {self.email}>"
