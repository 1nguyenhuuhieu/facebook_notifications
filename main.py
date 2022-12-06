from typing import Union
import sqlite3
import json

from fastapi import FastAPI

app = FastAPI()


@app.get("/post-uncheck")
def read_root():
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    res = cur.execute("SELECT post_id FROM post")
    context = res.fetchall()
    con.close()
    jsonString = json.dumps(context)
    return jsonString

@app.get("/post-checked")
def post_checked():
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM post_checked")

    r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in res.fetchall()]

    con.close()
    jsonString = json.dumps(r, ensure_ascii=False)
    return jsonString