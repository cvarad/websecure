from flask import Flask, render_template, redirect, url_for, request
import os
import psycopg2
import urlparse

try:
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])
    CONN_DETAILS = {
        'database': url.path[1:],
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port
    }

except Exception as e:
    pass

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        cur.execute("""SELECT * FROM Users;""")
        rows = cur.fetchall()
        for row in rows:
            if row[2] == request.form['email'] and row[3] == request.form['password']:
                return redirect(url_for('success'))

        return "Invalid Credentials"
        conn.close();

    except:
        return "Failed :/"


@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    CONN_DETAILS = {
        'database': 'mydb',
        'user': 'postgres',
        'password': 'varad',
        'host': '127.0.0.1',
        'port': '5432'
    }

    app.run(debug=True)
