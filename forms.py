from wtforms import Form, StringField, SelectField, PasswordField
from flask_wtf import Form
from wtforms.validators import DataRequired, length, Email, EqualTo

class UserSearchForm(Form):
    choices = [('username')]
    SelectField = SelectField('Search users:', choices= choices)
    search = StringField('')

class AjaxSavePhoto():
    def validate(self):
        try:
            self.url = self.args[0]["url"]
            self.baseurl = self.args[0]["baseurl"]
            self.caption = self.args [0]["caption"]
        except Exception as e:
            return self.error("Malformed reuqest, this did not process.")

        if self.user == "NL":
            return self.error("Unauthorised reuqest")

        if self.url[0:20] != "https://ucarecdn.com" or self.baseurl[0.20] != "https://ucarecdn.com":
            return self.error("Invalid image URL")

        result = urlopen(self.baseurl+"-/preview/-/main_color/3/")
        data = result.read()
        data = json.loads(data.decode('utf-8'))

        main_colour = ""
        if data["main_colors"] != []:
            for colour in data["main_colors"][randint(0,2)]:
                main_colour = main_colour + str(colour) + ","
            main_colour = main_colour[:-1]

        p = Photo(url=self.url, baseurl=self.baseurl, owner=self.user.username, likes=0, caption=self.caption, main_colour=main_colour)
        
        con = sqlite3.connect('static/Photo.db')
                
        with con:
                c = con.cursor()
                try:
                        sql = '''INSERT INTO Photo (baseurl, url, owner, likes, caption, main_colour  ) VALUES(?, ?, ?, ?,?,?) '''
                        c.executemany(sql, p)
                except sqlite3.IntegrityError as e:
                        error = 'This is already an account, please try again!'
                        return render_template("signup.html", error=error)
                        con.commit()
                return redirect(url_for('login'))
        return self.success("Image Uploaded")

