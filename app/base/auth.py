from flask import current_app, redirect, request, url_for, abort
from flask_login import (
    current_user,
    login_user,
)
from flask_restful import Resource

import logging
from app import db
from flask import current_app, session
from app.base.forms import SigninForm, ForgotForm
from app.base.models import User

from app.base.tools import (verify_pass,
                            success_response, fail_response,
                            send_email)
import secrets

# Login & Registration
class Auth(Resource):
    def get(self):
        return redirect(url_for('login'))

    def post(self):

        if current_user.is_authenticated:
            return {'message': 'Already logged in, Please log out before trying again !'}, 200

        data = request.json
        form = SigninForm(data=data)

        if form.validate():
            user = User.query.filter_by(email=form._user.email).first()
            login_user(user)
            return success_response(200)
        return fail_response(401, form.errors)


# Registration not used in this project
# class Register(Resource):
#     def post(self):
#         print(request.headers)
#         data = request.json
#         form = SignupForm(data=data)
#         if form.validate():
#             try:
#                 user = User(email=form.email.data,
#                             # insert User info
#                             password=form.password.data)
#
#                 user.is_active = False
#                 user.active_survey_id = 0
#                 # Generate activation link
#                 user.generate_activation_token()
#                 db.session.add(user)
#                 db.session.commit()
#
#                 url = f'{request.host_url}auth/activateAccount/{user.activation_token}'
#                 mail_subject = "ERP Bâtiment - POC : Activation votre compte !"
#                 mail_content = f"Félicitation ! Votre compte a été crée avec succès, afin" \
#                                f" de l'activer veuillez cliquer sur le lien suivant  : {url}"
#                 mail_content_html = f"Félicitation ! Votre compte a été crée avec succès, afin " \
#                                     f"de l'activer veuillez cliquer sur le lien suivant :" \
#                                     f"<br> <a href='{url}'>Activer votre compte !</a>"
#                 mail_sender = current_app.config['MAIL_DEFAULT_SENDER']
#                 mail_recipts = [user.email]
#
#                 send_email(subject=mail_subject,
#                            sender=mail_sender,
#                            recipients=mail_recipts,
#                            text_body=mail_content,
#                            html_body=mail_content_html)
#             except Exception as e:
#                 logging.error(f"Register Error : {str(e)}")
#                 db.session.rollback()
#                 abort(500)
#
#             return success_response(201)
#         else:
#             return fail_response(400, form.errors)


class PasswordForget(Resource):
    def post(self):
        data = request.json
        form = ForgotForm(data=data)
        if form.validate():
            try:
                # forgot_password()
                user = User.query.filter_by(email=form.email.data).first()
                user.generate_forgot_token()
                db.session.commit()

                url = f'{request.host_url}auth/resetPassword/{user.activation_token}'
                mail_subject = 'Changer votre mot de passe (Link valid for 10 mins)'
                mail_content = f'Pour obtenir un nouveau mot de passe : {url}'
                mail_content_html = f'Pour obtenir un nouveau mot de passe :<br> <a href="{url}">Click here !</a>'
                mail_sender = current_app.config['MAIL_DEFAULT_SENDER']
                mail_recipts = [form.email.data]

                send_email(subject=mail_subject,
                           sender=mail_sender,
                           recipients=mail_recipts,
                           text_body=mail_content,
                           html_body=mail_content_html)
            except Exception as e:
                logging.error(f"PasswordForget Error : {str(e)}")
                db.session.rollback()
                abort(500)

            return success_response(200)
        else:
            return fail_response(400, form.errors)
