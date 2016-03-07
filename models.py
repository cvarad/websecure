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

    @staticmethod
    def get(email, CONN_DETAILS):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        cur.execute("SELECT fname, lname, email, age FROM Users WHERE email='" + email + "';")
        user = cur.fetchone()
        conn.close()

        return User(*user)

    @staticmethod
    def exists(email, password, CONN_DETAILS):
        conn = psycopg2.connect(**CONN_DETAILS)
        cur = conn.cursor()
        # Line vulnerable to SQL Injection
        cur.execute("SELECT * FROM Passwords WHERE email='" + email + "' AND password='" + password + "';")
        user = cur.fetchone()
        conn.close()

        return False if not user else True
