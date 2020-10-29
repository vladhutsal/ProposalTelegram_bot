from lorem_text import lorem
from random import randint
from . templates import (
    content_template,
    info_template
)


def create_lorem_dict(proposal):
    puppet = {
        'N': ['Name', 'Puppet Vasya'],
        'P': ['Position', 'QA engineer'],
        'RT': ['Rate', '85'],
        'EM': ['Email', 'vasya.puppet@u-tor.com'],
        'PHT': ['Photo', 'engineers_photo/111.jpg']
    }

    puppet2 = {
        'N': ['Name', 'Puppet Petya'],
        'P': ['Position', 'Team lead'],
        'RT': ['Rate', '45'],
        'EM': ['Email', 'petya.puppet@u-tor.com'],
        'PHT': ['Photo', 'engineers_photo/222.jpg']
    }

    puppet_engineers = [puppet, puppet2]

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
        'content_dict': proposal.get_colored_titles(content_template),
        'info_dict': info_template,
        'engineers_list': puppet_engineers
    }
