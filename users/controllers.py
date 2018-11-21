from flask import Blueprint, request, session, jsonify, render_template
from sqlalchemy.exc import IntegrityError
from app import db
from .models import User



mod_user = Blueprint('user', __name__, url_prefix='/api')

@app.route('/register/', methods=['GET', 'POST'])
def register():
        error = None
        try:
                signupUsername = request.form['signupUsername']
                signupPassword = request.form['signupPassword']
                signupEmail = request.form['signupEmail']
                filename= photos.save(request.files['profilephoto'], 'profile', signupUsername+'.jpg')
 
                newEntry = [(signupUsername, signupPassword, signupEmail, 0 ,0, "", "")]
              
        except KeyError as e:
                return jsonify(success=False, message="%s not sent in the request" %e.args), 400
        if ' ' in signupUsername:
                return jsonify(success=False, message="Please enter a valid username"), 400
        
        u = User(signupUsername, signupPassword, signupEmail)
        db.session.add(u)
        try:
                db.session.commit()
        except IntegrityError as e:
                return jsonify(success=False, message="This username already exists"), 400
        
        return render_template('login.html')