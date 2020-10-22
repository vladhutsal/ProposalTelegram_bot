import ctrl_db
import templates


class Proposal:

    def __init__(self):
        self.stages = None

        self.current_template = None
        self.current_dict = None
        self.current_title_id = None

        self.dict_id_iterator = None

        self.edit_all = True

        self.engineers_in_proposal = []

        self.colored_titles_dict = None

        self.template = templates

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

    def save_new_engineer_to_db(self):
        new_engineer_dict = self.current_dict
        db_list = [field for field in new_engineer_dict.values()]
        db_tuple = [db_list[0][1], db_list[1][1], db_list[2][1], db_list[3][1]]
        new_eng_id = ctrl_db.add_new_engineer(db_tuple)
        
        eng = ctrl_db.get_engineer(new_eng_id)
        print(eng)

    def get_template_dict(self, template_name):
        return getattr(templates, template_name)
    
