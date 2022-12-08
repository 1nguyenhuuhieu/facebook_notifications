import sqlite3

data= {
    "status":"tốt",
    "count_post": 100,
    "last_time": "update_test",
    "start_time": "2022-12-08 16:02:59 "
}


def update_monitor(data):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    cur.execute("""
    UPDATE monitor_collector
    SET status = :status, count_post = :count_post, last_time = :last_time
    WHERE start_time = :start_time
    """, data)
    con.commit()
    con.close()

    return None

update_monitor(data)