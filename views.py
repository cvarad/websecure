from flask import Flask, render_template, redirect, url_for, request
import os
import psycopg2
import urlparse


app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
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

        error=None
        cur = conn.cursor()       
        cur.execute("""SELECT * FROM Users WHERE email = """ + request.form['email'] + """and password = """ + request.form['password'] + """;""")
        rows = cur.fetchall()
        for row in rows:
            print row

        conn.close();
        return redirect(url_for('index'))
        #return render_template('index.html',
        #                        data=rows,
        #                        error=error)
    except:
        return "Failed :/"
