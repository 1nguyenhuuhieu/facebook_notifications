from flask import Flask
from flask import render_template
import sqlite3
import json

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
    screenshot = "google.png"
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM post_checked ORDER BY checked_time DESC LIMIT 30")
    posts = res.fetchall()
    monitor = cur.execute("SELECT * FROM monitor_collector ORDER BY start_time DESC LIMIT 1")
    monitor = monitor.fetchone()

    monitor_post = cur.execute("SELECT * FROM monitor_post_checker ORDER BY start_time DESC LIMIT 1").fetchone()
    context = {
        "monitor": monitor,
        "posts": posts,
        "monitor_post": monitor_post,
        "keywords": keywords,
        "screenshot": screenshot
    }
    con.close()

    return render_template('base.html', context=context)