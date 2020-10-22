import templates
import sqlite3
from sqlite3 import Error


class Proposal:
    def __init__(self):

        self.current_template = None
        self.current_dict = None
        self.current_title_id = None

        self.dict_id_iterator = None

        self.edit_all = True

        self.engineers_in_proposal = []

    def reset_iter(self):
        if self.dict_id_iterator:
            self.dict_id_iterator = None

        self.dict_id_iterator = (title for title in self.current_dict.keys())

    def get_next_title_id(self):
        try:
            return next(self.dict_id_iterator)
        except StopIteration as end:
            raise end

    def store_content(self, text):
        self.current_dict[self.current_title_id][1] = text

    def get_bold_title(self, title_id):
        title_name = self.current_dict[title_id][0]
        title_content = self.current_dict[title_id][1]
        return f'<b>{title_name}</b>\n{title_content}'

    def get_colored_titles(self):
        template = self.get_template_dict('content_dict')
        colored_titles_dict = template.copy()
        for title_id in colored_titles_dict.keys():
            title = colored_titles_dict[title_id][0]
            title_white = title.split(' ')[0:-1]
            title_blue = title.split(' ')[-1]
            title_white = ' '.join(title_white)
            colored_titles_dict[title_id][0] = [f'{title_white} ', title_blue]
        return colored_titles_dict

    def save_new_engineer_to_db(self):
        new_engineer_dict = self.current_dict
        db_list = [field for field in new_engineer_dict.values()]
        db_tuple = (db_list[0][1], db_list[1][1], db_list[2][1], db_list[3][1])
        new_eng_id = self.db_inst.add_new_engineer(db_tuple)
        print(f'Engineer with id {new_eng_id} was added to DB')

    def get_template_dict(self, template_name):
        return getattr(templates, template_name)


class ProposalDBHandler(Proposal):
    def __init__(self, db_path):
        Proposal.__init__(self)
        self.conn = self.create_connection(db_path)
        self.curr = self.conn.cursor()

        self.all_engineers = self.get_all_engineers_id()

    def create_connection(self, db_path):
        try:
            conn = sqlite3.connect(self.db_path)
            print(f'Connected to {self.db_path}')
        except Error as err:
            print('Failed to connect to database', err)
        return conn

    def create_engineers_table(self):
        conn = self.conn
        table = """ CREATE TABLE IF NOT EXISTS engineers (
                    id integer PRIMARY KEY,
                    name text NOT NULL,
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
        return False

    def engineers_table_exists(db_query_func):
        def check_existance(self, content):
            curr = self.curr
            if not curr.lastrowid:
                self.create_engineers_table()
            return db_query_func(db_query_func)
        return check_existance

    @engineers_table_exists
    def add_new_engineer(self, content):
        conn = self.conn

        with conn:
            curr = conn.cursor()
            curr.execute(''' insert into engineers(name,position,email,photo)
                    values(?,?,?,?)''', content)
            conn.commit()
        return curr.lastrowid

    def get_engineer_info(self, field_name):
        curr = self.curr
        curr.execute(f"select * from engineers where {field_name}=?",
                     (field_name,))
        field_content = curr.fetchall()
        return field_content

    def get_all_engineers_id(self):
        self.curr.execute("select id from engineers")
        self.all_engineers = self.curr.fetchall()


def main():
    pass
    # content = ('Anton', 'QA engineer', 'anton@mail.com', '\x02')
    # add_new_engineer(content)
    # conn = create_connection(database)
    # if create_templates_table(conn):
    #     get_all_engineers(conn)
    # rows = select_template_by_priority(conn, "MCG")
    # print(rows)

