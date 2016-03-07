from flask import Flask, render_template, redirect, url_for, request, flash
from flask.ext.login import LoginManager, login_user, login_required, logout_user
from models import User
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
app.config.from_object('config')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(email):
    return User.get(email, CONN_DETAILS)


@app.route('/', methods=['GET', 'POST'])
def index():
    return 'NOTHING HERE'


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next = request.args.get('next')
    print next

    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']

        if User.exists(email, password, CONN_DETAILS):
            user = User.get(email, CONN_DETAILS)
            login_user(user)

            next = request.form['next']
            return redirect(next or url_for('catalogue'))

        else:
            error = "Invalid Credentials"

    return render_template('login.html',
                            error=error,
                            next=next)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/catalogue')
@login_required
def catalogue():
    conn = psycopg2.connect(**CONN_DETAILS)
    cur = conn.cursor()

    cur.execute('''SELECT id, title, manufacturer, price FROM Products;''')
    rows = cur.fetchall()
    rows = rows[:100]

    return render_template('catalogue.html',
                            products=rows,
                            columns=4)


if __name__ == '__main__':
    CONN_DETAILS = {
        'database': 'mydb',
        'user': 'postgres',
        'password': 'varad',
        'host': '127.0.0.1',
        'port': '5432'
    }

    app.run(debug=True)
