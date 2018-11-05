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
    con = sqlite3.connect('var/Flaskit.db')
    completion = False
    with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM users")
                rows = cur.fetchall()
                for row in rows:
                    dbUser = row[0]
                    dbPass = row[1]
                    if dbUser==username:
                        completion=check_password(dbPass, password)
    return completion


@app.route('/')
def index():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = validate(username, password)
        if completion ==False:
                error = 'Invalid Input, try again!'
        else:
                return redirect(url_for('homepage'))
        return render_template("index.html", error=error)

@app.route('/signup/')
def signup():
        return render_template("signup.html")

@app.route('/register/', methods=['GET', 'POST'])
def register():
        if request.method == 'POST':
                signupUsername = request.form['signupUsername']
                signupPassword = request.form['signupPassword']
                new_user = User(signupUsername , signupPassword , users_repository.next_index())
                users_repository.save_user(new_user)
                return render_template("index.html")
        return render_template("signup.html")

@app.route('/notifications/')
def notifications():
        return render_template("notifications.html")



@app.route('/homepage/')
def homepage():
        return render_template("homepage.html")


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
        return render_template("upload.html")
        


@app.route('/profile/')
def profile():
        return render_template("profile.html")



if __name__ == '__main__':
        app.run(debug=True)
