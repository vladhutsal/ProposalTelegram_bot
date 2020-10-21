import random
import database


class Proposal:

    def __init__(self):
        self.stages = None

        self.current_dict = None
        self.current_title_id = None

        self.dict_id_iterator = None

        self.edit_all = True

        self.engineers_in_proposal = []

        self.colored_titles_dict = None

        self.database = database

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
        self.colored_titles_dict = template.copy()
        for title_id in self.colored_titles_dict.keys():
            title = self.colored_titles_dict[title_id][0]

            title_white = title.split(' ')[0:-1]
            title_blue = title.split(' ')[-1]
            title_white = ' '.join(title_white)
            self.colored_titles_dict[title_id][0] = [f'{title_white} ', title_blue]
            print(self.colored_titles_dict[title_id][0])

    def add_new_engineer(self):
        template = self.get_template_dict('new_engineer_dict')
        engineers_storage = self.get_template_dict('engineers_dict')
        new_engineer = template.copy()
        new_engineer_id = random.randint(12, 30)
        engineers_storage[new_engineer_id] = new_engineer
        return engineers_storage[new_engineer_id]

    def get_template_dict(self, template_name):
        return getattr(database, template_name)
        
