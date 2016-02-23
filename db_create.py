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
    fname text,
    lname text,
    email text,
    password text,
    age integer);""")

cur.execute("""INSERT INTO Users (fname, lname, email, password, age) VALUES
    ('Varad', 'Deolankar', 'varaddeolankar@gmail.com', 'varadrocks', 21),
    ('Varad', 'Raut', 'varadraut@gmail.com', 'smartvarad', 21),
    ('Maitri', 'Vasa', 'maitrivasa15@gmail.com', 'technorocks', 21),
    ('Abigail', 'Fernandes', 'abigailferns94@gmail.com', 'imthebest', 21),
    ('Sushmita', 'Muthe', 'sush.muthe594@gmail.com', 'notinterested', 21);""")

conn.commit()
conn.close()
print "All done! :D holy crap this is awesome!"
