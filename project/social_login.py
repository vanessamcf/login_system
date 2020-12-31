from flask import Flask, render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user, login_user, login_required
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from . import db
from .models import User, OAuth

github_blueprint = make_github_blueprint(client_id = 'YOUR CLIENT ID', client_secret = 'YOUR CLIENT SECRET')

google_blueprint = make_google_blueprint(client_id= "YOUR CLIENT ID", client_secret= "YOUR CLIENT SECRET",  scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
)

facebook_blueprint = make_facebook_blueprint(client_id= "YOUR CLIENT ID", client_secret= "YOUR CLIENT SECRET", scope = [
    "email"
    ]
)

github_bp = make_github_blueprint(storage = SQLAlchemyStorage(OAuth, db.session, user = current_user))

google_bp = make_google_blueprint(storage = SQLAlchemyStorage(OAuth, db.session, user = current_user))

facebook_bp = make_facebook_blueprint(storage = SQLAlchemyStorage(OAuth, db.session, user = current_user))

@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with GitHub.", category = "error")
        return
    resp = blueprint.session.get("/user")
    if not resp.ok:
        msg = "Failed to fecth user info from GitHub."
        flash(msg, category= "error")
        return
    github_info = resp.json()
    github_user_id = str(github_info["id"])

    query = OAuth.query.filter_by(
        provider = blueprint.name, provider_user_id = github_user_id)
    try:
        oauth = query.one()
    except NoResultFound:
        github_user_login = str(github_info["login"])
        oauth = OAuth(
            provider = blueprint.name,
            provider_user_id = github_user_id,
            provider_user_login = github_user_login,
            token = token,
        )

    if current_user.is_anonymous:
        if oauth.user:
            login_user(oauth.user)
            flash("Successfully signed in with GitHub.")
        else:
            user = User(username = github_info["login"])
            oauth.user = user
            db.session.add_all([user, oauth])
            db.session.commit()
            login_user(user)
            flash("Successfully signed in with GitHub.")
    else:
        if oauth.user:
            if current_user != oauth.user:
                url = url_for("auth.merge", username = oauth.user.username)
                return redirect(url)
        else:
            oauth.user =current_user
            db.session.add(oauth)
            db.session.commit()
            flash("Successfully linked GitHub account.")

    return redirect(url_for("main.profile"))                        

    # return False

@oauth_error.connect_via(github_blueprint)
def github_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response = {response}").format(
        name = blueprint.name, message = message, response = response
    )            
    flash(msg, category="error") 

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flask("Failed to log in.", category="error")
        return 
    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        return

    google_info = resp.json()
    google_user_id = google_info["id"]

    query = OAuth.query.filter_by(
        provider = blueprint.name, provider_user_id = google_user_id
    )    
    try:
        oauth = query.one()
    except NoResultFound:
        google_user_login = str(google_info["email"])
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            provider_user_login=google_user_login,
            token=token,
        )
    if current_user.is_anonymous:        
        if oauth.user:
            login_user(oauth.user)
            flash("Successfully signed in with Google.")
        else:
            user = User(username = google_info["email"])
            oauth.user = user
            db.session.add_all([user, oauth])
            db.session.commit()
            login_user(user)
            flash("Successfully signed in with Google.")
    else:
        if oauth.user:
            if current_user != oauth.user:
                url = url_for("auth.merge", username=oauth.user.username)
                return redirect(url)
        else:
            oauth.user = current_user
            db.session.add(oauth)
            db.commit()
            flash("Successfully linked Google account.")

    return redirect(url_for("main.profile"))                        

@oauth_error.connect_via(google_blueprint)
def google_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message = message, response = response
    )    
    flash(msg, category = "error")

@oauth_authorized.connect_via(facebook_blueprint)
def facebook_logged_in(blueprint,token):
    if not token:
        flash("Failed to log in {name}".format(name = blueprint.name))
        return
    resp = blueprint.session.get("/me")
    if resp.ok:
        facebook_username = resp.json()["name"]    
        query = User.query.filter_by(username =facebook_username)
        try:
            user = query.one()
        except NoResultFound:
            user = User(username = facebook_username)
            oauth.user = user
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Successfully signed in with Facebook.")
    else:
        msg = "Failed to fetch user info from {name}".format(name = blueprint.name)
        flash(msg, category="error")
    return redirect(url_for("main.profile"))                        

@oauth_error.connect_via(facebook_blueprint)
def facebook_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")                 
