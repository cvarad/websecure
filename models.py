from flask.ext.login import UserMixin
import psycopg2

class User(UserMixin):
    def __init__(self, fname, lname, email, age, active=True):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.age = age
        self.active = active

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.email

    def update(self, form, CONN_DETAILS):
        self.fname = form['fname']
        self.lname = form['lname']
        self.age = int(form['age'])

        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        cur.execute(''' UPDATE Users
                        SET (fname, lname, age) = (%s, %s, %s)
                        WHERE email = (%s)''',
                        (self.fname, self.lname, self.age, self.email))
        cur.execute(''' UPDATE Passwords
                        SET password = (%s)
                        WHERE email = (%s)''',
                        (form['password'], self.email))
        conn.commit()
        conn.close()

    @staticmethod
    def get(email, CONN_DETAILS):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        cur.execute("SELECT fname, lname, email, age FROM Users WHERE email='" + email + "';")
        user = cur.fetchone()
        conn.close()

        return User(*user)

    @staticmethod
    def exists(CONN_DETAILS, email, password=None):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        if password is None:
            cur.execute("SELECT * FROM Users WHERE email='" + email + "';")
        else:
            # Line vulnerable to SQL Injection
            cur.execute("SELECT * FROM Passwords WHERE email='" + email + "' AND password='" + password + "';")

        user = cur.fetchone()
        conn.close()

        return False if not user else True

    @staticmethod
    def create(user, CONN_DETAILS):
        """ Creates a new user if not already present in database """
        if not User.exists(CONN_DETAILS, user['email']):
            conn = psycopg2.connect(**CONN_DETAILS)
            cur = conn.cursor()
            cur.execute("""INSERT INTO Users (fname, lname, email, age) VALUES
                (%s, %s, %s, %s)""", (user['fname'], user['lname'], user['email'], user['age']))
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
    def get_products(CONN_DETAILS, query=None):
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
