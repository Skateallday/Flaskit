from flask import Blueprint, request, session, jsonify
from sqlalchemy.exc import IntegrityError
from app import db
from .models import User

mod_user = Blueprint('user', __name__, url_prefix='/api')


@mod_user.route('/login', methods=['GET'])
def check_login():
    try:
        if 'user_id' in session:
            user = User.query.filter(User.id == session['user_id']).first()
            print(user)
            return jsonify(success=True, user=user.to_dict())

        return "NO Session"
    except: 
        return jsonify(success=False), 401


@mod_user.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
    except KeyError as e:
        return jsonify(success=False, message="%s not sent in the request" % e.args), 400

    user = User.query.filter(User.username == username).first()
    if user is None:
        return jsonify(success=False, message="No user"), 400
    if not user.check_password(password):
        return jsonify(success=False, message="wrong password"), 400
    session['user_id'] = user.id

    return jsonify(success=True, user=user.to_dict())

@mod_user.route('/logout', methods=['POST'])
def logout():
    try:
        session.pop('user_id')
        return jsonify(success=True)
    except:
        return jsonify(success=False), 401

@mod_user.route('/register', methods=['POST'])
def create_user():
    try:
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
    except KeyError as e:
        return jsonify(success=False, message="%s not sent in the request" % e.args), 400

    if ' ' in username:
        return jsonify(success=False, message="Please enter a valid username"), 400

    u = User(username, password, name)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError as e:
        return jsonify(success=False, message="This username already exists"), 400

    return jsonify(success=True)



@mod_user.route('/getId', methods=['POST'])
def get_id_from_username():
    try:
        username = request.form['username']

        user = User.query.filter(User.username == username).first()
        if user is None:
            return jsonify(success=False, message="No user"), 400

        return jsonify(success=True, user_id=user.id)
    except:
        return jsonify(success=False), 400