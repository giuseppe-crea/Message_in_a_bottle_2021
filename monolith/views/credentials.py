from flask import Blueprint, redirect, render_template, request
from flask_login import login_required, current_user

from monolith.forms import CredentialsForm
from monolith.database import db

credentials = Blueprint('credentials', __name__)


# noinspection PyUnresolvedReferences
@credentials.route('/credentials', methods=['POST', 'GET'])
@login_required
def _credentials():
    """
    Route from which users can modify their account data
    data which can be modified includes:
    - First name; Last name; email address; password
    The user will be prompted for confirmation before the changes are committed
    The user's old password is required to make edits
    """
    form = CredentialsForm()
    kwargs = {}
    if request.method == 'POST':
        if form.validate_on_submit():
            old_password = form.data['old_password']
            if current_user.authenticate(old_password):
                for key, value in form.data.items():
                    # create a dictionary of only meaningful new values
                    if key != 'old_password' and value != '':
                        kwargs[key] = value
                if kwargs != {}:
                    current_user.update(**kwargs)
                    db.session.commit()
                    return redirect('/user_data')
                else:
                    form.email.errors.append("No changes specified "
                                             "(How are you here?.")
            else:
                form.old_password.errors.append("Wrong Password!")
        return render_template('error_template.html', form=form)
    else:
        return render_template('edit_credentials.html', form=form)
