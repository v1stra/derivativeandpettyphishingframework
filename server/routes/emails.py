from os.path import exists

from flask import Blueprint, request, jsonify, render_template

from ..utils import *
from ..models import User
from .. import sender as email_sender

bp = Blueprint('emails', __name__)

@bp.route("/emails/send", methods=['POST'])
def send():
    data = request.get_json()

    # pretext template should be the name of the file in the templates folder
    pretext_template = data.get('pretext_template')

    if not exists(f'server/templates/{pretext_template}'):
        return jsonify({'error': f'pretext template "templates/{pretext_template}" not found. Typo? Fat fingers?'})

    # this is he sender that the user sees
    sender = data.get('sender')

    # this is the sender in the envelope (user does not see this)
    envelope_sender = data.get('envelope_sender')

    # subject of the email
    subject = data.get('subject')

    # this is the value of the link (https://example.com/test.php)
    link_value = data.get('link_value')

    # this is the group name for users, if omitted, all users will be sent to
    group_name = data.get('group_name')

    if not all([sender, subject, envelope_sender, pretext_template]):
        return jsonify({'error': 'missing required fields'})
    
    # check if group_name was provided
    if group_name:
        users = User.query.filter_by(group_name=group_name, sent=False).all()
    else:
        users = User.query.all()

    if not users:
        return jsonify({"error":"no users found"})

    log_write(f'Loaded {len(users)} users for sending from group {group_name}')

    for user in users:

        # These are the variables that can be used in the jinja template
        template_opts = {
            
            'first_name': user.first_name,
            'last_name': user.last_name,
            'unique_id': user.unique_id,
            'user_title': user.title,
            'link_value': link_value,
            'date_now_1': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            'date_now_2': datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            'random_value_16': generate_random_string(16),
            'random_value_5': generate_random_string(5),
            'file_name': Config['payload_file']['file_name'],
            'sha265': f'{get_payload_hash_sha256()}',
            'file_size': get_payload_file_size(),
            'file_description': "Generic Description of Field rendered within template",
        }

        body = render_template(
            pretext_template,
            **template_opts
        )

        print(body)

        mime_type = 'html' if '.html' in pretext_template else 'txt'

        email_sender.enqueue(body, user.email, sender, envelope_sender, subject, link_value, mime_type)

        return jsonify("", 200)
