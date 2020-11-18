from copy import deepcopy

content_template = {
    # '<title-id>_<html-position>': ['<title>', '<content>']
    'MCG': ['Main current Goal', ''],
    'CE_list': ['Client Expectations', ''],
    'NPS_list': ['Next potential Steps', ''],
    'TOPS': ['Type of provided Services', ''],
    'TOR_line': ['Type of Reports', ''],
    'EHPW_line': ['Expected hours per Week', ''],
    'VA_list': ['Value Added', '']
}

# set date automaticaly
info_template = {
    'PB': ['Prepared by', ''],
    'CD': ['Creation date', ''],
    'DL': ['Deadlines', ''],
    'CN': ['Client`s company name', '']
}

engineer_template = {
    'N': ['Name', ''],
    'P': ['Position', ''],
    'EM': ['Email', ''],
    'PHT': ['Photo', '']
}

templates = {
    'content': content_template,
    'info': info_template,
    'engineer': engineer_template
}


def get_template(template_name):
    for template in templates.keys():
        if template == template_name:
            return deepcopy(templates[template])
