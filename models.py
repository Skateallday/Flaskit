import sqlite3 as sql
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import ModelFormWithFileField

def upload_file(request):
    if request.method == 'POST':
        form = ModelFormWithFileField(request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            form.save()
            return HttpResponseRedirect('/success/url/')
    else:
        form = ModelFormWithFileField()
    return render(request, 'upload.html', {'form': form})

def insertUser(username,password):
    con = sql.connect("instaslam.db")
    cur = con.cursor()
    cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
    con.commit()
    con.close()

def retrieveUsers(username,password):
    con = sql.connect("instaslam.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = username & password = password ")
    users = cur.fetchall()
    con.close()
    return users