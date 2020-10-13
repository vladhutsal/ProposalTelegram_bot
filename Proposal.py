
class Proposal:

    def __init__(self):
        self.hdr_dict = {
                    'MCG': ['Main current goal', ''],
                    'CE_list': ['Client Expectations', ''],
                    'NPS_list': ['Next potential steps', ''],
                    'TOPS': ['Type of provided services', ''],
                    'RT_line': ['Report types', ''],
                    'EHPW_line': ['Expected hours per week', ''],
                    'VA_list': ['Value-added', '']}

        self.headers_id = self.hdr_dict.keys()
        self.go_through = (hdr for hdr in self.headers_id)
        self.edit_all = True
        self.current_hdr = None

    def eidt_content(self, hdr_code, content):
        self.hdr_dict[hdr_code][1] = content

    def get_next_header(self):
        try:
            return next(self.go_through)
        except StopIteration as end:
            raise end

    def get_hdr_name(self, ):
        return self.hdr_dict[self.current_hdr][0]

    def store_text(self, text):
        self.hdr_dict[self.current_hdr][1] = text

# do it better
    def hdr_overview(self, header):
        header_name = self.hdr_dict[header][0]
        header_content = self.hdr_dict[header][1]
        return f'<b>{header_name}</b>\n{header_content}'
