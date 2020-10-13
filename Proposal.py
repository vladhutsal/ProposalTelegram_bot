
class Proposal:

    def __init__(self):
        self.hdr_dict = {
                    'MCG': ['Main current Goal', ''],
                    'CE_list': ['Client Expectations', ''],
                    'NPS_list': ['Next potential Steps', ''],
                    'TOPS': ['Type of provided Services', ''],
                    'RT_line': ['Report Types', ''],
                    'EHPW_line': ['Expected hours per Week', ''],
                    'VA_list': ['Value Added', '']}

        self.info_dict = {
                    'Pb': '',   # Prepared by
                    'CD': '',   # Creation date
                    'DL': ''}   # Deadlines
        
        self.engineer_dict = {
                    'N': '',    # Name
                    'P': '',    # Position
                    'RT': '',   # Rate
                    'EM': '',   # Email
                    'PHT': ''   # Photo
        }

        self.headers_id = self.hdr_dict.keys()
        self.go_through = None
        self.edit_all = True
        self.current_hdr = None

    def get_next_header(self):
        try:
            return next(self.go_through)
        except StopIteration as end:
            raise end
    
    def reset_iter(self):
        self.go_through = None
        self.go_through = (hdr for hdr in self.headers_id)

    def get_hdr_name(self, ):
        return self.hdr_dict[self.current_hdr][0]

    def store_text(self, text):
        self.hdr_dict[self.current_hdr][1] = text

# do it in a better way
    def hdr_overview(self, header):
        header_name = self.hdr_dict[header][0]
        header_content = self.hdr_dict[header][1]
        return f'<b>{header_name}</b>\n{header_content}'

    def get_colored_titles(self):
        for hdr_id in self.headers_id:
            title = self.hdr_dict[hdr_id][0]

            title_white = title.split(' ')[0:-1]
            title_blue = title.split(' ')[-1]
            title_white = ' '.join(title_white)
            self.hdr_dict[hdr_id][0] = [title_white, f' {title_blue}']
