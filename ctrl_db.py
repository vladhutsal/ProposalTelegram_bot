import sqlite3
from sqlite3 import Error


database = 'proposal.db'


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print('connected to db')
    except Error as err:
        print(err)
    return conn


def create_templates_table(conn):
    table = """ CREATE TABLE IF NOT EXISTS engineers (
                id integer PRIMARY KEY,
                name text NOT NULL,
                position text NOT NULL,
                email text NOT NULL,
                photo text NOT NULL
            ); """
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(table)
            return True
        except Error as err:
            print(err)
    else:
        print('error')
    return False


def db_exists(func):
    def check_existance(content):
        conn = create_connection(database)
        curr = conn.cursor()
        print(curr.rowcount)
        if not curr.rowcount or curr.rowcount == -1:
            create_templates_table(conn)
            conn.close()
            return func(content)
        conn.close()
        return func(content)
    return check_existance


@db_exists
def add_new_engineer(content):
    conn = create_connection(database)

    with conn:
        sql = ''' INSERT INTO engineers(name,position,email,photo)
                 VALUES(?,?,?,?)'''
        # ('Anton', 'QA engineer', 'anton@mail.com', '\x02')
        curr = conn.cursor()
        curr.execute(sql, content)
        conn.commit()
        eng_id = curr.lastrowid
    conn.close()
    return eng_id


def get_engineer(id):
    conn = create_connection(database)
    curr = conn.cursor()
    curr.execute("SELECT * FROM engineers WHERE id=?", (id,))
    data = curr.fetchall()
    conn.close()
    return data


def main():
    pass
    # content = ('Anton', 'QA engineer', 'anton@mail.com', '\x02')
    # add_new_engineer(content)
    # conn = create_connection(database)
    # if create_templates_table(conn):
    #     get_all_engineers(conn)
    # rows = select_template_by_priority(conn, "MCG")
    # print(rows)


if __name__ == "__main__":
    main()
