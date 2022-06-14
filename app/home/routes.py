# -*- encoding: utf-8 -*-

import os
import time
from datetime import datetime
from os import path

import sqlalchemy as sql
from flask import current_app as app
from flask import render_template, redirect, url_for, abort, request, jsonify, flash, send_file
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy.sql.expression import cast

from app.base.models import User
from app.base.tools import send_email
from app.base.orm_tools import FactoryController
from app.home import blueprint
from .forms import UserForm, EditUserForm
from .. import db


@blueprint.route('/index')
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for('home_blueprint.admin_dashboard'))
    else:
        return redirect(url_for('home_blueprint.dashboard'))


@blueprint.route('/administration')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    return render_template('admin_dashboard.html', page='dashboard')


@blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', page='dashboard')


@blueprint.route('/users')
@login_required
def list_users():
    if not current_user.is_admin:
        abort(403)

    count_users = User.query.count()

    return render_template('users_list.html', count_users=count_users, page='list_users')


@blueprint.route('/usersData')
@login_required
def users_data():
    if not current_user.is_admin:
        abort(403)

    users = User.query.all()
    user_array = []
    json_array = []
    for user in users:
        user_obj = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'last_seen': user.last_seen,
            'is_active': user.is_active,
            'is_admin': user.is_admin}

        user_array.append(user_obj)

    return jsonify(user_array)


@blueprint.route('/addUser', methods=['POST', 'GET'])
@login_required
def add_user():
    if not current_user.is_admin:
        abort(403)

    form = UserForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=form.password.data )

        is_admin = form.is_admin.data
        if is_admin:
            user.is_admin = True

        is_active = form.is_active.data
        if is_active:
            user.is_active = True
        else:
            # send verification email to activate the account
            user.generate_activation_token()
            url = f'{request.host_url}auth/activateAccount/{user.activation_token}'
            mail_subject = "ERP BET - POC: Activation de compte !"
            mail_content = f"Votre compte d'analayse salariale a été crée avec succès," \
                           f" afin de l'activer veuillez cliquer sur le lien suivant  : {url}"
            mail_content_html = f"Votre compte d'analayse salariale a été crée avec succès," \
                                f" afin de l'activer veuillez cliquer sur le lien suivant   :<br>" \
                                f" <a href='{url}'>Activer votre compte !</a>"
            mail_sender = app.config['MAIL_DEFAULT_SENDER']
            mail_recipts = [user.email]
            try:
                send_email(subject=mail_subject,
                           sender=mail_sender,
                           recipients=mail_recipts,
                           text_body=mail_content,
                           html_body=mail_content_html)
            except Exception as e:
                return render_template('add_user.html', edit=False, form=form, msg=f'Erreur server email {str(e)}')

        FactoryController.createOne(user)

        return redirect(url_for('home_blueprint.list_users'))

    return render_template('add_user.html', edit=False, form=form)


@blueprint.route('/editUser/<int:user_id>', methods=['POST', 'GET'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():

        email = form.email.data
        if email != user.email:
            usr = User.query.filter_by(email=email).first()
            if usr:
                return render_template('add_user.html',
                                       edit=True, form=form,
                                       msg="Cette adresse email existe déjà dans la base donnée")
        else:
            user.email = email

        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        FactoryController.commit()

        return redirect(url_for('home_blueprint.list_users'))

    return render_template('add_user.html', edit=True, form=form)


@blueprint.route('/deleteUser/<int:user_id>', methods=['POST', 'GET'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    if current_user.id == user.id:
        jsonify(status='ERROR', message='Impossible de supprimer cet utilisateur')

    FactoryController.deleteOne(user)

    return jsonify(status='OK')


