import sqlite3
from sqlite3 import Error, IntegrityError
from . templates import engineer_template
from copy import deepcopy


# check for table existance
class ProposalDBHandler:
    def __init__(self):
        self.db_path = 'proposal.db'
        self.table = 'engineers'
        self.conn = None
        self.cur = None

        self.engineers_in_proposal_id = []
        self.engineers_rates = {}

    def create_connection(self):
        database_path = self.db_path
        try:
            conn = sqlite3.connect(database_path)
            # print(f'Connected to {database_path}')
        except Error as err:
            print('Failed to connect to database', err)
        return conn

    def work_with_connection(func):
        def checker(self, *args, **kwargs):
            self.conn = self.create_connection()
            self.cur = self.conn.cursor()
            self.cur.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{self.table}'")
            if self.cur.fetchone()[0] <= 0:
                self.create_table()
            res = func(self, *args, **kwargs)
            self.conn.close()
            return res
        return checker

    def create_table(self):
        table = f""" CREATE TABLE IF NOT EXISTS {self.table} (
                    id integer PRIMARY KEY,
                    N text NOT NULL UNIQUE,
                    P text NOT NULL,
                    EM text NOT NULL,
                    PHT text NOT NULL
                ); """
        if self.conn is not None:
            try:
                self.conn.execute(table)
                return True
            except Error as err:
                print(f'Unable to create {self.table} table', err)
        else:
            print('Not connected')
        return False

    def get_proposal_engineers(self):
        # 1. Create list_of_engn_dicts - list of dicts based on engineer_template
        # list_of_eng_dicts - all engineers in current proposal
        # 2. Add rate to each dictionary in list_of_engn_dicts.
        #
        # This method used in html_to_pdf(), when all data for current proposal
        # is retrieved from database and filled by user template-dicts.
        # engineers_rates is a dict like: {'RT': ['name', 'rate']}
        # field 'name' is used in show_title(), to show propper name of engineer,
        # instead of ID, when asking user for Rate of current engineer.
        list_of_engn_dicts = []
        proposal_ids = self.engineers_in_proposal_id
        # if something goes wrong, there will be two similar templates
        for engn_id in proposal_ids:
            template = deepcopy(engineer_template)
            content_from_db = self.get_engineer(engn_id)
            for title_id in template.keys():
                template[title_id][1] = content_from_db.pop(0)

            rate = self.engineers_rates[str(engn_id)][1]
            template['RT'] = ['Rate', rate]
            list_of_engn_dicts.append(template)
        return list_of_engn_dicts

    @work_with_connection
    def get_engineer(self, engn_id):
        cur = self.cur
        cur.execute(f'select * from {self.table} where id=?', (engn_id,))
        engineer = self.deserialize(cur.fetchall(), 'fields')
        return engineer[1:]

    @work_with_connection
    def get_engineers_id_list(self):
        cur = self.cur
        cur.execute(f"select id from {self.table}")
        engineers_id = cur.fetchall()
        if engineers_id:
            return self.deserialize(engineers_id, 'column')
        return None

    @work_with_connection
    def get_field_info(self, obj_id, field_name):
        cur = self.cur
        cur.execute(f"select {field_name} from {self.table} where id=?",
                    (obj_id,))
        field_content = cur.fetchall()
        return self.deserialize(field_content, 'field')

    @work_with_connection
    def store_new_engineer_to_db(self, engineer_dict):
        content = self.serialize(engineer_dict)
        conn = self.conn
        cur = self.cur
        try:
            cur.execute(f''' insert into {self.table}(N,P,EM,PHT)
                            values(?,?,?,?)''', content)
            conn.commit()
        except IntegrityError:
            return 'This engineer is already in db'

        print(f'Engineer with id {cur.lastrowid} was added to DB')

    def deserialize(self, content, content_type):
        if content_type == 'column':
            # only works if ID from 0 to 9
            return [field[0] for field in content]
        elif content_type == 'fields':
            return [field for field in content[0]]
        elif content_type == 'field':
            return content[0][0]

    def serialize(self, content):
        db_list = [field for field in content.values()]
        return (db_list[0][1], db_list[1][1], db_list[2][1], db_list[3][1])
