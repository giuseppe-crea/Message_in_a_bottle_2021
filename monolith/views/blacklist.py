import flask_login
from flask import Blueprint, redirect, render_template
from flask_login import login_required

from monolith.database import User, db, Blacklist
from monolith.forms import EmailForm

blacklist = Blueprint('blacklist', __name__)


@blacklist.route('/blacklist', methods=['GET'])
@login_required
def get_blacklist():
    """
    Get the logged user's blacklist.
    Only logged users are authorized to use this function.
    :return: display the user's blacklist using the blacklist template.
    """
    # get the current user
    user = flask_login.current_user
    # get the user's blacklist fom the database
    _blacklist = db.session.query(Blacklist).filter(
        Blacklist.owner == user.get_id()
    ).all()
    _blacklist = [e.email for e in _blacklist]
    # noinspection PyUnresolvedReferences
    return render_template('blacklist.html', result=_blacklist)


# some checks for the add functionality
def _check_exist(email):
    return db.session.query(User.query.filter(User.email == email)
                            .exists()).scalar()


def _check_already_blocked(user, email):
    return db.session.query(
        Blacklist.query.filter(
            Blacklist.email == email,
            Blacklist.owner == user.get_id()).exists()).scalar()


def _check_itself(user, email):
    usr = db.session.query(User).filter(User.id == user.get_id()).first()
    return usr.email == email


def _check_add_blacklist(user, email):
    return _check_exist(email) and not (
            _check_already_blocked(user, email) or
            _check_itself(user, email))


def add2blacklist_local(user, email):
    if _check_add_blacklist(user, email):
        # insert the email to block in the user's blacklist
        blacklist = Blacklist()
        blacklist.add_blocked_user(user.get_id(), email)
        db.session.add(blacklist)
        db.session.commit()


@blacklist.route('/blacklist/add', methods=['GET', 'POST'])
@login_required
def add2blacklist():
    """
    The logged user adds an email to his blacklist.
    Only logged users are authorized to use this function.
    :return: display the user's blacklist using the blacklist template or
    a form to request an email to the user.
    """
    form = EmailForm()
    if form.validate_on_submit():
        # get the email to block
        email = form.data['email']
        # get the current user
        user = flask_login.current_user
        add2blacklist_local(user, email)
        return redirect('/blacklist')

    # noinspection PyUnresolvedReferences
    return render_template('request_form.html', form=form)


@blacklist.route('/blacklist/remove', methods=['GET', 'POST'])
@login_required
def delete_from_blacklist():
    """
    The logged user removes an email from his blacklist.
    Only logged users are authorized to use this function.
    :return: display the user's blacklist using the blacklist template or
    a form to request an email to the user.
    """
    form = EmailForm()
    if form.validate_on_submit():
        # get the email to block
        email = form.data['email']

        # get the current user
        user = flask_login.current_user

        # remove the email from the blacklist
        _blacklist = db.session.query(Blacklist).filter(
            Blacklist.owner == user.get_id(),
            Blacklist.email == email
        )
        _blacklist.delete(synchronize_session=False)
        db.session.commit()
        return redirect('/blacklist')

    # noinspection PyUnresolvedReferences
    return render_template('request_form.html', form=form)


def is_blacklisted(sender, receiver):
    receiver_id = db.session.query(User).filter(User.email == receiver) \
        .first().id
    return db.session.query(
        Blacklist.query.filter(
            Blacklist.email == sender,
            Blacklist.owner == receiver_id).exists()).scalar()
