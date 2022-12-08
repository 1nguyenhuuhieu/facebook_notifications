from flask import Flask
from flask import render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def hello_world(context = None):
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
        "monitor_post": monitor_post
    }
    con.close()

    return render_template('base.html', context=context)