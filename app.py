from flask import Flask, render_template, request, redirect, Response, url_for, session, abort, g, flash
from flask_uploads import UploadSet, configure_uploads, IMAGES
import sqlite3
import os
from forms import UserSearchForm
import hashlib
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_login import LoginManager

app = Flask(__name__)
bcrypt = Bcrypt(app)
LoginManager = LoginManager(app)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
photos = UploadSet('photos')
app.config['UPLOADED_PHOTOS_DEST']= 'static'
configure_uploads(app, photos)



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
                        find_user = ("SELECT * FROM USER WHERE USERNAME = ? ")
                        c.execute(find_user, [(username)])
                        results = c.fetchall()                  
                        try:
                                userResults = results[0]
                                results and bcrypt.check_password_hash(userResults[2], password) 
                                session['logged_in'] = True
                                session['username'] = username
                                return redirect(url_for('homepage'))
                        except Exception:
                                error=("username and password not recognised")
                                return render_template('login.html', error=error)
        
        return render_template('login.html')

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
                
                pw_hash = bcrypt.generate_password_hash(signupPassword)
                
                filename= photos.save(request.files['profilephoto'], 'profile', signupUsername+'.jpg')

                newEntry = [(signupUsername, pw_hash, 0 ,0 )]
              
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
                con = sqlite3.connect('static/User.db')
                completion = False
                with con:
                        c = con.cursor()
                        findUserId = ("SELECT user_id FROM USER where username like(?)")
                        c.execute(findUserId, [username])
                        firstId=c.fetchall()
                        secondId=firstId[0]
                        thirdId=secondId[0]
                        
                        findNotes = ("SELECT noteType FROM notifications where (receiver_id) like (?)")
                        c.execute(findNotes, secondId)
                        noteNumber = c.fetchall()
                        
                        
                        
                        
                        if noteNumber == 1 :
                                noteMessage = "You have a new follower"
                                
                        else: 
                                
                                noteMessage = "You have a no new notifications"
                                
                                deleteNotes = ("DELETE FROM notifications WHERE (receiver_id) LIKE (?) ")
                                c.execute(deleteNotes, secondId)
                        
                                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                return render_template("notifications.html", noteMessage=noteMessage, img_url=img_url, username=g.username)
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
                                        
                                        search_img = url_for('static', filename= 'profile/' + search_string+'.jpg')
                                        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                        return render_template("results.html", search=search, search_img=search_img, i=i, img_url=img_url, username=g.username)
                                        
                                        
                                
                                if not results:
                                        error= 'No results found! Please try again.'
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
                        
                        con = sqlite3.connect('static/User.db')
                        completion = False
                        with con:
                                c = con.cursor()
                                
                                find_followers = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_followers, [username])
                                followers = c.fetchall()
                                sfollowers = followers[0]
                                dfollowers = sfollowers[0]
                                
                                insert = [(upload, username)]
                                insertImage = ("INSERT INTO PHOTO (url, username, dateUPLOADED) VALUES (?,?, datetime('now', 'localtime'))")
                                c.executemany(insertImage, insert)
                                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                return redirect(url_for('homepage', img_url=img_url, username=g.username))
                        
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
                        

                        countFollowers = ("SELECT COUNT(followed_id) FROM relationships WHERE followed_id = %s" %dfollowers)
                        c.execute(countFollowers) 
                        followers = c.fetchall()
                        finalFollowers = followers[0]  

                        countfollowing = ("SELECT COUNT(follower_id) FROM relationships WHERE follower_id = %s" %dfollowers)
                        c.execute(countfollowing)  
                        following = c.fetchall()
                        finalFollowing = following[0]

                        profilePictures = ('SELECT url, username FROM PHOTO WHERE username LIKE (?) ORDER BY dateUploaded DESC' )
                        c.execute(profilePictures, [username])
                        url = c.fetchall()
                        
                        
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
        notifications = 0
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
                                
                                
                                find_following = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_following, [username])
                                following = c.fetchall()
                                sfollowing = following[0]
                                rfollowing = sfollowers[0]
                                
                                userIDS = [(sfollowing[0], sfollowers[0], "Yes")]
                                noteDriver =[(sfollowing[0], sfollowers[0], 1)]

                                
                                setFollow = ("INSERT INTO relationships (follower_id, followed_id, exsists) VALUES (?, ?, ?)")
                                c.executemany(setFollow, userIDS)
                                giveNotification =("INSERT INTO notifications (  giver_id, receiver_id, noteType)  VALUES (?,?,?)")
                                c.executemany(giveNotification, noteDriver)
                                notifications = notifications +1
                                countFollowers = ("SELECT COUNT(follower_id) FROM relationships WHERE follower_id = %s" %dfollowers)
                                c.execute(countFollowers) 
                                followers = c.fetchall()
                                finalFollowers = followers[0]   
                                countfollowing = ("SELECT COUNT(followed_id) FROM relationships WHERE followed_id = %s" %dfollowers)
                                c.execute(countfollowing)  
                                following = c.fetchall()
                                finalFollowing = following[0]
                                search_url = url_for('static', filename= 'profile/' + search+'.jpg')
                                
                                
                                return redirect(url_for('searchProfile', followers=finalFollowers[0], notifications=notifications ,following=finalFollowing[0], search_url=search_url, username=g.username))
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
                                
                                
                                find_following = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(find_following, [username])
                                following = c.fetchall()
                                sfollowing = following[0]
                                rfollowing = sfollowers[0]
                                
                                userIDS = [(sfollowing[0], sfollowers[0])]

                                
                                unfollow = ("DELETE FROM relationships WHERE (follower_id) LIKE (?) AND (followed_id) LIKE (?)")
                                c.executemany(unfollow, userIDS)
                                unfollow = ("DELETE FROM notifications WHERE (giver_id) LIKE (?) AND (receiver_id) LIKE (?)")
                                c.executemany(unfollow, userIDS)

                                countFollowers = ("SELECT COUNT(follower_id) FROM relationships WHERE follower_id = %s" %dfollowers)
                                c.execute(countFollowers) 
                                followers = c.fetchall()
                                finalFollowers = followers[0]   
                                countfollowing = ("SELECT COUNT(followed_id) FROM relationships WHERE followed_id = %s" %dfollowers)
                                c.execute(countfollowing)  
                                following = c.fetchall()
                                finalFollowing = following[0]
                                search_url = url_for('static', filename= 'profile/' + search+'.jpg'
                                )
                                return redirect(url_for('searchProfile', followers=finalFollowers[0], following=finalFollowing[0], search_url=search_url, username=g.username))
                else:   
                        error = 'Please sign in before accessing this page!'
                        return render_template('index.html', error=error)
        error = 'Please sign in before accessing this page!'
        return render_template('index.html', error=error)



