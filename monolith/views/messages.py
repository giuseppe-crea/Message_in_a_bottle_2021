from flask import Blueprint, render_template
from flask.globals import request
from flask_wtf.recaptcha.widgets import JSONEncoder
from werkzeug.utils import redirect

from monolith.forms import MessageForm
from monolith.database import Message, db
from flask_login import current_user

messages = Blueprint('messages', __name__)

@messages.route('/create_msg', methods=['POST', 'GET'])
def create_message():
   msg_form = MessageForm()
   if request.method == 'POST':

      if msg_form.validate_on_submit():
         new_msg = Message()
         msg_form.populate_obj(new_msg)

         db.session.add(new_msg)
         db.session.commit()
         
         return redirect('/')

      return render_template('messages/create_msg.html', form=msg_form)
   elif request.method == 'GET':
        return render_template('messages/create_msg.html', form=msg_form)
   else:
      raise RuntimeError('This should not happen!')

@messages.route('/get_msg_list', methods=['GET'])
def get_message():
   messages = Message().query.filter_by(is_draft=False, receiver_email=current_user.email).all()
   return render_template('messages/get_msg_list.html', messages = messages)


@messages.route('/get_msg/<msg_id>', methods=['GET'])
def get_message_list(msg_id):
   message = Message().query.filter_by(id=int(msg_id)).one()
   return render_template('messages/get_msg.html', message = message)