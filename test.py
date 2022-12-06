import sqlite3
result = {
"status": status,
"keywords_found": keywords_found,
"group": group_id,
"post_id": post_id,
"post_text": post_text,
"checked_time": now
}


con = sqlite3.connect("fb.db")
cur = con.cursor()
cur.execute("INSERT INTO post_checked VALUES (:status, :keywords_found, :post_id, :group, :post_text, :checked_time)", result)
con.commit()
con.close()