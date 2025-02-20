import os

from flask import request, jsonify, Blueprint

from ..config import Config

bp = Blueprint('config', __name__)

@bp.route("/")
def home():
    return list_config()

@bp.route("/config", methods=['GET'])
def list_config():
    """ List configuration options

    Returns:
        json: config.config
    """
    return jsonify(Config)

@bp.route("/config/update", methods=['POST'])
def update_config():
    data = request.get_json()
    for key in set(Config) & set(data):
        print(Config[key], data[key])
    return jsonify("ok")


@bp.route("/config/payload", methods=['POST'])
def update_payload():
    """ Update the payload file path """
    data = request.get_json()
    file_path = data.get('file_path')
    if file_path:
        
            normalized_path = os.path.normpath(file_path)

            if os.path.exists(normalized_path):
                Config['payload_file']['file_path'] = normalized_path
                Config['payload_file']['file_name'] = normalized_path.split(os.path.sep)[-1]
            else:
                return jsonify({"error": "file not found"}), 500

    return jsonify("ok")

