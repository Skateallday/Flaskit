from flask import Flask, render_template, request, redirect, Response, url_for, session, abort, g
from flask_uploads import UploadSet, configure_uploads, IMAGES
import sqlite3
import os
from forms import UserSearchForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)

photos = UploadSet('photos')
app.config['UPLOADED_PHOTOS_DEST']= 'static'
configure_uploads(app, photos)

def check_password(hashed_password, user_password):
    return hashed_password == hashlib.md5(user_password.encode()).hexdigest()

def validate(username, password):
    con = sqlite3.connect('static/User.db')
    completion = False
    with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM USER")
                rows = cur.fetchall()
                for row in rows:
                    dbUser = row[0]
                    dbPass = row[1]
                    if dbUser==username:
                        completion=check_password(dbPass, password)
    return completion


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


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
                        
                        find_user = ("SELECT * FROM USER WHERE USERNAME = ? AND PASSWORD =? ")
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
        if 'search' in session:
                g.search = session['search']

@app.route('/signup/')
def signup():
        return render_template("signup.html")

@app.route('/register/', methods=['GET', 'POST'])
def register():
        error = None
        if request.method == 'POST' and 'profilephoto' in request.files:

                signupUsername = request.form['signupUsername']
                signupPassword = request.form['signupPassword']
                
                filename= photos.save(request.files['profilephoto'], 'profile', signupUsername+'.jpg')

                newEntry = [(signupUsername, signupPassword, 0 ,0 )]
              
                con = sqlite3.connect('static/User.db')
                completion = False
                with con:
                        c = con.cursor()
                        try:
                                sql = '''INSERT INTO USER (username, password, followers, following  ) VALUES(?, ?, ?, ?) '''
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
                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                return render_template("notifications.html", img_url=img_url, username=g.username)
        else:   
                error = 'Please sign in before accessing this page!'
                return render_template('index.html', error=error)



@app.route('/search/', methods=['GET', 'POST'])
def search():
        error = None
        
        if g.username:
                username=g.username
                search = UserSearchForm(request.form)
                if request.method == 'POST':
                        return searchResults(search)
                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                return render_template('searchResults.html', img_url=img_url, search=search,  username=g.username)
        else:   
                error = 'Please sign in before accessing this page!'
                return render_template('index.html', error=error)

        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
        return render_template('search.html', form=search, img_url=img_url, error=error)

@app.route('/searchResults/', methods=['GET', 'POST'])
def searchResults(search):
        error = None
        search_img = None
        results= []
        search_string = search.data['search']
        if g.username:
                username=g.username
                if request.method == 'POST':
                        
                        
                        con = sqlite3.connect('static/User.db')
                        completion = False
                        with con:
                                c = con.cursor()
                                
                                find_user = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_user, [(search_string)])
                                results = c.fetchall()

                                for i in results:
                                        session['search']=search_string
                                        print(i)
                                        search_img = url_for('static', filename= 'profile/' + search_string+'.jpg')
                                        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                        return render_template("results.html", search=search, search_img=search_img, i=i, img_url=img_url, username=g.username)
                                        
                                        
                                
                                if not results:
                                        error= 'Yo No results found!'
                                        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                        return render_template('search.html', error=error, img_url=img_url, search=search)
                                else:
                                        
                                        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                        return render_template('searchResults.html', img_url=img_url, results=results)
                                
        error= 'No results found!'
        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
        return render_template('search.html', img_url=img_url, error=error)



@app.route('/searchUsers/', methods=['GET', 'POST'])
def searchUsers():
        error = None
        if g.username:
                username=g.username
                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                return render_template("searchUsers.html", img_url=img_url, username=g.username)
        else:   
                error = 'Please sign in before accessing this page!'
                return render_template('index.html', error=error)

@app.route('/homepage/', methods=['GET', 'POST'])
def homepage():
        error = None
        if g.username:
                username=g.username
                con = sqlite3.connect('static/User.db')
                completion = False
                with con:
                        c = con.cursor()
                        c.execute('SELECT url, username FROM PHOTO ORDER BY dateUploaded DESC')
                        url = c.fetchall()
                        print(url)
                        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                        return render_template("homepage.html", img_url=img_url, url=url, username=g.username)
                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                return render_template("homepage.html", img_url=img_url, url=url, username=g.username)
        error = 'Please sign in before accessing this page!'
        return render_template('index.html', error=error)

