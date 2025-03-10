import os

from flask import Blueprint, jsonify

from ..utils import get_file_sha256, get_file_size, get_template_variables

bp = Blueprint('templates', __name__)

TEMPLATES_FOLDER = 'server/templates/'

@bp.route('/templates', methods=['GET'])
def get_templates():
    dir = os.listdir('server/templates/')
    return jsonify(dir), 200

@bp.route('/templates/<template_name>', methods=['GET'])
def get_template_info(template_name):
    path = f"{TEMPLATES_FOLDER}/{template_name}"
    if os.path.exists(path):
        template_info = {
            "path": path,
            "size": get_file_size(path),
            "sha256": get_file_sha256(path),
            "variables": get_template_variables(path)
        }
        return jsonify(template_info), 200
    return jsonify(""), 404