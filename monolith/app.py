import datetime
import sys

from flask import Flask
from flask_uploads import configure_uploads

from monolith.background import LOTTERY_PRICE
from monolith.auth import login_manager
from monolith.database import User, db
from monolith.views import blueprints
from monolith.forms import images
from monolith.send import UPLOAD_FOLDER, MAX_CONTENT_LENGTH


def create_app():
    _app = Flask(__name__)
    _app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    _app.config['SECRET_KEY'] = 'ANOTHER ONE'
    _app.config['UPLOADED_IMAGES_DEST'] = UPLOAD_FOLDER
    _app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    # disable CSRF protection when the app is running in dev or test mode
    if _app.config['ENV'] == 'development' or "pytest" in sys.modules:
        _app.config['WTF_CSRF_ENABLED'] = False
    if "pytest" in sys.modules:
        _app.config['TESTING'] = True
        _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../T_mmiab.db'
    else:
        _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    _app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    configure_uploads(_app, images)
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
            example.content_filter = False
            example.set_password('admin')
            example.set_points(10 * LOTTERY_PRICE)
            db.session.add(example)
            db.session.commit()
    return _app


app = create_app()

if __name__ == '__main__':
    app.run()
