import os
import time
import sched
import threading
import inquirer
import sqlite3
from sqlite3 import Error

class Friend:
    age = 0
    bored = 0
    food = 100
    exhausted = 0
    alive = 1

    def __init__(self):

        database = r"db/sqlite.db"
        self.conn = create_connection(database)
        friends = select_friends(self.conn)
        new = True

        if friends:
            choices = [(friend[1],friend[0]) for friend in friends]
            choices.append(("Criar um novo",0))
            question = [
                inquirer.List("id", "Gostaria de selecionar um amigo existente?",
                choices=choices)
            ]
            answer = inquirer.prompt(question)
            if answer.get('id') != 0:
                new = False
                self.id = answer.get('id')
        if new:
            question = [
                inquirer.Text(
                    "name", message="Qual é o nome do seu melhor amigo virtual?")
            ]
            answer = inquirer.prompt(question)
            self.name = answer.get("name")
            self.id = create_friends(self.conn,(self.name, self.age, self.bored, self.food, self.exhausted, self.alive))
        
        friend_selected = select_friend(self.conn, self.id)
        self.name = friend_selected[0]
        self.age = friend_selected[1]
        self.bored = friend_selected[2]
        self.food = friend_selected[3]
        self.exhausted = friend_selected[4]
        self.alive = friend_selected[5]

    def activity_eat(self):
        self.food = self.food + 2.5
        return ("Nhac nhac!", 3.5)

    def activity_drink(self):
        self.food = self.food + 0.5
        return ("Glub glub!...", 2.5)

    def activity_workout(self):
        self.food = self.food - 5
        self.bored = self.bored - 10
        self.exhausted = self.exhausted + 20
        return ("Sniff... Sniff...", 6)

    def activity_play(self):
        self.food = self.food - 2
        self.bored = self.bored - 20
        self.exhausted = self.exhausted + 10
        return ("Pow!! Kabum! Fire in the role!...", 4)

    def activity_sleep(self):
        self.exhausted = 0
        self.food = 20
        return ("Zzzzz...", 10)

    def pass_time(self):
        self.age = self.age + 0.2
        self.bored = self.bored + 2.5
        self.food = self.food - 5
        self.exhausted = self.exhausted + 0.5

        if self.food < -20 or self.exhausted >= 100:
            self.alive = 0

    def status(self):
        print(
            f"""
Nome: {self.name}
Idade: {round(self.age)}
Comida: {self.food}
Tédio: {self.bored}
Cansaço: {self.exhausted}
-----------
        """
        )

    def run(self):
        self.clear()
        self.status()
        update_friends(self.conn,(self.age, self.bored, self.food, self.exhausted, self.alive, self.id))
        question = [
            inquirer.List(
                "activity",
                message="O que faremos?",

                choices=[
                    ("Comida!", "eat"),
                    ("Sede!", "drink"),
                    ("Exercícios!!", "workout"),
                    ("Se divertir!!", "play"), 
                    ("Dormir (bzzz)!", "sleep")
                ],
            ),
        ]
        answer = inquirer.prompt(question)
        activity_name = "activity_{}".format(answer.get("activity")).lower()
        activity = getattr(self, activity_name, lambda: "Atividade inválida")
        (status, sleep) = activity()
        print(status)
        time.sleep(sleep)

    def clear(self):
        if os.name == "nt":
            _ = os.system("cls")
        else:
            _ = os.system("clear")


def main():
    tamago = Friend()

    s = sched.scheduler(time.time, time.sleep)

    def run(sc):
        tamago.pass_time()
        if tamago.alive == 1:
            s.enter(10, 1, run, (sc,))

    s.enter(10, 1, run, (s,))
    t = threading.Thread(target=s.run)
    t.start()

    while tamago.alive == 1:
        tamago.run()

    print(f"{tamago.name} morreu :(")



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
    sql = ''' INSERT INTO users(name)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, name)
    conn.commit()

    return cur.lastrowid

def manage_db():
    database = r"db/sqlite.db"

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


if __name__ == "__main__":
    try:
        manage_db()
        main()
    except KeyboardInterrupt:
        print(f"Adeus!")