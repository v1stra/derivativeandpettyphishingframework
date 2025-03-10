from flask import request, jsonify, Blueprint

from ..config import Options

bp = Blueprint('options', __name__)

@bp.route("/")
def home():
    return list_config()

@bp.route("/options", methods=['GET'])
def list_config():
    """ List configuration options """
    return jsonify(Options)

@bp.route("/options/update", methods=['POST'])
def update_config():
    data = request.get_json()
    for key in set(Options) & set(data):
        print(Options[key], data[key])
    return jsonify("ok")
