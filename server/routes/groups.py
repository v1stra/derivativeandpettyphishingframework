from flask import Blueprint, jsonify

from ..utils import *
from ..models import User

from .. import db

bp = Blueprint('groups', __name__)

@bp.route("/groups/<string:group_name>")
def get_user_by_group(group_name):
    """ Gets all users with a specific group name """
    users = User.query.filter_by(group_name=group_name).all()
    return jsonify([{'email': user.email, 'unique_id': user.unique_id, 'first_name': user.first_name, 'last_name': user.last_name, 'title': user.title, 'sent':user.sent} for user in users])


@bp.route("/groups/<string:group_name>/delete")
def delete_group(group_name):
    users = User.query.filter_by(group_name=group_name).all()
    for user in users:
        db.session.delete(user)
        db.session.commit()
    return jsonify("ok")


@bp.route("/groups")
def list_groups():
    data = User.query.with_entities(User.group_name).distinct().all()

    return jsonify([d.group_name for d in data])
