from flask import Blueprint
from flask_autodoc import Autodoc


doc = Blueprint('doc', __name__, url_prefix='/doc')
auto = Autodoc()


@doc.route('/')
@doc.route('/public')
def api_doc():
    return auto.html(groups=['routes'], title='API Documentation')
