from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from base64 import b64encode

from ..utils import *
from ..config import Config
from ..models import User

from .. import db

bp = Blueprint('users', __name__)

@bp.route("/users/load", methods=['POST',])
def load_users():
    """
    Loads users from json data - generates a random string for unique_id
    inputs:
        [ user ]
        user:
            first_name
            last_name
            title (nullable)
            email
            group_name
    outputs:
        [ uid: email ]
    """
    data = request.get_json()
    resp = []
    if type(data) == type(resp):
        for user_data in data:
                first_name = user_data.get('first_name')
                last_name = user_data.get('last_name')
                title = user_data.get('title')
                email = user_data.get('email')
                group_name = user_data.get('group_name')
                unique_id = generate_random_string(16)

                try:
                    user = User(first_name=first_name, last_name=last_name, title=title, email=email, group_name=group_name, unique_id=unique_id)
                    db.session.add(user)
                    db.session.commit()
                except IntegrityError as e:
                    return jsonify({'error':e._message()})
                resp.append({'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'title': user.title, 'group_name': user.group_name, 'unique_id': user.unique_id})
                #resp.append({'id': user.id, 'email': user.email, 'unique_id': user.unique_id})
    else:
        return jsonify({"error":"incorrect format"})
    return jsonify(f'{len(resp)} users loaded')


@bp.route("/user/<string:uid>", methods=['GET', 'POST'])
def get_user(uid):
    """ Gets information about a user from uid """
    
    user = User.query.filter_by(unique_id=uid).first()

    if request.method == 'POST':

        data = request.get_data()

        log_write(f'User {user.email} navigated to the landing page. Data: [{data.decode("utf-8")}]')
    
    if user:
        return jsonify({'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'title': user.title, 'group_name': user.group_name, 'unique_id': user.unique_id, 'sent': user.sent})
    else:
        return jsonify({'error':"user not found"})


@bp.route("/user/<string:uid>/delete")
def delete_user(uid):
    user = User.query.filter_by(unique_id=uid).first()
    if user:
        user = User.query.filter_by(unique_id=uid).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify("ok")
    else:
        return jsonify({"error":"user not found"})
    

@bp.route("/user/<string:uid>/click")
def user_clicked(uid):
    """ Logs that a user clicked on the execution of the page """
    
    user = User.query.filter_by(unique_id=uid).first()

    if user:
        log_write(f'User {user.email} clicked the button and was served the {Config["payload_file"]["file_name"]} file.')

        with open(Config["payload_file"]["file_path"], 'rb') as f:

            return jsonify(
                    {
                        "data": b64encode(f.read()).decode('utf-8'),
                        "name": Config['payload_file']['file_name']
                    }
                )

    return jsonify("ok")
    

@bp.route("/users/add", methods=['POST'])
def add_user():
    """
    Adds an individual user
    inputs:
        first_name
        last_name
        title (nullable)
        email
        group_name
    outputs:
        uid
    """
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    title = data.get('title')
    email = data.get('email')
    group_name = data.get('group_name')
    unique_id = generate_random_string(16)

    if not all([first_name, last_name, email, group_name]):
        return jsonify({'error':'missing required fields'})
    try:
        user = User(first_name=first_name, last_name=last_name, title=title, email=email, group_name=group_name, unique_id=unique_id)
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        return jsonify({'error':e._message()})
    return jsonify({'uid': unique_id})


@bp.route("/users", methods=['GET'])
def get_users():
    """ Gets all users from the database """
    users = User.query.all()

    return jsonify([{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'title': user.title, 'group_name': user.group_name, 'unique_id': user.unique_id, 'sent': user.sent} for user in users])
