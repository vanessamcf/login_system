from flask import Blueprint, render_template, redirect, url_for, request, flash 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User, OAuth
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
  return render_template('login.html') #inform data

@auth.route('/login', methods=['POST']) #get data and redirect to profile
def login_post():
  email = request.form.get('email')
  password = request.form.get('password')
  remember = True if request.form.get('remember') else False

  user = User.query.filter_by(email=email).first()

  if not user or not check_password_hash(user.password, password):
      flash('Please check your login details and try again.')
      return redirect(url_for('auth.login'))

#if the user has the right credentials
  login_user(user, remember=remember)
  return redirect(url_for('main.profile')) 

@auth.route('/signup')
def signup():
  return render_template('signup.html')
  
@auth.route('/signup', methods=['POST'])
def signup_post():
  # code to validate and add user to db goes here
  username = request.form.get('username')
  email = request.form.get('email')
  password = request.form.get('password')

  user = User.query.filter_by(email = email).first() #if returns a user, the email is already in the db

  if user:
    flash('Email address already exists')
    return redirect(url_for('auth.signup'))
  
  new_user = User(username = username, email = email, password = generate_password_hash(password, method='sha256'))

  db.session.add(new_user)
  db.session.commit()

  return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('main.index'))   

