from typing import Union
import sqlite3

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    res = cur.execute("SELECT post_id FROM post")
    context = res.fetchall()
    con.close()
    return context


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}