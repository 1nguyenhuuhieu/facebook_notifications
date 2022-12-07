from typing import Union
import sqlite3
import json
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

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

@app.get("/post-checked/")
def post_checked():
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM post_checked")
    context = res.fetchall()

    c = "\n".join(list(context))


    con.close()

    return c
    