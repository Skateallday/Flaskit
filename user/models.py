from flask_sqlalchemy import SQLAlchemy
from app import db
from app.like.models import *
from app.dislike.models import *
from app.comment.models import *
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    subscriptions = db.relationship('Photo', secondary=subs, backref=db.backref('subscribers', lazy='dynamic'))
    dissubscriptions = db.relationship('Photo', secondary=dissubs, backref=db.backref('dissubscribers', lazy='dynamic'))
    #comsubscriptions = db.relationship('Comment', backref=db.backref('comsubscriber'))
    def __init__(self, username, password, name):
        self.name = name
        self.username = username
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id' : self.id,
            'name': self.name,
            'username': self.username,
        }

    def __repr__(self):
        return "User<%d> %s" % (self.id, self.username)