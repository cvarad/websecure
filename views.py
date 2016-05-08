#!flask/bin/python

import flask
from flask import Flask, render_template, redirect, url_for, request, flash, make_response, session
from flask.ext.login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.contrib.fixers import ProxyFix
from models import User, DB
import logging
import sys
import os
import psycopg2
import random
import urlparse
import re

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

# For error logging. Temporary.
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(email):
    return User.get(email)


@app.route('/')
@app.route('/index')
def index():
    print 'Remote Addr', request.remote_addr
    print 'X-Forwarded-For', request.headers.get('X-Forwarded-For')
    print 'X-Client-IP', request.headers.get('X-Client-IP')
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next = request.args.get('next')

    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        detect_attack(email); detect_attack(password)

        if User.exists(email, password):
            session['cart'] = list()    # Add 'cart' to the current user session.

            user = User.get(email)
            login_user(user)
            create_purchases_text(current_user.email, current_user.id)

            next = request.form['next']
            if next == 'None':
                next = None
            elif 'http' in next:
                print 'Unvalidated Redirect detected!'
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
        detect_attack(request.form['password'])

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

    product = DB.get_product(product_id)
    rows = DB.get_comments(product_id)
    comments = list()
    for row in rows:
        comment = dict()
        comment['name'] = ' '.join(row[:2])
        comment['text'] = row[2]
        comment['date'], comment['time'] = row[3].split()
        comment['time'] = comment['time'].split('.')[0]
        comments.append(comment)

    r = make_response(
            render_template('details.html',
                            message=msg,
                            product=product,
                            comments=comments)
        )

    r.headers.set('X-XSS-Protection', '0')
    return r


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
    return render_template('purchases.html',
                            products=rows)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    msg = None

    if request.method == 'POST':
        mode = request.form['mode']
        if mode == 'clear':
            session['cart'] = list()
        elif mode == 'checkout':
            current_user.on_purchase(session['cart'])
            session['cart'] = list()
            msg = 'Items successfully purchased!'
        elif mode == 'add':
            product_id = request.form['product_id']
            session['cart'].append(product_id)

    current_user.set_cart(session['cart'])
    total = sum([product['price'] for product in current_user.cart])
    return render_template('cart.html',
                            cart=current_user.cart,
                            total=total,
                            msg=msg)


@app.route('/comment', methods=['POST'])
def comment():
    email = current_user.email
    product_id = request.form['product_id']
    comment = request.form['comment']

    detect_attack(comment)
    DB.add_comment(email, product_id, comment)
    return redirect(url_for('details', id=product_id))


@app.route('/search')
@login_required
def search():
    query = request.args.get('query')

    detect_attack(query)
    return catalogue(query=query)


@app.route('/file', methods=['POST'])
def serve_file():
    file_name = request.form['name']

    check_file = file_name.split('/')[-1]
    if not os.path.isfile('purchase_records/'+check_file):
        print 'Potential Insecure Direct Object Reference Attack'

    if current_user.is_authenticated:
        create_purchases_text(current_user.email, current_user.id)
    return flask.send_file( 'purchase_records/'+file_name,
                            as_attachment=True,
                            attachment_filename=file_name)


@app.route('/iprecv', methods=['POST'])
def iprecv():
    ip_addr = request.form['addr']
    print "Client's Internal/External IP:", ip_addr
    return "Success"


@app.route('/address')
def address():
    return "Your IP Address is: %s\n" % str(request.remote_addr)


''' Methods below are not a part of the Main Website '''
@app.route('/steal')
def steal():
    print 'Cookie stolen: ', request.args.get('cookie')
    return 'Cookie stolen'


def create_purchases_text(user_email, user_id):
    rows = DB.get_purchases(user_email)
    with open('purchase_records/'+str(user_id)+'.csv', 'w') as f:
        for row in rows:
            f.write('{}, {}\n'.format(row[0], row[1]))


def detect_attack(input):
    if SQLIre.match(input):
        print 'SQL Injection detected!'
    elif XSSre1.match(input):
        print 'XSS detected!'
    elif XSSre2.match(input):
        print 'XSS of type "<img src.." detected'


app.wsgi_app = ProxyFix(app.wsgi_app)

#SQLIre = re.compile("(\%27)|(\')|(\-\-)")
SQLIre = re.compile("[a-zA-Z0-9_ ]*((\%27)|(\'))([ ]*)((\%6F)|o|(\%4F))((\%72)|r|(\%52))", re.I)
XSSre1 = re.compile("[^<\%3C]*((\%3C)|<)((\%2F)|\/)*[a-z0-9\%]+((\%3E)|>)", re.I)
XSSre2 = re.compile("[^<\%3C]*((\%3C)|<)((\%69)|i|(\%49))((\%6D)|m|(\%4D))((\%67)|g|(\%47))[^\n]+((\%3E)|>)", re.I)

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
    app.run(debug=True, host='0.0.0.0', threaded=True)
