from flask import Blueprint, render_template, request, abort
import flask_login
from flask_login.utils import login_required
from werkzeug.utils import redirect
from monolith.database import User, db
from monolith.forms import UnregisterForm
from monolith.views.doc import auto


unreg = Blueprint('unreg', __name__)


# delete user account
# noinspection PyUnresolvedReferences
@unreg.route('/unregister', methods=['GET', 'POST'])
@auto.doc(groups=['public'])
@login_required
def unregister():

    form = UnregisterForm()

    if request.method == 'GET':
        return render_template("unregister.html", form=form)

    elif request.method == 'POST':
        if form.validate_on_submit():
            password = form.data['password']
            _id = flask_login.current_user.id    # get user unique id
            # find user in database
            q = db.session.query(User).filter(User.id == _id)
            user = q.first()
            # if the input password is correct, delete user account
            if user.authenticate(password):
                db.session.delete(user)
                db.session.commit()
                return redirect('/')
            # if the input password password is wrong, return a 401 status code
            else:
                abort(401)
    else:
        raise RuntimeError('This should not happen!')
