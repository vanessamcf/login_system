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

    github_name = resp.json()["name"]
    github_user_id = resp.json()["id"]

    query = OAuth.query.filter_by(
        provider = blueprint.name, provider_user_id = github_user_id)
    try:
        oauth = query.one()
    except NoResultFound:
        github_user_login = github_name
        oauth = OAuth(
            provider = blueprint.name,
            provider_user_id = github_user_id,
            provider_user_login = github_user_login,
            token = token,
        )

    if current_user.is_anonymous:
        if oauth.user:
            login_user(oauth.user)
            # flash("Successfully signed in with GitHub.", 'success')
        else:
            user = User(username = github_name)
            oauth.user = user
            db.session.add_all([user, oauth])
            db.session.commit()
            login_user(user)
            # flash("Successfully signed in with GitHub.", 'success')
    else:
        if oauth.user:
            if current_user != oauth.user:
                url = url_for("auth.merge", username = oauth.user.username)
                return redirect(url)
        else:
            oauth.user =current_user
            db.session.add(oauth)
            db.session.commit()
            # flash("Successfully linked GitHub account.", 'success')

    return redirect(url_for("main.profile"))                        

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

    google_name = resp.json()["name"]
    google_user_id = resp.json()["id"]

    query = OAuth.query.filter_by(
        provider = blueprint.name, provider_user_id = google_user_id
    )    
    try:
        oauth = query.one()
    except NoResultFound:
        google_user_login = google_name

        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            provider_user_login=google_user_login,
            token=token,
        )
    if current_user.is_anonymous:        
        if oauth.user:
            login_user(oauth.user)
            # flash("Successfully signed in with Google.", 'success')
        else:
            user = User(username = google_name)

            oauth.user = user
            db.session.add_all([user, oauth])
            db.session.commit()
            login_user(user)
            # flash("Successfully signed in with Google.", 'success')
    else:
        if oauth.user:
            if current_user != oauth.user:
                url = url_for("auth.merge", username=oauth.user.username)
                return redirect(url)
        else:
            oauth.user = current_user
            db.session.add(oauth)
            db.commit()
            # flash("Successfully linked Google account.")

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
        flash("Failed to log in.", category="error")
        return 

    resp = blueprint.session.get("/me")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        return 

    facebook_name = resp.json()["name"]
    facebook_user_id = resp.json()["id"]

    query = OAuth.query.filter_by(
        provider = blueprint.name, 
        provider_user_id = facebook_user_id
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider = blueprint.name, 
            provider_user_id = facebook_user_id, 
            token = token
        )

    if oauth.user:
        login_user(oauth.user)
        # flash("Successfully signed in with Facebook.", 'success')
    else:
        user = User(username = facebook_name)
        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        # flash("Successfully signed in with Facebook.", 'success')
    return redirect(url_for("main.profile"))                   

@oauth_error.connect_via(facebook_blueprint)
def facebook_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")                 
