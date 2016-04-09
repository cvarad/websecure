import os
import psycopg2
import urlparse

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

cur = conn.cursor()

cur.execute("""DROP TABLE IF EXISTS Users;""")
cur.execute("""DROP TABLE IF EXISTS Passwords;""")

cur.execute("""CREATE TABLE Users (
    id serial,
    fname text,
    lname text,
    email text primary key,
    age integer,
    admin boolean);""")

cur.execute("""CREATE TABLE Passwords (
    email text references Users(email),
    password text);""")

cur.execute("""CREATE TABLE Purchases (
    email text references Users(email),
    product_id text references Products(id));""")

cur.execute("""INSERT INTO Users (fname, lname, email, age, admin) VALUES
    ('Varad', 'Deolankar', 'varaddeolankar@gmail.com', 21, 'true'),
    ('Varad', 'Raut', 'varadraut@gmail.com', 21, 'true'),
    ('Maitri', 'Vasa', 'maitrivasa15@gmail.com', 21, 'true'),
    ('Abigail', 'Fernandes', 'abigailferns94@gmail.com', 21, 'false'),
    ('Sushmita', 'Muthe', 'sush.muthe594@gmail.com', 21, 'false');""")

cur.execute("""INSERT INTO Passwords VALUES
    ('varaddeolankar@gmail.com', 'varadrocks'),
    ('varadraut@gmail.com', 'smartvarad'),
    ('maitrivasa15@gmail.com', 'technorocks'),
    ('abigailferns94@gmail.com', 'imthebest'),
    ('sush.muthe594@gmail.com', 'notinterested');""")

conn.commit()
conn.close()
print "All done! :D holy crap this is awesome!"
