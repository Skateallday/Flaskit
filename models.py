from flask_sqlalchemy import SQLAlchemy
from app import db

db = SQLAlchemy()


subs = db.table('subs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
    db.Column('follower_id', db.Integer, db.ForeignKey('follower.follower_id'))
    )

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    subscriptions = db.relationship('follower', secondary=subs, backref=db.backref('subscribers', lazy='dynamic'))

class follower(db.Model):
    follower_id= db.Column(db.Integer, primary_key=True)
    follower_name = db.Column(db.String(20))



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(8))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime,
                           default=db.func.now(),
                           onupdate=db.func.now())

    def __repr__(self):
        return '<Post %r>' % self.id