from flask import Flask, render_template, request, Response, url_for, session, abort
from flask_login import LoginManager , login_required , UserMixin , login_user
import models as dbHandler
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
login_manager = LoginManager()
login_manager.login_view = "index"
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self , username , password , id , active=True):
        self.id = id
        self.username = username
        self.password = password
        self.active = active

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def get_auth_token(self):
        return make_secure_token(self.username , key='secret_key')


class UsersRepository:

    def __init__(self):
        self.users = dict()
        self.users_id_dict = dict()
        self.identifier = 0
    
    def save_user(self, user):
        self.users_id_dict.setdefault(user.id, user)
        self.users.setdefault(user.username, user)
    
    def get_user(self, username):
        return self.users.get(username)
    
    def get_user_by_id(self, userid):
        return self.users_id_dict.get(userid)
    
    def next_index(self):
        self.identifier +=1
        return self.identifier

users_repository = UsersRepository()


# config
UPLOAD_FOLDER = '/static/uploads/'
ALLOW_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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



@app.route('/homepage/'<string:username>, methods=['POST', 'GET'])
@login_required
def homepage(username):
        return render_template("homepage.html", username=username)


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
        return render_template("upload.html")
        


@app.route('/profile/')
def profile():
        return render_template("profile.html")

@app.route('/')
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print('username')
        registeredUser = users_repository.get_user(username)
        print('Users '+ str(users_repository.users))
        print('Register user %s , password %s' % (registeredUser.username, registeredUser.password))
        if registeredUser != None and registeredUser.password == password:
            print('Logged in..')
            login_user(registeredUser)
            return redirect(url_for('homepage', username=marc))
        else:
            return abort(401)
    else:
       
        return render_template("index.html")



# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')

# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return users_repository.get_user_by_id(userid)

if __name__ == '__main__':
        app.run(debug=True)
