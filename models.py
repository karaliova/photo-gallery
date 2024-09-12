from db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(300), nullable=False)
    likes = db.Column(db.Integer, default=0)
