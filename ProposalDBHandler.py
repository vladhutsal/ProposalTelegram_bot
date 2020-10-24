import sqlite3
from sqlite3 import Error, IntegrityError
from Proposal import Proposal


class ProposalDBHandler(Proposal):
    def __init__(self, path):
        Proposal.__init__(self)
        self.db_path = path
        self.table_exc = None
        self.table = 'proposal'
        self.engineers_in_proposal_id = []

    def create_connection(self):
        database_path = self.db_path
        try:
            conn = sqlite3.connect(database_path)
            # print(f'Connected to {database_path}')
        except Error as err:
            print('Failed to connect to database', err)
        return conn

    def create_table(self, name='engineers'):
        conn = self.create_connection()
        table = f""" CREATE TABLE IF NOT EXISTS {name} (
                    id integer PRIMARY KEY,
                    N text NOT NULL UNIQUE,
                    P text NOT NULL,
                    EM text NOT NULL,
                    PHT text NOT NULL
                ); """
        if conn is not None:
            try:
                conn.execute(table)
                return True
            except Error as err:
                print(f'Unable to create {name} table', err)
        else:
            print('Not connected')
        conn.close()
        return False

    def get_all_engineers_in_proposal(self):
        engn_template = self.engineer_template
        list_of_engn_dicts = []
        proposal_ids = self.engineers_in_proposal_id

        for engn_id in proposal_ids:
            engn_content = self.get_engineer(engn_id)
            for title_id in engn_template.keys():
                engn_template[title_id][1] = engn_content.pop(0)
            list_of_engn_dicts.append(engn_template)
            self.reset_engineer_template()
        return list_of_engn_dicts

    def get_engineer(self, engn_id):
        conn = self.create_connection()
        cur = conn.cursor()
        cur.execute(f'select * from {self.table} where id=?', (engn_id,))
        engineer = self.deserialize(cur.fetchall(), 'fields', conn)[1:]
        return engineer

    def get_all_engineers_id(self):
        conn = self.create_connection()
        cur = conn.cursor()
        cur.execute(f"select id from {self.table}")
        engineers_id = cur.fetchall()
        if engineers_id:
            return self.deserialize(engineers_id, 'column', conn)
        return None

    def get_field_info(self, obj_id, field_name):
        conn = self.create_connection()
        cur = conn.cursor()
        cur.execute(f"select {field_name} from {self.table} where id=?",
                    (obj_id,))
        field_content = cur.fetchall()
        return self.deserialize(field_content, 'field', conn)

    def store_new_engineer_to_db(self, template_engineer_dict):
        content = self.serialize(template_engineer_dict)
        conn = self.create_connection()
        cur = conn.cursor()
        try:
            cur.execute(f''' insert into {self.table}(N,P,EM,PHT)
                            values(?,?,?,?)''', content)
            conn.commit()
        except IntegrityError:
            conn.close()
            return 'This engineer is already in db'

        print(f'Engineer with id {cur.lastrowid} was added to DB')
        conn.close()

    def deserialize(self, content, content_type, conn):
        if content_type == 'column':
            # only works if ID from 0 to 9
            conn.close()
            return [field[0] for field in content]
        elif content_type == 'fields':
            conn.close()
            return [field for field in content[0]]
        elif content_type == 'field':
            conn.close()
            return content[0][0]
    
    def serialize(self, content):
        db_list = [field for field in content.values()]
        return (db_list[0][1], db_list[1][1], db_list[2][1], db_list[3][1])
