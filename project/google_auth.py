# import json
# import os
# from oauthlib.oauth2 import WebApplicationClient
# import requests


# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
# GOOGLE_DISCOVERY_URL = (
#     "https://accounts.google.com/.well-known/openid-configuration"
# )

# @app.route('/gconnect')
# def gconnect():
#     redirect_uri = url_for('authorize', _external=True)
#     return oauth.twitter.authorize_redirect(redirect_uri)

# @app.route('/authorize')
# def authorize():
#     token = oauth.twitter.authorize_access_token()
#     resp = oauth.twitter.get('userinfo')
#     user_info = resp.json()
#     # do something with the token and profile
#     return redirect('/')


# FLASK DANCE
import os 
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
google_bp = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(google_bp, url_prefix="/gconnect")

@app.route('/gconnect')
def gconnect():
  if not google.authorized:
    return redirect(url_for("google.login"))
  resp = google.get("/oauth2/v1/userinfo")
  assert resp.ok, resp.text 
  return "Your are {email} on Google".format(email = resp.json()["email"])

