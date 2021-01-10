from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os 

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

def create_app():
  app = Flask(__name__)

  app.config['SECRET_KEY'] = 'key-goes-here'
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
  app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
  app.config['MAIL_PORT'] = 587
  app.config['MAIL_USE_TLS'] = True
  app.config['MAIL_USERNAME'] = 'username@gmail.com'
  app.config['MAIL_PASSWORD'] = "password"

  db.init_app(app)

  login_manager = LoginManager()
  login_manager.login_view = 'auth.login'
  login_manager.init_app(app)

  jwt.init_app(app)
  mail.init_app(app)

  from .models import User, OAuth

  @login_manager.user_loader
  def load_user(user_id):
    return User.query.get(int(user_id))

  #blueprints auth routes
  from .auth import auth as auth_blueprint
  app.register_blueprint(auth_blueprint)

  from .social_login import github_blueprint
  app.register_blueprint(github_blueprint, url_prefix = "/login")

  from .social_login import google_blueprint
  app.register_blueprint(google_blueprint, url_prefix = "/login")

  from .social_login import facebook_blueprint
  app.register_blueprint(facebook_blueprint, url_prefix = "/login")

  #non-auth parts
  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint)

  return app