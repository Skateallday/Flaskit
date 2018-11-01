from flask import Flask, render_template, request, url_for
import models as dbHandler


app = Flask(__name__)

@app.route('/signup/')
def signup():
        return render_template("signup.html")

@app.route('/homepage/', methods=['POST', 'GET'])
def homepage():
        logo = url_for('static', filename='logo.png')
        if request.method=='POST':
                username = request.form['username']
                password = request.form['password']
                dbHandler.retrieveUsers(username, password)
                users = dbHandler.retrieveUsers(username,password)
                return render_template('homepage.html', logo=logo, users=users)
        else:
                return render_template("index.html" )





@app.route('/')
def index():
        return render_template("index.html")

if __name__ == '__main__':
        app.run(debug=True)
