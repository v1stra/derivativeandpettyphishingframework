from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import Options
from .sender import Sender

db = SQLAlchemy()

sender = Sender(Options["threads"], Options["throttle"]["seconds"], Options["throttle"]["jitter"])

def register_blueprints(app):

    from .routes import options_bp
    from .routes import groups_bp
    from .routes import emails_bp
    from .routes import users_bp
    from .routes import search_bp
    from .routes import templates_bp

    app.register_blueprint(options_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(emails_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(templates_bp)


def create_app():

    app = Flask(__name__)
    app.config ['SQLALCHEMY_DATABASE_URI'] = Options['db']['sqlite']
    db.init_app(app)

    register_blueprints(app)

    with app.app_context():
        db.create_all()

    sender.run()

    return app

