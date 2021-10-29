from flask import Blueprint, render_template, request, redirect, \
    url_for, jsonify
from flask_login import login_required
from monolith.database import User, db
from monolith.forms import RecipientsListForm

list_blueprint = Blueprint('list', __name__)


@list_blueprint.route('/list_of_recipients', methods=['POST', 'GET'])
@login_required
def _display_users():
    """
    # ordering alphabetically, filtering admin accounts and the sender itself
    _users = db.session.query(User).order_by(User.lastname). \
        filter(User.firstname != 'Admin').all()
    """

    if request.method == 'POST':  # POST request
        if len(request.form) != 0:  # check the selection of a recipient
            # create a list of emails, removing the submitted label
            selected_recipient_list = \
                request.form.getlist('multiple_field_form')
            # create a dictionary to construct the right structure
            payload = {'email_list': ', '.join(selected_recipient_list)}
            # send a list of comma-separated emails
            # redirecting to /send
            return redirect(url_for('send._send', data=payload['email_list']))

        else:  # no recipient selected
            return redirect(url_for('send._send'))

    else:  # GET request, returns the list_of_recipients.html page
        return render_template('list_of_recipients.html')


@list_blueprint.route('/live_search', methods=['POST'])
@login_required
def ajax_livesearch():

    try:
        search_word = request.form['query']
        search = "%{}%".format(search_word)
    except:
        recipients_found = db.session.query(User).all()
    else:
        recipients_found = db.session.query(User). \
            filter(User.email.like(search) \
                   | User.firstname.like(search) \
                   | User.lastname.like(search)). \
                    limit(100).all() # avoiding a huge result

    # instantiate the form
    form = RecipientsListForm()

    # sets choices
    form.multiple_field_form.choices = \
        [(user.email, user.lastname + ' ' + user.firstname + ': ' + user.email)
         for user in recipients_found]

    return jsonify({'htmlresponse': render_template('search_response.html', form=form)})