@app.route('/upload/', methods=['GET', 'POST'])
def upload():
        error = None
        if g.username:
                username=g.username
                if request.method == 'POST':
                        upload = request.form['content']
                        print(upload)
                        con = sqlite3.connect('static/User.db')
                        completion = False
                        with con:
                                c = con.cursor()
                                
                                find_followers = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_followers, [username])
                                followers = c.fetchall()
                                sfollowers = followers[0]
                                dfollowers = sfollowers[0]
                                print (dfollowers)
                                insert = [(upload, username)]
                                insertImage = ("INSERT INTO PHOTO (url, username, dateUPLOADED) VALUES (?,?, datetime('now', 'localtime'))")
                                c.executemany(insertImage, insert)
                                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                return render_template("homepage.html", img_url=img_url, username=g.username)
                        return render_template("homepage.html", img_url=img_url, username=g.username)
        error = 'Please sign in before accessing this page!'
        return render_template('index.html', error=error)

@app.route("/logout")
def logout():
        message= None
        session['logged_in'] = True
        session.clear()
        message = "You have successfully logged out."
        return render_template("index.html", message=message)


@app.route('/results/')
def results():
        error = None
        img_url= None
        if g.username:
                username=g.username
                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                return render_template("results.html", img_url=img_url, username=g.username)
        else:   
                error = 'Please sign in before accessing this page!'
                return render_template('index.html', error=error)

@app.route('/profile/')
def profile():
        error = None
        img_url= None
        followers =[]
        following =[]
        if g.username:
                username=g.username
                con = sqlite3.connect('static/User.db')
                completion = False
                with con:
                        c = con.cursor()
                        
                        find_followers = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                        c.execute(find_followers, [username])
                        followers = c.fetchall()
                        sfollowers = followers[0]
                        dfollowers = sfollowers[0]
                        print (dfollowers)

                        countFollowers = ("SELECT COUNT(followed_id) FROM relationship WHERE followed_id = %s" %dfollowers)
                        c.execute(countFollowers) 
                        followers = c.fetchall()
                        finalFollowers = followers[0]  

                        countfollowing = ("SELECT COUNT(follower_id) FROM relationship WHERE follower_id = %s" %dfollowers)
                        c.execute(countfollowing)  
                        following = c.fetchall()
                        finalFollowing = following[0]

                        profilePictures = ('SELECT url, username FROM PHOTO WHERE username LIKE (?) ORDER BY dateUploaded DESC' )
                        c.execute(profilePictures, [username])
                        url = c.fetchall()
                        
                        print(url)
                        search_url = url_for('static', filename= 'profile/' + username+'.jpg')                        
                        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                        return render_template("profile.html", followers=finalFollowers[0], following=finalFollowing[0], url=url, img_url=img_url, username=g.username)
        else:   
                error = 'Please sign in before accessing this page!'
                return render_template('index.html', error=error)
        error = 'Please sign in before accessing this page!'
        return render_template('index.html', error=error)
       
@app.route('/follow/', methods=['GET', 'POST'])
def follow():
        error = None
        img_url= None
        search_url = None
        if g.username:
                if g.search:
                        username=g.username
                        search=g.search
                        con = sqlite3.connect('static/User.db')
                        completion = False
                        with con:
                                c = con.cursor()
                                
                                find_followers = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_followers, [search])
                                followers = c.fetchall()
                                sfollowers = followers[0]
                                dfollowers = sfollowers[0]
                                print(dfollowers)
                                
                                find_following = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_following, [username])
                                following = c.fetchall()
                                sfollowing = following[0]
                                rfollowing = sfollowers[0]
                                
                                userIDS = [(sfollowing[0], sfollowers[0])]

                                print (userIDS)
                                setFollow = ("INSERT INTO relationship (follower_id, followed_id) VALUES (?, ?)")
                                c.executemany(setFollow, userIDS)

                                countFollowers = ("SELECT COUNT(follower_id) FROM relationship WHERE follower_id = %s" %dfollowers)
                                c.execute(countFollowers) 
                                followers = c.fetchall()
                                finalFollowers = followers[0]   
                                countfollowing = ("SELECT COUNT(followed_id) FROM relationship WHERE followed_id = %s" %dfollowers)
                                c.execute(countfollowing)  
                                following = c.fetchall()
                                finalFollowing = following[0]
                                search_url = url_for('static', filename= 'profile/' + search+'.jpg')
                                
                                return render_template("follow.html", followers=finalFollowers[0], following=finalFollowing[0], search_url=search_url, username=g.username)
                else:   
                        error = 'Please sign in before accessing this page!'
                        return render_template('index.html', error=error)
        error = 'Please sign in before accessing this page!'
        return render_template('index.html', error=error)

 
