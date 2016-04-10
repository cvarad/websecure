#!flask/bin/python

import flask
from flask import Flask, render_template, redirect, url_for, request, flash, make_response
from flask.ext.login import LoginManager, login_user, login_required, logout_user, current_user
from models import User, DB
import os
import psycopg2
import random
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

    import models
    models.set_conn_details(CONN_DETAILS)

except Exception as e:
    pass

app = Flask(__name__)
app.config.from_object('config')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(email):
    return User.get(email)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next = request.args.get('next')

    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']

        if User.exists(email, password):
            user = User.get(email)
            login_user(user)
            create_purchases_text(current_user.email, current_user.id)

            next = request.form['next']
            if next == 'None':
                next = None
            return redirect(next or url_for('catalogue'))

        else:
            error = "Invalid Credentials"

    return render_template('login.html',
                            error=error,
                            next=next,
                            addr=request.remote_addr)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = None
    if request.method == 'POST':
        status = User.create(request.form)
        if status:
            message = """Account created successfully!
                Please Log in to continue."""
        else:
            message = 'User already exists!'

    return render_template('signup.html',
                            message=message)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_account():
    message = None
    if request.method == 'POST':
        current_user.update(request.form)
        message = 'Details updated successfully!'

    return render_template('edit.html',
                            message=message)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/delete')
@login_required
def delete():
    current_user.delete()
    return logout()


@app.route('/catalogue')
@login_required
def catalogue(query=None):
    rows = DB.get_products(query)[:20]

    images = list()
    directory = os.path.join(os.getcwd(), 'static/images/')
    files = os.listdir(directory)
    for i in range(len(rows)):
        images.append('static/images/' + random.choice(files))

    r = make_response(
            render_template('catalogue.html',
                            query=query,
                            products=rows,
                            images=images,
                            dim=(140, 170),
                            columns=3)
        )

    r.headers.set('X-XSS-Protection', '0')
    return r


@app.route('/details')
@login_required
def details(product_id=None, msg=None):
    product_id = product_id or request.args.get('id')
    if not product_id:
        return redirect(url_for('catalogue'))

    row = DB.get_product(product_id)
    return render_template('details.html',
                            message=msg,
                            product=row)


@app.route('/buy')
def buy():
    product_id = request.args.get('id')
    current_user.on_purchase(product_id)
    msg = 'Congrats! Purchase Successful'
    return details(product_id, msg)


@app.route('/purchases', methods=['POST'])
def purchases():
    email = request.form['email']
    rows = DB.get_purchases(email)
    print rows
    return render_template('purchases.html',
                            products=rows)

@app.route('/search')
@login_required
def search():
    query = request.args.get('query')
    return catalogue(query=query)


@app.route('/file', methods=['POST'])
def serve_file():
    file_name = request.form['name']
    return flask.send_file( 'purchase_records/'+file_name,
                            as_attachment=True,
                            attachment_filename=file_name)


def create_purchases_text(user_email, user_id):
    rows = DB.get_purchases(user_email)
    with open('purchase_records/'+str(user_id)+'.csv', 'w') as f:
        for row in rows:
            f.write('{}, {}\n'.format(row[0], row[1]))


if __name__ == '__main__':
    CONN_DETAILS = {
        'database': 'mydb',
        'user': 'postgres',
        'password': 'varad',
        'host': '127.0.0.1',
        'port': '5432'
    }

    import models
    models.set_conn_details(CONN_DETAILS)
    app.run(debug=True, host='0.0.0.0')
