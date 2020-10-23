import templates


class Proposal:
    def __init__(self):
        self.engineers_in_proposal = []

        self.current_template = None
        self.current_dict = None
        self.current_title_id = None

        self.dict_id_iterator = None

        self.edit_all = True

    def reset_iter(self):
        if self.dict_id_iterator:
            self.dict_id_iterator = None

        self.dict_id_iterator = (title for title in self.current_dict.keys())

    def get_next_title_id(self):
        try:
            return next(self.dict_id_iterator)
        except StopIteration as end:
            raise end

    def get_template_dict(self, template_name):
        return getattr(templates, template_name)

    def store_content(self, content):
        self.current_dict[self.current_title_id][1] = content

    def get_bold_title(self, title_id):
        title_name = self.current_dict[title_id][0]
        return f'<b>{title_name}</b>'

    def get_title_content(self, title_id):
        return self.current_dict[title_id][1]

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
