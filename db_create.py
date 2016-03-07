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

cur.execute("""CREATE TABLE Users (
    id serial,
    fname text,
    lname text,
    email text,
    age integer);""")

cur.execute("""CREATE TABLE Passwords (
    email text,
    password text);""")

cur.execute("""INSERT INTO Users (fname, lname, email, password, age) VALUES
    ('Varad', 'Deolankar', 'varaddeolankar@gmail.com', 21),
    ('Varad', 'Raut', 'varadraut@gmail.com', 21),
    ('Maitri', 'Vasa', 'maitrivasa15@gmail.com', 21),
    ('Abigail', 'Fernandes', 'abigailferns94@gmail.com', 21),
    ('Sushmita', 'Muthe', 'sush.muthe594@gmail.com', 21);""")

cur.execute("""INSERT INTO Passwords VALUES
    ('varaddeolankar@gmail.com', 'varadrocks'),
    ('varadraut@gmail.com', 'smartvarad'),
    ('maitrivasa15@gmail.com', 'technorocks'),
    ('abigailferns94@gmail.com', 'imthebest'),
    ('sush.muthe594@gmail.com', 'notinterested');""")

conn.commit()
conn.close()
print "All done! :D holy crap this is awesome!"
