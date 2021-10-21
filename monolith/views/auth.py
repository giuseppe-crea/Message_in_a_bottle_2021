from flask import Blueprint, redirect, render_template
from flask_login import login_user, logout_user

from monolith.database import User, db
from monolith.forms import LoginForm, UserForm

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        if user is not None and user.authenticate(password):
            login_user(user)
            return redirect('/')
    return render_template('login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        email, password, first_name, last_name, date_of_birth = \
            form.data['email'], form.data['password'], form.data['firstname'], form.data['lastname'], form.data['dateofbirth']
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        if user is not None:
            return redirect('/register')
        else:
            me = User()
            me.register_new_user(email, first_name, last_name, password, date_of_birth)
            db.session.add(me)
            db.session.commit()
            return redirect('/login')
    return render_template('register.html', form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')
