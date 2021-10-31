from flask import Blueprint, render_template, request
import flask_login
from monolith.auth import admin_required
from flask_login.utils import login_required
from werkzeug.utils import redirect
from monolith.database import Report, db, User
from monolith.forms import ReportForm
from datetime import datetime


report = Blueprint('report', __name__)


# noinspection PyUnresolvedReferences
@report.route('/reports', methods=['GET'])
@login_required
@admin_required
def _users():
    query_reports = db.session.query(Report).order_by(Report.id.desc())
    return render_template("reports.html", reports=query_reports)


# report a user to the admins
# noinspection PyUnresolvedReferences
@report.route('/report_user', methods=['GET', 'POST'])
@login_required
def report_user():

    form = ReportForm()

    if request.method == 'GET':
        return render_template("report_user.html", form=form)

    elif request.method == 'POST':
        if form.validate_on_submit():
            reported_user = form.data['user']
            description = form.data['description']
            # block_user = form.data['block_user']
            current_user = flask_login.current_user.email

            # check if the reported email exists
            q = db.session.query(User).filter(User.email == reported_user)
            if q.first() is None:
                form.user.errors.append("ERROR: reported user does not exist")
                return render_template('error_template.html', form=form)

            # a user cannot report himself
            if reported_user == current_user:
                form.user.errors.append("ERROR: cannot report yourself")
                return render_template('error_template.html', form=form)

            # create the report
            report = Report()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report.add_report(
                current_user,
                reported_user,
                description,
                timestamp
                )
            db.session.add(report)
            db.session.commit()

            # blacklist reported user
            # if block_user == 'yes':
            # todo

            return redirect('/')

    else:
        raise RuntimeError('This should not happen!')