@app.route('/otherProfile/<string:otherUsers>')
def otherProfile(otherUsers):
        error = None
        img_url= None
        search_url = None
        followers = None
        following = None
        if g.username:
        
                username=g.username
                search=otherUsers
                
                con = sqlite3.connect('static/User.db')
                completion = False
                with con:
                        c = con.cursor()
                        
                        find_followers = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                        c.execute(find_followers, [search])
                        followers = c.fetchall()
                        sfollowers = followers[0]
                        dfollowers = sfollowers[0]

                        
                        
                        
                        find_following = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                        c.execute(find_following, [search])
                        following = c.fetchall()
                        sfollowing = following[0]
                        rfollowing = sfollowers[0]
                        
                        userIDS = [(sfollowing[0], sfollowers[0])]
                        profilePictures = ('SELECT url, username FROM PHOTO WHERE username LIKE (?) ORDER BY dateUploaded DESC' )
                        c.execute(profilePictures, [search])
                        url = c.fetchall()

                        countFollowers = ("SELECT COUNT(followed_id) FROM relationships WHERE followed_id = %s" %dfollowers)
                        c.execute(countFollowers) 
                        followers = c.fetchall()
                        finalFollowers = followers[0]
                        countfollowing = ("SELECT COUNT(follower_id) FROM relationships WHERE follower_id = %s" %rfollowing)
                        c.execute(countfollowing)  
                        following = c.fetchall()
                        finalFollowing = following[0]
                                        
                        
                        search_url = url_for('static', filename= 'profile/' + search +'.jpg')
                        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                        if finalFollowers[0] > 1:
                                return render_template("otherFollow.html", followers=finalFollowers[0], following=finalFollowing[0], url=url, search_url=search_url, username=g.username)
                        return render_template("otherFollow.html", followers=finalFollowers[0], following=finalFollowing[0], url=url, search_url=search_url, img_url=img_url, search=search, username=g.username)
          
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
                                
                                
                                
                                findUser = ("SELECT * FROM USER WHERE USERNAME LIKE (?)")
                                c.execute(findUser, [username])
                                following = c.fetchall()
                                sfollowing = following[0]
                                dfollowing = sfollowing[0]
                                
                                profilePictures = ('SELECT url, username FROM PHOTO WHERE username LIKE (?) ORDER BY dateUploaded DESC' )
                                c.execute(profilePictures, [search])
                                url = c.fetchall()

                                
                                        
                                countFollowers = ("SELECT COUNT(followed_id) FROM relationships WHERE followed_id = %s" %dfollowers)
                                c.execute(countFollowers) 
                                followers = c.fetchall()
                                finalFollowers = followers[0]
                                countfollowing = ("SELECT COUNT(follower_id) FROM relationships WHERE follower_id = %s" %dfollowers)
                                c.execute(countfollowing)  
                                following = c.fetchall()
                                finalFollowing = following[0]

                                
                                findExsists = ("SELECT * FROM relationships WHERE followed_id = %s " %dfollowers)
                                c.execute(findExsists)
                                findUser = c.fetchall()
                                               
                                try:
                                        exsistsResults = findUser[0]
                                        checkResults = dfollowers
                                        checkResult2 = "Yes"
                                        if checkResults == exsistsResults[1] and checkResult2 == exsistsResults[2]:
                                                
                                                flash("your are following")
                                                search_url = url_for('static', filename= 'profile/' + search +'.jpg')
                                                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                                return render_template("follow.html", img_url= img_url, followers=finalFollowers[0], following=finalFollowing[0], url=url, search=g.search, username =g.username, search_url= search_url)
                                        else:

                                                search_url = url_for('static', filename= 'profile/' + search +'.jpg')
                                                img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                                return render_template("searchProfile.html", followers=finalFollowers[0], following=finalFollowing[0], url=url, search_url=search_url, search=g.search, username=g.username)
                                except:
                                        search_url = url_for('static', filename= 'profile/' + search +'.jpg')
                                        img_url = url_for('static', filename= 'profile/' + username+'.jpg')
                                        return render_template("searchProfile.html", followers=finalFollowers[0], following=finalFollowing[0], url=url, search_url=search_url, search=g.search, username=g.username)
                else:   
                        error = 'Please sign in before accessing this page!'
                        return render_template('index.html', error=error)
        



if __name__ == '__main__':
        app.run(debug=True)
