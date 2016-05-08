from flask.ext.login import UserMixin
import psycopg2, psycopg2.extras

CONN_DETAILS = dict()
def set_conn_details(details):
    global CONN_DETAILS
    CONN_DETAILS = details

class User(UserMixin):
    def __init__(self, id, fname, lname, email, age, admin, active=True):
        self.id = id
        self.fname = fname
        self.lname = lname
        self.email = email
        self.age = age
        self.admin = admin
        self.active = active
        self.cart = list()

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.email

    def update(self, form):
        self.fname = form['fname']
        self.lname = form['lname']
        self.age = int(form['age'])
        password = form['password']

        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        cur.execute(''' UPDATE Users
                        SET (fname, lname, age) = (%s, %s, %s)
                        WHERE email = (%s)''',
                        (self.fname, self.lname, self.age, self.email))
#        cur.execute(''' UPDATE Passwords
#                        SET password = (%s)
#                        WHERE email = (%s)''',
#                        (form['password'], self.email))

        cur.execute("UPDATE Passwords SET password='" + password + "' WHERE email='" + self.email + "'")
        conn.commit()
        conn.close()

    def delete(self):
        """ Deletes all details about the user from the DB """
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        cur.execute("""DELETE FROM Users WHERE email=(%s)""", (self.email,))
        cur.execute("""DELETE FROM Passwords WHERE email=(%s)""", (self.email,))
        conn.commit()
        conn.close()

    def on_purchase(self, product_id_list):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        for _id in product_id_list:
            cur.execute("""INSERT INTO Purchases VALUES
                (%s, %s)""", (self.email, _id))
        conn.commit()
        conn.close()

    def get_purchases(self):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        cur.execute('''SELECT product_id FROM Purchases WHERE email=(%s)''', (self.email,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def set_cart(self, products):
        for _id in products:
            row = DB.get_product(_id)
            product = {k:row[k] for k in ['id', 'title', 'price']}
            self.cart.append(product)


    @staticmethod
    def get(email):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        cur.execute("SELECT id, fname, lname, email, age, admin FROM Users WHERE email='" + email + "';")
        user = cur.fetchone()
        conn.close()

        return User(*user)

    @staticmethod
    def exists(email, password=None):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        if password is None:
            #cur.execute("SELECT * FROM Users WHERE email='" + email + "';")
            cur.execute("SELECT * FROM Users WHERE email=(%s)", (email,))
        else:
            # Line vulnerable to SQL Injection
            cur.execute("SELECT * FROM Passwords WHERE email='" + email + "' AND password='" + password + "';")

        user = cur.fetchone()
        conn.close()

        return False if not user else True

    @staticmethod
    def create(user):
        """ Creates a new user if not already present in database """
        if not User.exists(user['email']):
            conn = psycopg2.connect(**CONN_DETAILS)
            cur = conn.cursor()
            cur.execute("""INSERT INTO Users (fname, lname, email, age, admin) VALUES
                (%s, %s, %s, %s, %s)""", (user['fname'], user['lname'], user['email'], user['age'], 'f'))
            cur.execute("""INSERT INTO Passwords VALUES
                (%s, %s)""", (user['email'], user['password']))
            conn.commit()
            conn.close()

            return True

        return False


class DB():
    """docstring for DB"""
    def __init__(self):
        pass

    @staticmethod
    def get_products(query=None):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()

        if query is None:
            cur.execute('''SELECT id, title, manufacturer, price FROM Products;''')
        else:
            cur.execute(""" SELECT id, title, manufacturer, price
                            FROM products
                            WHERE title LIKE '%""" +query+ """%'""")

        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_product(id):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute(''' SELECT *
                        FROM products
                        WHERE id=(%s)''',
                        (id,))

        row = cur.fetchone()
        conn.close()
        return row

    @staticmethod
    def get_purchases(email):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()

        cur.execute(''' SELECT title, price
                        FROM Users, Products, Purchases
                        WHERE Users.email=(%s)
                            AND Purchases.email=Users.email
                            AND Products.id=product_id''',
                        (email,))

        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_comment(email, product_id, comment):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()

        cur.execute(''' INSERT INTO Comments VALUES
            (%s, %s, %s, CURRENT_TIMESTAMP)''', (email, product_id, comment))

        conn.commit()
        conn.close()

    @staticmethod
    def get_comments(product_id):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()

        cur.execute(''' SELECT fname, lname, comment, timestamp
                        FROM Users, Comments
                        WHERE Comments.product_id=(%s)
                            AND Users.email=Comments.email''',
                        (product_id,))

        rows = cur.fetchall()
        conn.close()
        return rows
