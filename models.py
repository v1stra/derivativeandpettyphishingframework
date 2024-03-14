from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column('user_id', db.Integer, primary_key = True)
    unique_id = db.Column(db.String(16), unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    group_name = db.Column(db.String(100))
    title = db.Column(db.String(100))
    sent = db.Column(db.Boolean, default=False)

