from flask import Flask, render_template, request, url_for, session, abort
import models as dbHandler
from werkzeug.utils import secure_filename

app = Flask(__name__)

# config
UPLOAD_FOLDER = '/static/uploads/'
ALLOW_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/signup/')
def signup():
        return render_template("signup.html")

@app.route('/homepage/', methods=['POST', 'GET'])
def homepage():
        with open:(file_path, 'flasklogin.py')
        return render_template("homepage.html")


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
        return render_template("upload.html")
        


@app.route('/profile/')
def profile():
        return render_template("profile.html")

@app.route('/')
def index():
        return render_template("index.html")


if __name__ == '__main__':
        app.run(debug=True)
