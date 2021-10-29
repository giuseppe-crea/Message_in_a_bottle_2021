import datetime

from flask import Flask

from monolith.auth import login_manager
from monolith.database import User, db
from monolith.views import blueprints


def create_app():
    _app = Flask(__name__)
    _app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    _app.config['SECRET_KEY'] = 'ANOTHER ONE'
    # disable CSRF protection when the app is running in dev mode
    if _app.config['ENV'] == 'development':
        _app.config['WTF_CSRF_ENABLED'] = False
    _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    _app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    for bp in blueprints:
        _app.register_blueprint(bp)
        bp.app = _app

    db.init_app(_app)
    login_manager.init_app(_app)
    db.create_all(app=_app)

    # create a first admin user
    with _app.app_context():
        q = db.session.query(User).filter(User.email == 'example@example.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.date_of_birth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()

    return _app


app = create_app()

if __name__ == '__main__':
    app.run()
