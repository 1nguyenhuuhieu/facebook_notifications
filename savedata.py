import sqlite3

con = sqlite3.connect("fb.db")
cur = con.cursor()
cur.execute("CREATE TABLE post(status, keywords_found, groupa, post_id, post_text, checked_time)")
cur.execute("""
    INSERT INTO post VALUES
        ('found', "mua, tìm", 'bdshadong', '132456', "ví dụ về một bài viết", '2022-12-04' )
""")

con.commit()