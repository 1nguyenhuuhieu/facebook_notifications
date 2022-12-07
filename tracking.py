from flask import Flask
from flask import render_template
import sqlite3

app = Flask(__name__)

@app.route("/post-checked/")
def hello_world(context = None):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM post_checked ORDER BY checked_time DESC LIMIT 30")
    context = res.fetchall()
    con.close()

    return render_template('base.html', context=(("test1"), ("test2")))