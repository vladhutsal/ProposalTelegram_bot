from . templates import (
    content_template,
    info_template,
    engineer_template
)
from . test_pdf import create_lorem_dict
from copy import deepcopy
import random
import os


class Proposal:
    # current_dict = template data, dictionary like
    # {'title_id':['title_name', 'title_content']}

    def __init__(self, db_handler):
        self.db_handler = db_handler

        self.content_dict = deepcopy(content_template)
        self.info_dict = deepcopy(info_template)
        self.engineer_dict = deepcopy(engineer_template)

        self.html = None
        self.pdf = None

        self.dict_id_iterator = None

        self.current_dict = None
        self.current_title_id = None
        
        self.edit_all = True
        self.test = False
        self.finish = False

    def reset_iter(self):
        if self.dict_id_iterator:
            self.dict_id_iterator = None

        self.dict_id_iterator = iter(self.current_dict.keys())

    def reset_engineer_dict(self):
        self.engineer_dict = deepcopy(engineer_template)

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

    def get_colored_titles(self, user_dict):
        # use here a function to iterate through dictionaries,
        # like in get_all_engineers func
        colored_titles_dict = deepcopy(user_dict)
        for title_id in colored_titles_dict.keys():
            title = colored_titles_dict[title_id][0]
            title_white = ' '.join(title.split(' ')[0:-1])
            title_blue = title.split(' ')[-1]
            colored_titles_dict[title_id][0] = [f'{title_white} ', title_blue]
        return colored_titles_dict

    # let it loop
    def collect_user_data_for_html(self):
        if self.test:
            data = create_lorem_dict(self)
        else:
            data = {
                'content_dict': self.get_colored_titles(self.content_dict),
                'info_dict': self.info_dict,
                'engineers_list': self.db_handler.get_proposal_engineers()
            }

        return data
