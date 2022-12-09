from flask import Flask
from flask import render_template
import sqlite3
import json
import psutil
import platform
import os
from config import init

file_path = "config.ini"
config = init(file_path)

keyword_filepath = config["KEYWORDS"]["file_path"]

def load_json_file(file_path):
    file = open(file_path, encoding='utf-8')
    items_json = json.load(file)
    file.close()

    return [item for item in items_json.values()]

keywords = load_json_file(keyword_filepath)    

app = Flask(__name__)

@app.route("/")
def index(context = None):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM post_checked ORDER BY checked_time DESC LIMIT 10")
    posts = res.fetchall()
    monitor = cur.execute("SELECT * FROM monitor_collector ORDER BY start_time DESC LIMIT 1")
    monitor = monitor.fetchone()

    monitor_post = cur.execute("SELECT * FROM monitor_post_checker ORDER BY start_time DESC LIMIT 1").fetchone()

    cpu_usage = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory()[2]
    ram_used = "{:.2f}".format(psutil.virtual_memory()[3]/1000000000)
    os_info = platform.platform()

    context = {
        "monitor": monitor,
        "posts": posts,
        "monitor_post": monitor_post,
        "keywords": keywords,
        "cpu_usage": cpu_usage,
        "ram_percent": ram_percent,
        "ram_used": ram_used,
        "os_info": os_info
        
    }
    con.close()

    return render_template('index.html', context=context)


@app.route("/post-checked/")
def post_checked(context = None):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM post_checked ORDER BY checked_time DESC LIMIT 1000")
    posts = res.fetchall()

    cpu_usage = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory()[2]
    ram_used = "{:.2f}".format(psutil.virtual_memory()[3]/1000000000)
    os_info = platform.platform()

    context = {
        "posts": posts,
        "keywords": keywords,
        "cpu_usage": cpu_usage,
        "ram_percent": ram_percent,
        "ram_used": ram_used,
        "os_info": os_info
        
    }
    con.close()

    return render_template('post-checked.html', context=context)

@app.route("/post-found/")
def post_found(context = None):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM post_checked WHERE status = 'found' ORDER BY checked_time DESC LIMIT 1000")
    posts = res.fetchall()

    cpu_usage = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory()[2]
    ram_used = "{:.2f}".format(psutil.virtual_memory()[3]/1000000000)
    os_info = platform.platform()

    context = {
        "posts": posts,
        "keywords": keywords,
        "cpu_usage": cpu_usage,
        "ram_percent": ram_percent,
        "ram_used": ram_used,
        "os_info": os_info
        
    }
    con.close()

    return render_template('post-found.html', context=context)
