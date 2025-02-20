from flask import Blueprint, jsonify

from ..utils import *
from ..models import User

bp = Blueprint('search', __name__)

@bp.route("/search/user/<string:email>", methods=['GET'])
def search_user(email):
    users = User.query.filter(User.email.like(email)).all()
    return jsonify([{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'title': user.title, 'group_name': user.group_name, 'unique_id': user.unique_id, 'sent': user.sent} for user in users])