@app.route('/unfollow/', methods=['GET', 'POST'])
def unfollow():
        error = None
        img_url= None
        search_url = None
        if g.username:
                if g.search:
                        username=g.username
                        search=g.search
                        con = sqlite3.connect('static/User.db')
                        completion = False
                        with con:
                                c = con.cursor()
                                
                                find_followers = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_followers, [search])
                                followers = c.fetchall()
                                sfollowers = followers[0]
                                dfollowers = sfollowers[0]
                                print(dfollowers)
                                
                                find_following = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_following, [username])
                                following = c.fetchall()
                                sfollowing = following[0]
                                rfollowing = sfollowers[0]
                                
                                userIDS = [(sfollowing[0], sfollowers[0])]

                                print (userIDS)
                                unfollow = ("DELETE FROM relationship WHERE (follower_id, followed_id) LIKE (?, ?)")
                                c.executemany(unfollow, userIDS)

                                countFollowers = ("SELECT COUNT(follower_id) FROM relationship WHERE follower_id = %s" %dfollowers)
                                c.execute(countFollowers) 
                                followers = c.fetchall()
                                finalFollowers = followers[0]   
                                countfollowing = ("SELECT COUNT(followed_id) FROM relationship WHERE followed_id = %s" %dfollowers)
                                c.execute(countfollowing)  
                                following = c.fetchall()
                                finalFollowing = following[0]
                                search_url = url_for('static', filename= 'profile/' + search+'.jpg'
                                )
                                return render_template("searchProfile.html", followers=finalFollowers[0], following=finalFollowing[0], search_url=search_url, username=g.username)
                else:   
                        error = 'Please sign in before accessing this page!'
                        return render_template('index.html', error=error)
        error = 'Please sign in before accessing this page!'
        return render_template('index.html', error=error)

@app.route('/searchProfile/')
def searchProfile():
        error = None
        img_url= None
        search_url = None
        if g.username:
                if g.search:
                        username=g.username
                        search=g.search
                        con = sqlite3.connect('static/User.db')
                        completion = False
                        with con:
                                c = con.cursor()
                                
                                find_followers = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_followers, [search])
                                followers = c.fetchall()
                                sfollowers = followers[0]
                                dfollowers = sfollowers[0]
                                print (sfollowers)
                                
                                find_following = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_following, [search])
                                following = c.fetchall()
                                sfollowing = following[0]
                                dfollowing = sfollowing[0]
                                profilePictures = ('SELECT url, username FROM PHOTO WHERE username LIKE (?) ORDER BY dateUploaded DESC' )
                                c.execute(profilePictures, [search])
                                url = c.fetchall()
                                            
                                countFollowers = ("SELECT COUNT(followed_id) FROM relationship WHERE followed_id = %s" %dfollowers)
                                c.execute(countFollowers) 
                                followers = c.fetchall()
                                finalFollowers = followers[0]
                                countfollowing = ("SELECT COUNT(follower_id) FROM relationship WHERE follower_id = %s" %dfollowing)
                                c.execute(countfollowing)  
                                following = c.fetchall()
                                finalFollowing = following[0]
                                search_url = url_for('static', filename= 'profile/' + search +'.jpg')
                                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                if finalFollowers[0] > 1:
                                        return render_template("follow.html", followers=finalFollowers[0], following=finalFollowing[0], url=url, search_url=search_url, search=g.search, username=g.username)
                                return render_template("searchProfile.html", followers=finalFollowers[0], following=finalFollowing[0], url=url, search_url=search_url, img_url=img_url, search=search, username=g.username)
                else:   
                        error = 'Please sign in before accessing this page!'
                        return render_template('index.html', error=error)
        error = 'Please sign in before accessing this page!'
        return render_template('index.html', error=error)
       


if __name__ == '__main__':
        app.run(debug=True)
