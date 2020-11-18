from datetime import datetime

from . templates import get_template
from . test_pdf import create_lorem_dict

import random
import os


class Proposal:
    # current_dict is the template from templates.py. Dictionary like:
    # {'title_id':['title_name', 'title_content']}

    def __init__(self, db_handler):
        self.db_handler = db_handler

        self.content_dict = get_template('content')
        self.info_dict = get_template('info')
        self.engineer_dict = get_template('engineer')

        self.html = None
        self.pdf = None

        self.dict_id_iterator = None

        self.current_dict = None
        self.current_title_id = None

        self.edit_all = True
        self.test = False
        self.finish = False
        self.info = True
        self.settings = False
        self.manual_mode = True

    def reset_iter(self):
        if self.dict_id_iterator:
            self.dict_id_iterator = None

        self.dict_id_iterator = iter(self.current_dict.keys())

    def reset_dict(self, name):
        setattr(self, f'{name}_dict', get_template(name))

    def store_content(self, content):
        self.current_dict[self.current_title_id][1] = content

    def get_next_title_id(self):
        try:
            self.current_title_id = next(self.dict_id_iterator)
        except StopIteration as end:
            raise end

    def get_bold_title(self, title_id):
        title_name = self.current_dict[title_id][0]
        return f'<b>{title_name}</b>'

    def get_title_content(self, title_id):
        return self.current_dict[title_id][1]

    # generate name for proposal like date and company
    def get_random_name(self):
        tmp_files_list = os.listdir('media/')
        rand_nm = random.randint(12, 999999)
        exists = [fn for fn in tmp_files_list if str(rand_nm) in fn]
        if exists:
            self.get_random_name()
        return rand_nm

    def get_colored_titles(self):
        colored_titles_dict = self.content_dict
        for title_id in colored_titles_dict.keys():
            title = colored_titles_dict[title_id][0]
            *title_white, title_blue = title.split(' ')
            title_white = ' '.join(title_white)
            colored_titles_dict[title_id][0] = [f'{title_white} ', title_blue]
        return colored_titles_dict

    # let it loop
    def collect_user_data_for_html(self):
        if self.test:
            data = create_lorem_dict(self)
        else:
            data = {
                'content_dict': self.get_colored_titles(),
                'info_dict': self.info_dict,
                'engineers_list': self.db_handler.get_proposal_engineers()
            }

        return data

    def add_timestamp(self, text):
        date = datetime.now().strftime('%m_%d_%Y')
        time = datetime.now().strftime('%H%M')
        name = text.replace(' ', '_')
        name += f'_{date}_{time}'
        return name
