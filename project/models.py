from . import db
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(100))
  # firstname = db.Column(db.String(150))
  # lastname = db.Column(db.String(150))
  username = db.Column(db.String(150))


class OAuth(OAuthConsumerMixin, db.Model):
  __table_args__ = (db.UniqueConstraint("provider", "provider_user_id"),)
  provider_user_id = db.Column(db.String(256), nullable = False)
  provider_user_login = db.Column(db.String(256), nullable = False)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable = False)
  user = db.relationship(User)

  """

  Update Social login github part: https://github.com/singingwolfboy/flask-dance-multi-provider

  Update models.py OAuth class

  Organize:

  __init__.py
  models.py
  auth.py


  need to remove db and create new again """

