import os
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get(
    "1090468009131-v3t7df612bj0nc8vu4k60a84hq5f4h46.apps.googleusercontent.com")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get(
    "jh7OELB0RukDRUmYvFWNWhCh")
google_bp = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(google_bp, url_prefix="/google_login")



# {"web":{"client_id":"1090468009131-v3t7df612bj0nc8vu4k60a84hq5f4h46.apps.googleusercontent.com","project_id":"loginsystem-295200","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"jh7OELB0RukDRUmYvFWNWhCh","redirect_uris":["http://localhost:5000/login/google/authorized"],"javascript_origins":["http://127.0.0.1:5000"]}}


app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get("300ab5a1b76f4420643e")
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get(
    "a198ffb6c4af22313fbc16ae0785ed47e2e65d5b")
github_bp = make_github_blueprint()
app.register_blueprint(github_bp, url_prefix="/github_login")

app.config["FACEBOOK_OAUTH_CLIENT_ID"] = os.environ.get("375263070388104")
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = os.environ.get("1ec14db8d4328b566c6c8b972b24bbfc")
facebook_bp = make_facebook_blueprint()
app.register_blueprint(facebook_bp, url_prefix = "/facebook_login")


@app.route('/google')
def gconnect():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    assert resp.ok, resp.text
    return "Your are {email} on Google".format(email=resp.json()["email"])


@app.route('/github')
def ghconnect():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get('/user')
    assert resp.ok
    return "You are @{login} on GitHub".format(login=resp.json()["login"])


@app.route('/facebook')
def fconnect():
  if not facebook.authorized:
    return redirect(url_for("facebook.login"))
  resp = facebook.get("/me")
  assert resp.ok, resp.text
  return "You are {name} on Facebook".format(name=resp.json()["name"])  