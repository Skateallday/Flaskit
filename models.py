from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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