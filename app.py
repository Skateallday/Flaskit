from flask import Flask, render_template, request, redirect, Response, url_for, session, abort
import sqlite3

import models as dbHandler
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)


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
        completion = validate(username, password)
        if completion ==False:
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('homepage', username=username))
    return render_template('login.html', error=error)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup/')
def signup():
        return render_template("signup.html")

@app.route('/register/', methods=['GET', 'POST'])
def register():
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
                                print('sqlite error: ', e.args[0]) # column name is not unique
                        con.commit()
                return redirect(url_for('login'))
        return render_template("signup.html")

@app.route('/notifications/')
def notifications():
        return render_template("notifications.html")



@app.route('/homepage/')
@app.route('/homepage/<string:username>')
def homepage(username):
        return render_template("homepage.html", username=username)


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
        return render_template("upload.html")
        


@app.route('/profile/')
def profile():
        return render_template("profile.html")



if __name__ == '__main__':
        app.run(debug=True)
