from flask import Blueprint, render_template, request
import flask_login
from werkzeug.utils import redirect
from monolith.database import User, db
from monolith.forms import UnregisterForm



unreg = Blueprint('unreg', __name__)




@unreg.route('/unregister', methods=['GET', 'POST'])
def unregister():

    if not flask_login.current_user.is_authenticated:
        return redirect ('/login')

    form = UnregisterForm()

    if request.method == 'GET':
        return  render_template("unregister.html", form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            password = form.data['password']
            id = flask_login.current_user.id
            q = db.session.query(User).filter(User.id == id)
            user=q.first()
            if user.authenticate(password):
                db.session.delete(user)
                db.session.commit()
                return   redirect('/')
            else:
                return   redirect ('/unregister') #wrong password
    else:
        raise RuntimeError('This should not happen!')

