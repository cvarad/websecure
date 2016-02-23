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
        cur.execute("""SELECT * FROM Users;""")
        rows = cur.fetchall()
        for row in rows:
            if row[2] == request.form['email'] and row[3] == request.form['password']:
                return redirect(url_for('success'))
                
        conn.close();
        return render_template('index.html',
                                data=rows,
                                error=error)
    except:
        return "Failed :/"

      
@app.route('/success', methods=['GET', 'POST'])
def success():
    return render_template('success')