from flask import Blueprint
from flask_autodoc import Autodoc


doc = Blueprint('doc', __name__, url_prefix='/doc')
auto = Autodoc()


@doc.route('/')
@doc.route('/routes')
def public_doc():
    return auto.html(groups=['routes'], title='API Documentation')


@doc.route('/private')
def private_doc():
    return auto.html(groups=['code'], title='Private Documentation')
