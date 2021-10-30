from flask import Blueprint, render_template
from flask_login import login_required
from monolith.auth import admin_required

admin = Blueprint('admin', __name__)


@admin.route('/admin', methods=['GET'])
@login_required
@admin_required
def placeholder():
    return render_template("index.html", welcome="Hello Admin")
