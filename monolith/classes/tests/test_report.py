import unittest

from monolith.classes.tests.utils import create_user, get_testing_app, login


class TestReport(unittest.TestCase):

    # a non-authenticated user cannot file a report
    def test_unauthorized(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/report_user')
            assert rv.status_code == 401

    # report creation testing
    def test_report(self):
        tested_app = get_testing_app()
        with tested_app:

            # create the report author account
            rv = create_user(
                tested_app,
                "author@example.com",
                "author",
                "author",
                "01/01/1990",
                "author")
            assert rv.status_code == 200

            # the author logs in
            response = login(tested_app, 'author@example.com', 'author')
            assert response.status_code == 200

            # get the report user page
            rv = tested_app.get('/report_user')
            assert rv.status_code == 200

            # the author tries to report a non-existant user
            rv = tested_app.post(
                '/report_user',
                data={
                    'user': "wrong@user.com",
                    'description': 'lorem ipsum',
                    'block_user': 'yes'
                },
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'ERROR: reported user does not exist' in rv.data

            # the author tries to report himself
            rv = tested_app.post(
                '/report_user',
                data={
                    'user': "author@example.com",
                    'description': 'lorem ipsum',
                    'block_user': 'yes'
                },
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'ERROR: cannot report yourself' in rv.data

            # create the reported account
            rv = create_user(
                tested_app,
                "reported@example.com",
                "reported",
                "reported",
                "01/01/1990",
                "reported")
            assert rv.status_code == 200

            # the author succesfully files a report
            rv = tested_app.post(
                '/report_user',
                data={
                    'user': "reported@example.com",
                    'description': 'lorem ipsum',
                    'block_user': 'yes'
                },
                follow_redirects=False
            )
            assert rv.status_code == 302

    # test unauthorized access to filed reports
    def test_user_reports(self):
        tested_app = get_testing_app()
        with tested_app:

            # a non-authenticated user cannot access the reports
            rv = tested_app.get('/reports')
            assert rv.status_code == 401

            # create a normal user
            rv = create_user(
                tested_app,
                "user@example.com",
                "user",
                "user",
                "01/01/1990",
                "user")
            assert rv.status_code == 200

            # the user logs in
            response = login(tested_app, 'user@example.com', 'user')
            assert response.status_code == 200

            # a normal user cannot access the reports
            rv = tested_app.get('/reports')
            assert rv.status_code == 401

    # test admin access to filed reports
    def test_admin_reports(self):
        tested_app = get_testing_app()
        with tested_app:

            # an admin logs in
            response = login(tested_app, 'example@example.com', 'admin')
            assert response.status_code == 200

            # an admin can access the reports
            rv = tested_app.get('/reports')
            assert rv.status_code == 200
