from flask import Flask
import os
import psycopg2
import urlparse

app = Flask(__name__)

@app.route('/')
def index():
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    try:
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        cur = conn.cursor()
        cur.execute("""SELECT * FROM User""")
        rows = cur.fetchall()
        for row in rows:
            print row

        return "Connection successful"
    except:
        return "Failed! :("
