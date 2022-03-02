import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def select_friends(conn):

    cur = conn.cursor()
    cur.execute(''' SELECT id, name FROM friends ''')
    rows = cur.fetchall()

    return rows

def select_friend(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT name, age, bored, food, exhausted, alive FROM friends where id =?", (id,))
    return cur.fetchone()

def select_user(conn):
    cur = conn.cursor()
    cur.execute("SELECT name from users")
    return cur.fetchone()

def update_friends(conn, friend):
    
    sql = ''' UPDATE friends
              SET age = ? ,
                  bored = ? ,
                  food = ? ,
                  exhausted = ? ,
                  alive = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, friend)
    conn.commit()

def create_friends(conn, friend):
    sql = ''' INSERT INTO friends(name,age,bored,food,exhausted,alive)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, friend)
    conn.commit()

    return cur.lastrowid

def create_user(conn, name):
    sql = " INSERT INTO users(name) VALUES('" + name + "')"
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

    return cur.lastrowid

def config_db():
    database = r"sqlite.db"

    sql_create_user_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL
                                    ); """

    sql_create_friend_table = """CREATE TABLE IF NOT EXISTS friends (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    age integer,
                                    food integer NOT NULL,
                                    bored integer NOT NULL,
                                    exhausted integer NOT NULL,
                                    alive boolean NOT NULL
                                );"""

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_user_table)
        create_table(conn, sql_create_friend_table)
    else:
        print("Error! cannot create the database connection.")


