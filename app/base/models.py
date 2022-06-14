# -*- encoding: utf-8 -*-
from flask_login import UserMixin
from app import db, login_manager

from app.base.tools import hash_pass
import secrets
import datetime


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


# @login_manager.request_loader
# def request_loader(request):
#     username = request.form.get('username')
#     user = User.query.filter_by(username=username).first()
#     return user if user else None


############## MIXINS ##############################################

class TimestampMixin(object):
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

############## Models ##############################################


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True, unique=True)
    last_name = db.Column(db.String(60), index=True, unique=True)
    password = db.Column(db.String(128))
    password_reset_token = db.Column(db.String(128))
    password_reset_expires = db.Column(db.DateTime)
    activation_token = db.Column(db.String(128))

    is_admin = db.Column(db.Boolean, default=False)

    last_seen = db.Column(db.DateTime, server_default=db.func.now())
    is_active = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # hash the password

            setattr(self, property, value)

    def __repr__(self):
        return f"<User {self.id} - {self.email}>"

    def change_password(self, newPassword):
        self.password = hash_pass(newPassword)

    def generate_forgot_token(self):
        token = secrets.token_urlsafe(16)
        token_exp_minutes = 10
        self.password_reset_token = token
        self.password_reset_expires = datetime.datetime.now(
        ) + datetime.timedelta(minutes=token_exp_minutes)

    def generate_activation_token(self):
        token = secrets.token_urlsafe(16)
        self.activation_token = token

    @property
    def get_name(self):
        return f"{self.first_name} {self.last_name}"



