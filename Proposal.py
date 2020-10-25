from templates import (
    content_template,
    info_template,
    engineer_template
)
import random
import os
from copy import deepcopy


class Proposal:
    def __init__(self):
        self.content_template = deepcopy(content_template)
        self.info_template = deepcopy(info_template)
        self.engineer_template = deepcopy(engineer_template)

        self.dict_id_iterator = None

        self.current_template = None
        self.current_dict = None
        self.current_title_id = None

        self.edit_all = True
        self.add_rate = False
        self.engineers = None

    def reset_iter(self):
        if self.dict_id_iterator:
            self.dict_id_iterator = None

        self.dict_id_iterator = iter(self.current_dict.keys())

    def reset_engineer_template(self):
        self.engineer_template = deepcopy(engineer_template)

    def get_next_title_id(self):
        try:
            return next(self.dict_id_iterator)
        except StopIteration as end:
            raise end

    def store_content(self, content):
        self.current_dict[self.current_title_id][1] = content

    def get_random_name(self):
        tmp_files_list = os.listdir('engineers_photo/')
        rand_nm = random.randint(12, 999999)
        exists = [fn for fn in tmp_files_list if str(rand_nm) in fn]
        if exists:
            self.get_random_name()
        return rand_nm

    def get_bold_title(self, title_id):
        title_name = self.current_dict[title_id][0]
        return f'<b>{title_name}</b>'

    def get_title_content(self, title_id):
        return self.current_dict[title_id][1]

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
