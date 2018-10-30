import sqlite3 as sql


def insertUser(username,password):
    con = sql.connect("flaskit.db")
    cur = con.cursor()
    cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
    con.commit()
    con.close()

def retrieveUsers(username,password):
    con = sql.connect("flaskit.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = username & password = password ")
    users = cur.fetchall()
    con.close()
    return users