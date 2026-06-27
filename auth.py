from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)
from google.cloud import datastore
import constants

client = datastore.Client()


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    query = client.query(kind=constants.users)
    query.add_filter("email", "=", email)

    user = list(query.fetch())  # if this returns a user, then the email already exists in database

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user[0]["password"], password):
        flash('Please check your login details and try again.')
        return redirect(url_for('index'))  # if the user doesn't exist or password is wrong, reload the page

    # # if the above check passes, then we know the user has the right credentials
    new_route = '/home/' + str(user[0].id)
    return redirect(new_route)


@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    first_name = request.form.get('fname')
    last_name = request.form.get('lname')
    password = request.form.get('password')
    hash_pw = generate_password_hash(password, method='sha256')

    query = client.query(kind=constants.users)
    query.add_filter("email", "=", email)

    user = list(query.fetch())  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already has an account!')
        return redirect(url_for('index'))

    new_user = datastore.entity.Entity(key=client.key(constants.users))
    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user.update({"first_name": first_name, "last_name": last_name,
                     "password": hash_pw, "email": email, "challenges": []})
    client.put(new_user)

    flash('Account successfully created! Please log in.')
    return redirect(url_for('index'))
