from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms import ValidationError, validators
from wtforms.validators import Email, DataRequired, EqualTo

from app.base.models import User


class UserForm(FlaskForm):
    first_name = StringField("Prénom",
                             validators=[DataRequired()])
    last_name = StringField("Nom",
                            validators=[DataRequired()])

    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe',
                             id='pwd_create',
                             validators=[DataRequired(),
                                         EqualTo('confirm_password',
                                                 message='Le mot de passe de confirmation est incorrect'),
                                         validators.Length(min=8,
                                                           message='Mot de passe doit '
                                                                   'contenir au moins 8 caractère !')])
    confirm_password = PasswordField('Confirm Password')
    is_admin = BooleanField('Administrateur', default=False)
    is_active = BooleanField('Activer', default=True)

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Cet email est déjà enregistré !')


class EditUserForm(FlaskForm):
    first_name = StringField("Prénom",
                             validators=[DataRequired()])
    last_name = StringField("Nom",
                            validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    is_admin = BooleanField('Administrateur', default=False)
    is_active = BooleanField('Activer', default=True)
