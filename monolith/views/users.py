import flask_login
from flask import Blueprint, redirect, render_template, request
from flask_login import login_required

from monolith.database import User, db
from monolith.forms import UserForm

users = Blueprint('users', __name__)


# noinspection PyUnresolvedReferences
@users.route('/users')
def _users():
    users_query = db.session.query(User)
    return render_template("users.html", users=users_query)


# noinspection PyUnresolvedReferences
@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            q = db.session.query(User).filter(User.email == form.data['email'])
            user = q.first()
            if user is None:
                new_user = User()
                form.populate_obj(new_user)
                # Password should be hashed with some salt.
                # For example if you choose a hash function x,
                # where x is in [md5, sha1, bcrypt],
                # the hashed_password should be = x(password + s) where
                # s is a secret key.
                new_user.set_password(form.password.data)
                db.session.add(new_user)
                db.session.commit()
                return redirect('/users')
            else:
                form.email.errors.append("Mail already in use.")
                return render_template('error_template.html', form=form)
        else:
            return render_template('error_template.html', form=form)
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)
    else:
        raise RuntimeError('This should not happen!')


def _user_data2dict(data: User):
    """
    Convert user data into a dictionary for easy display.
    """
    return {
        "first name": data.firstname,
        "last name": data.lastname,
        "email": data.email,
        "date of birth": data.date_of_birth.date()
    }


# noinspection PyUnresolvedReferences
@users.route('/user_data', methods=['GET'])
@login_required
def user_data():
    """
    The user can read his account's data.
    Only logged users are authorized to use this function.
    :return: display the user's data using the user_data template.
    """
    # get the current user
    user = flask_login.current_user
    # get the user's data fom the database
    data = db.session.query(User).filter(User.id == user.get_id()).first()
    # convert user data into a dictionary for easy display.
    result = _user_data2dict(data)
    return render_template('user_data.html', result=result)
