from flask import Blueprint, render_template, request, abort
import flask_login
from flask_login.utils import login_required
from werkzeug.utils import redirect
from monolith.database import User, db
from monolith.forms import UnregisterForm



unreg = Blueprint('unreg', __name__)



#delete user account
@unreg.route('/unregister', methods=['GET', 'POST'])
@login_required
def unregister():

    form = UnregisterForm()

    if request.method == 'GET':
        return  render_template("unregister.html", form=form)

    elif request.method == 'POST':
        if form.validate_on_submit():
            password = form.data['password']
            id = flask_login.current_user.id    #get user unique id
            q = db.session.query(User).filter(User.id == id)    #find user in database
            user=q.first()
            if user.authenticate(password): #if the input password is correct, delete user account
                db.session.delete(user)
                db.session.commit()
                return   redirect('/')
            else:
                abort(401)  #if the input password password is wrong, return a 401 status code
    else:
        raise RuntimeError('This should not happen!')

