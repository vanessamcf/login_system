from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(100))
  firstname = db.Column(db.String(150))
  lastname = db.Column(db.String(150))



# 