import flask_login
from flask import Blueprint, redirect, render_template, request, abort, jsonify
from flask_login import login_required

from monolith.database import User, db, Blacklist
from monolith.forms import UserForm

blacklist = Blueprint('blacklist', __name__)

@blacklist.route('/blacklist', methods=['GET'])
@login_required
def get_blacklist():
    """
    The user can read his account's data.
    Only logged users are authorized to use this function.
    :return: display the user's data using the user_data template.
    """
    # get the current user
    user = flask_login.current_user
    # get the user's blacklist fom the database
    blacklist = db.session.query(Blacklist).filter(Blacklist.owner ==
        user.get_id()).distinct(Blacklist.email).all()
    blacklist = [e.email for e in blacklist]
    if not blacklist:
        return jsonify("Your blacklist is empty")
    return jsonify(blacklist)

@blacklist.route('/blacklist/<email>', methods=['POST'])
@login_required
def add2blacklist(email):
    """
    The user can read his account's data.
    Only logged users are authorized to use this function.
    :return: display the user's data using the user_data template.
    """
    # get the current user
    user = flask_login.current_user
    #get the email to block
    #email = request.args.get("email")
    # insert the email to block in the user's blacklist
    blacklist = Blacklist()
    blacklist.add_blocked_user(user.get_id(), email)
    db.session.add(blacklist)
    db.session.commit()

    return jsonify(email + " blocked")

@blacklist.route('/blacklist/<email>', methods=['DELETE'])
@login_required
def delete_from_blacklist(email):
    """
    The user can read his account's data.
    Only logged users are authorized to use this function.
    :return: display the user's data using the user_data template.
    """
    # get the current user
    user = flask_login.current_user
    #get the email to block
    #email = request.args.get("email")
    blacklist = db.session.query(Blacklist).filter(Blacklist.owner ==
        user.get_id(), Blacklist.email == email)
    blacklist.delete(synchronize_session=False)
    db.session.commit()

    return jsonify(email + " removed")