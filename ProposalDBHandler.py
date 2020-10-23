import sqlite3
from sqlite3 import Error


class ProposalDBHandler():
    def __init__(self, path):
        self.db_path = path

    def create_connection(self):
        database_path = self.db_path
        try:
            conn = sqlite3.connect(database_path)
            # print(f'Connected to {database_path}')
        except Error as err:
            print('Failed to connect to database', err)
        return conn

    def create_engineers_table(self):
        conn = self.create_connection()
        table = """ CREATE TABLE IF NOT EXISTS engineers (
                    id integer PRIMARY KEY,
                    name text NOT NULL UNIQUE,
                    position text NOT NULL,
                    email text NOT NULL,
                    photo text NOT NULL
                ); """
        if conn is not None:
            try:
                conn.execute(table)
                return True
            except Error as err:
                print('Unable to create Engineers table', err)
        else:
            print('Not connected')
        conn.close()
        return False

    def get_engineer_info(self, obj_id, field_name):
        conn = self.create_connection()
        curr = conn.cursor()
        curr.execute(f"select {field_name} from engineers where id=?",
                     (obj_id,))
        field_content = curr.fetchall()
        conn.close()
        return self.serialize(field_content, 'obj')

    def get_all_engineers_id(self):
        conn = self.create_connection()
        curr = conn.cursor()
        curr.execute("select id from engineers")
        engineers_id = curr.fetchall()
        conn.close()
        if engineers_id:
            return self.serialize(engineers_id, 'list')
        return None

    def save_new_engineer_to_db(self, template_engineer_dict):
        db_list = [field for field in template_engineer_dict.values()]
        content = (db_list[0][1], db_list[1][1], db_list[2][1], db_list[3][1])

        conn = self.create_connection()
        with conn:
            curr = conn.cursor()
            curr.execute(''' insert into engineers(name,position,email,photo)
                    values(?,?,?,?)''', content)
            conn.commit()
        print(f'Engineer with id {curr.lastrowid} was added to DB')
        conn.close()

    def serialize(self, content, content_type):
        data = [db_data[0] for db_data in content]
        if content_type == 'list':
            return data
        elif content_type == 'obj':
            return data[0]
