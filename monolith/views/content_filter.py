from flask_login import current_user
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from monolith.database import User, db
from monolith.forms import ContentFilterForm
from better_profanity import profanity
from werkzeug.exceptions import BadRequestKeyError


content_filter = Blueprint('content_filter', __name__)


@content_filter.route('/content_filter', methods=['GET', 'POST'])
@login_required
def _content_filter():
    form = ContentFilterForm()
    if request.method == 'POST':  # POST request
        user = db.session.query(User).filter(User.id ==
                                             current_user.get_id()).first()
        try:
            request.form['content_filter']
        except BadRequestKeyError:
            setattr(user, 'content_filter', False)
        else:
            setattr(user, 'content_filter', True)

        db.session.commit()
        return redirect(url_for("content_filter._content_filter"))
    else:  # GET request
        content_filter_status = db.session.query(User).filter(
            User.id == current_user.get_id()
        ).first().content_filter
        return render_template('content_filter.html',
                               status=content_filter_status, form=form)


@content_filter.route('/content_filter/list', methods=['GET'])
@login_required
def _content_filter_list():
    file = open(r"./monolith/static/default_badwords.txt", "r")
    wordlist = []
    for line in file:
        wordlist.append(line)
    return render_template("badwords.html", wordlist=wordlist)


def check_content_filter(receiver_address, message_to_send):
    # check recipient content filter
    content_filter_status = db.session.query(User).filter(
        User.email == receiver_address
    ).first().content_filter
    if content_filter_status:
        if profanity.contains_profanity(message_to_send):
            return False
    return True
