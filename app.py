from flask import Flask, render_template, request, redirect, Response, url_for, session, abort, g

import sqlite3
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models as dbHandler
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)

# config
UPLOAD_FOLDER = '/static/uploads/'
ALLOW_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def check_password(hashed_password, user_password):
    return hashed_password == hashlib.md5(user_password.encode()).hexdigest()

def validate(username, password):
    con = sqlite3.connect('static/User.db')
    completion = False
    with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM Users")
                rows = cur.fetchall()
                for row in rows:
                    dbUser = row[0]
                    dbPass = row[1]
                    if dbUser==username:
                        completion=check_password(dbPass, password)
    return completion


@app.route('/login/', methods=['GET', 'POST'])
def login():
        error = None
        if request.method == 'POST':
                
                username = request.form['username']
                password = request.form['password']
                
                con = sqlite3.connect('static/User.db')
                completion = False
                with con:
                        c = con.cursor()
                        
                        find_user = ("SELECT * FROM USERS WHERE USERNAME = ? AND PASSWORD =? ")
                        c.execute(find_user, [(username), (password)])
                        results = c.fetchall()

                        if results:
                                session['logged_in'] = True
                                session['username'] = username
                                return redirect(url_for('homepage'))
                        else:
                                error=("username and password not recognised")
                                return render_template('login.html', error=error)
                        print("username and password not recognised")
                        return render_template('login.html', error=error)
                print("username and password not recognised")
                return render_template('login.html', error=error)
        print("username and password not recognised")
        return render_template('login.html', error=error)
                                
                                
                
        
        



@app.route('/')
def index():
        
        if g.username:
                username=g.username
                return redirect(url_for('homepage'))
        else:
                return render_template('index.html')
        
@app.before_request
def before_request():
        g.username = None
        if 'username' in session:
                g.username = session['username']

@app.route('/signup/')
def signup():
        return render_template("signup.html")

@app.route('/register/', methods=['GET', 'POST'])
def register():
        error = None
        if request.method == 'POST':
                signupUsername = request.form['signupUsername']
                signupPassword = request.form['signupPassword']
                newEntry = [
                        (signupUsername, signupPassword)
                ]                
                con = sqlite3.connect('static/User.db')
                completion = False
                with con:
                        c = con.cursor()
                        try:
                                sql = '''INSERT INTO USERS (USERNAME, PASSWORD) VALUES(?, ?) '''
                                c.executemany(sql, newEntry)
                        except sqlite3.IntegrityError as e:
                                error = 'This is already an account, please try again!'
                                return render_template("signup.html", error=error)
                                con.commit()
                        return redirect(url_for('login'))
                

@app.route('/notifications/')
def notifications():
        error = None
        if g.username:
                username=g.username
                
                return render_template("notifications.html", username=g.username)
        else:   
                error = 'Please sign in before accessing this page!'
                return render_template('index.html', error=error)



@app.route('/homepage/')
def homepage():
        error = None
        if g.username:
                username=g.username
                
                return render_template("homepage.html", username=g.username)
        else:   
                error = 'Please sign in before accessing this page!'
                return render_template('index.html', error=error)


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
        error = None
        if g.username:
                username=g.username
                
                return render_template("upload.html", username=g.username)
        else:   
                error = 'Please sign in before accessing this page!'
                return render_template('index.html', error=error)

@app.route("/logout")
def logout():
        message= None
        session['logged_in'] = True
        session.clear()
        message = "You have successfully logged out."
        return render_template("index.html", message=message)


@app.route('/profile/')
def profile():
        error = None
        if g.username:
                username=g.username
                
                return render_template("profile.html", username=g.username)
        else:   
                error = 'Please sign in before accessing this page!'
                return render_template('index.html', error=error)



if __name__ == '__main__':
        app.run(debug=True)
