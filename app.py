import smtplib
import os

from config import config
from models import db, User
from utils import *

from datetime import datetime
from flask import Flask, request, jsonify, render_template
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import TemplateNotFound
from base64 import b64encode
from threading import Thread
from random import uniform
from os.path import exists

SMTPSERVER = f'{config["smtp"]["hostname"]}:{config["smtp"]["port"]}'
THROTTLE_SECONDS = int(config["throttle"]["seconds"])
THROTTLE_LOW = THROTTLE_SECONDS - (THROTTLE_SECONDS * float(config["throttle"]["jitter"]))
THROTTLE_HIGH = THROTTLE_SECONDS + (THROTTLE_SECONDS * float(config["throttle"]["jitter"]))
BATCH_SIZE = int(config["throttle"]["batch_size"])

EMAIL_THREADS = []

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = config['db']['sqlite']
db.init_app(app)

@app.route("/")
def home():
    db.create_all()
    return "",404


###########################
#### Config Routes ########

@app.route("/config", methods=['GET'])
def list_config():
    """ List configuration options

    Returns:
        json: config.config
    """
    return jsonify(config)

@app.route("/config/update", methods=['POST'])
def update_config():
    data = request.get_json()
    for key in set(config) & set(data):
        print(config[key], data[key])
    return jsonify("ok")


@app.route("/config/payload", methods=['POST'])
def update_payload():
    """ Update the payload file path """
    data = request.get_json()
    file_path = data.get('file_path')
    if file_path:
        
            normalized_path = os.path.normpath(file_path)

            if os.path.exists(normalized_path):
                config['payload_file']['file_path'] = normalized_path
                config['payload_file']['file_name'] = normalized_path.split(os.path.sep)[-1]
            else:
                return jsonify({"error": "file not found"}), 500

    return jsonify("ok")


#####################################
#### User and Group Management Routes

@app.route("/users/load", methods=['POST',])
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


@app.route("/user/<string:uid>", methods=['GET', 'POST'])
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


@app.route("/user/<string:uid>/delete")
def delete_user(uid):
    user = User.query.filter_by(unique_id=uid).first()
    if user:
        user = User.query.filter_by(unique_id=uid).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify("ok")
    else:
        return jsonify({"error":"user not found"})
    

@app.route("/user/<string:uid>/click")
def user_clicked(uid):
    """ Logs that a user clicked on the execution of the page """
    
    user = User.query.filter_by(unique_id=uid).first()

    if user:
        log_write(f'User {user.email} clicked the button and was served the {config["payload_file"]["file_name"]} file.')

        with open(config["payload_file"]["file_path"], 'rb') as f:

            return jsonify(
                    {
                        "data": b64encode(f.read()).decode('utf-8'),
                        "name": config['payload_file']['file_name']
                    }
                )

    return jsonify("ok")
    

@app.route("/users/add", methods=['POST'])
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


@app.route("/users", methods=['GET'])
def get_users():
    """ Gets all users from the database """
    users = User.query.all()

    return jsonify([{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'title': user.title, 'group_name': user.group_name, 'unique_id': user.unique_id, 'sent': user.sent} for user in users])


@app.route("/groups/<string:group_name>")
def get_user_by_group(group_name):
    """ Gets all users with a specific group name """
    users = User.query.filter_by(group_name=group_name).all()
    return jsonify([{'email': user.email, 'unique_id': user.unique_id, 'first_name': user.first_name, 'last_name': user.last_name, 'title': user.title, 'sent':user.sent} for user in users])


@app.route("/groups/<string:group_name>/delete")
def delete_group(group_name):
    users = User.query.filter_by(group_name=group_name).all()
    for user in users:
        db.session.delete(user)
        db.session.commit()
    return jsonify("ok")


@app.route("/groups")
def list_groups():

    data = User.query.with_entities(User.group_name).distinct().all()

    return jsonify([d.group_name for d in data])


@app.route("/search/user/<string:email>", methods=['GET'])
def search_user(email):
    users = User.query.filter(User.email.like(email)).all()
    return jsonify([{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'title': user.title, 'group_name': user.group_name, 'unique_id': user.unique_id, 'sent': user.sent} for user in users])

##############################
#### Sending Management Routes

@app.route("/emails/status", methods=['GET'])
def status():
    ret = []
    for i, thread in enumerate(EMAIL_THREADS):
        if thread.is_alive():
            ret.append({
                f'Thread {i}': 'Running'
            })
    return jsonify(ret)


@app.route("/emails/send", methods=['POST'])
def send():
    data = request.get_json()

    # pretext template should be the name of the file in the templates folder
    pretext_template = data.get('pretext_template')

    if not exists(f'templates/{pretext_template}'):
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
    
    email_thread = Thread(target=send_emails, args=(pretext_template, sender, envelope_sender, subject, users, link_value))
    
    EMAIL_THREADS.append(email_thread)
    
    email_thread.start()
    
    return jsonify(f'thread {len(EMAIL_THREADS) - 1} started')


def send_emails(pretext_template, sender, envelope_sender, subject, users, link_value=""):

    # ensure application context
    with app.app_context():

        # get begin time
        date_begin = datetime.utcnow()

        try:

            # connect to SMTP server
            server = smtplib.SMTP(SMTPSERVER)  # this code assumes you have a postfix server running locally
            
            log_write(f'Connected to SMTP server {SMTPSERVER}')
            
            # perform SMTP EHLO
            log_write(f'Sending server EHLO')

            server.ehlo()

            log_write(f'Sending emails to {len(users)} users.')

            # send for each user in group or all
            for i, user in enumerate(users):
                
                # sleep in seconds 
                throttle = uniform(THROTTLE_LOW, THROTTLE_HIGH)  # Return a random floating point number N such that a <= N <= b for a <= b and b <= N <= a for b < a.

                if i and i % BATCH_SIZE == 0:
                    sleep(throttle)
                
                # render message_data from jinja2 template in templates folder
                message_data = render_template(
                    pretext_template,
                    first_name = user.first_name,
                    last_name = user.last_name,
                    unique_id = user.unique_id,
                    title = user.title,
                    link_value = link_value,
                    date_a = date_begin.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    date_b = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    random_value = generate_random_string(16),
                    random_value_small = generate_random_string(5),
                    file_name = config['payload_file']['file_name'],
                    sha265 = f'{get_payload_hash_sha256()}',
                    file_size = get_payload_file_size(),
                    file_description = "Generic Description of Field rendered within template"
                    )

                email_message = MIMEMultipart()
                email_message['From'] = sender
                email_message['To'] = user.email
                email_message['Subject'] = subject
                email_message['List-Unsubscribe'] = f'<mailto:{envelope_sender}?subject=unsubscribe>'

                if '.html' in pretext_template:
                    email_message.attach(MIMEText(message_data, 'html'))
                else:
                    email_message.attach(MIMEText(message_data, 'plain'))
                
                message = email_message.as_string()

                # set envelope sender (pass SPF)
                server.mail(f"<{envelope_sender}>")

                # set recipient
                server.rcpt(user.email)

                log_write(f'Sending email to "{user.email}" - {pretext_template} - "{subject}" - "{sender}" [{i}/{len(users)-1}]')
                
                # set the message data
                server.data(message)

                # set sent to true for this user
                User.query.filter_by(unique_id=user.unique_id).update(dict(sent=True))
                db.session.commit()
                
            # done
            log_write(f'Sending completed.')
            server.quit()
            
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, smtplib.SMTPResponseException, smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused) as e:
            log_write(f'[SMTP] An error occured: {e}')