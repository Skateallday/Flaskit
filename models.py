import sqlite3 as sql


def insertUser(username,password):
    con = sql.connect("flaskit.db")
    cur = con.cursor()
    cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
    con.commit()
    con.close()

