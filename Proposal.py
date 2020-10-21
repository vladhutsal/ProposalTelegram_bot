class Proposal:

    def __init__(self):
        self.content_dict = {
            # '<title-id>_<html-position>': ['<title>', '<content>']
            'MCG': ['Main current Goal', ''],
            'CE_list': ['Client Expectations', ''],
            'NPS_list': ['Next potential Steps', ''],
            'TOPS': ['Type of provided Services', ''],
            'RT_line': ['Report Types', ''],
            'EHPW_line': ['Expected hours per Week', ''],
            'VA_list': ['Value Added', '']
        }

        self.info_dict = {
            'PB': ['Prepared by', ''],
            'CD': ['Creation date', ''],
            'DL': ['Deadlines', '']
        }

        self.new_engineer_dict = {
            'N': ['Name', ''],
            'P': ['Position', ''],
            'EM': ['Email', ''],
            'PHT': ['Photo', '']
        }

        self.engineers_dict = {
            'Vlados': {
                'id': 1,
                'N': ['Name', 'Vlados'],
                'P': ['Position', 'Software engineer'],
                'EM': ['Email', 'tdge@gmail.com'],
                'PHT': ['Photo', 'static/photo.jpg']
            },
            'Kekoz': {
                'id': 2,
                'N': ['Name', 'Kekoz'],
                'P': ['Position', 'Intern'],
                'EM': ['Email', 'tdge@gmail.com'],
                'PHT': ['Photo', 'static/photo.jpg']
            }
        }

        self.stages = None

        self.current_dict = None
        self.current_title_id = None

        self.dict_id_iterator = None

        self.edit_all = True

        self.engineers_in_proposal = []

        self.colored_titles_dict = None

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
        self.colored_titles_dict = self.content_dict.copy()
        for title_id in self.colored_titles_dict.keys():
            title = self.colored_titles_dict[title_id][0]

            title_white = title.split(' ')[0:-1]
            title_blue = title.split(' ')[-1]
            title_white = ' '.join(title_white)
            self.colored_titles_dict[title_id][0] = [f'{title_white} ', title_blue]
            print(self.colored_titles_dict[title_id][0])

    def get_engineers_dict(self):
        return self.engineers_dict
