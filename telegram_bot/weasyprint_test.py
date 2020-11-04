#!/usr/bin/env python3

from copy import deepcopy
from random import randint
from weasyprint import HTML
from lorem_text import lorem

from jinja2 import Environment, FileSystemLoader

content_template = {
    # '<title-id>_<html-position>': ['<title>', '<content>']
    'MCG': ['Main current Goal', ''],
    'CE_list': ['Client Expectations', ''],
    'NPS_list': ['Next potential Steps', ''],
    'TOPS': ['Type of provided Services', ''],
    'RT_line': ['Report Types', ''],
    'EHPW_line': ['Expected hours per Week', ''],
    'VA_list': ['Value Added', '']
}

info_template = {
    'PB': ['Prepared by', ''],
    'CD': ['Creation date', ''],
    'DL': ['Deadlines', '']
}

puppet = {
    'N': ['Name', 'Puppet Vasya'],
    'P': ['Position', 'QA engineer'],
    'RT': ['Rate', '85'],
    'EM': ['Email', 'vasya.puppet@u-tor.com'],
    'PHT': ['Photo', 'engineers_photo/vasya.jpg']
}

puppet2 = {
    'N': ['Name', 'Puppet Petya'],
    'P': ['Position', 'Developer'],
    'RT': ['Rate', '45'],
    'EM': ['Email', 'petya.puppet@u-tor.com'],
    'PHT': ['Photo', 'engineers_photo/petya.jpg']
}

puppet3 = {
    'N': ['Name', 'Puppet Georgiy'],
    'P': ['Position', 'Project manager'],
    'RT': ['Rate', '11'],
    'EM': ['Email', 'grisha@u-tor.com'],
    'PHT': ['Photo', './engineers_photo/georgiy.jpg']
}

puppet4 = {
     'N': ['Name', 'Puppet Onur'],
     'P': ['Position', 'Good boy'],
     'RT': ['Rate', '44'],
     'EM': ['Email', 'onur@u-tor.com'],
     'PHT': ['Photo', './engineers_photo/onur.jpg']
 }


def create_lorem_dict():
    puppet_engineers = [puppet]

    # generating lorem text for content dict
    for title_id in content_template.keys():
        if '_list' in title_id:
            for x in range(randint(1, 4)):
                content_template[title_id][1] += f'{lorem.sentence()}\n'
        else:
            content_template[title_id][1] = lorem.sentence()

    # generating lorem text for info dict
    for title_id in info_template.keys():
        info_template[title_id][1] = lorem.words(randint(2, 5))

    content_template['EHPW_line'][1] = '40 hrs/week'
    info_template['DL'][1] = '30.10.2020'
    info_template['CD'][1] = '27.10.2020'
    info_template['PB'][1] = 'Alex'

    return {
        'content_dict': get_colored_titles(content_template),
        'info_dict': info_template,
        'engineers_list': puppet_engineers
    }


def get_colored_titles(user_dict):
    user_dict = deepcopy(user_dict)
    for title_id in user_dict.keys():
        title = user_dict[title_id][0]
        title_white = ' '.join(title.split(' ')[0:-1])
        title_blue = title.split(' ')[-1]
        user_dict[title_id][0] = [f'{title_white} ', title_blue]
    return user_dict


def generate_html():
    collected_data = create_lorem_dict()

    env = Environment(loader=FileSystemLoader('static/'))
    template = env.get_template('index_clear.html')
    jinja_rendered_html = template.render(**collected_data)

    with open('result.html', 'w+') as html:
        html.write(jinja_rendered_html)

    return generate_pdf()


def generate_pdf():
    pdf_doc = HTML('result.html')
    pdf_doc_rndr = pdf_doc.render(stylesheets=['static/main.css'])
    page = pdf_doc_rndr.pages[0]
    child_list = [child for child in page._page_box.descendants()]
    body_height = child_list[2].height
    page.height = body_height
    pdf_doc_rndr.write_pdf('result.pdf')


if __name__ == "__main__":
    generate_html()
