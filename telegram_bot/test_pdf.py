from lorem_text import lorem
from random import randint
from . templates import get_template


def create_lorem_dict(proposal):

    proposal.content_dict = get_template('content')
    proposal.info_template = get_template('info')

    content_template = proposal.content_dict
    info_template = proposal.info_template

    puppet = {
        'N': ['Name', 'Puppet Vasya'],
        'P': ['Position', 'QA engineer'],
        'RT': ['Rate', '85'],
        'EM': ['Email', 'vasya.puppet@u-tor.com'],
        'PHT': ['Photo', '../engineers_photo/111.jpg']
    }

    puppet2 = {
        'N': ['Name', 'Puppet Petya'],
        'P': ['Position', 'Team lead'],
        'RT': ['Rate', '45'],
        'EM': ['Email', 'petya.puppet@u-tor.com'],
        'PHT': ['Photo', '../engineers_photo/222.jpg']
    }

    puppet3 = {
        'N': ['Name', 'Puppet Anton'],
        'P': ['Position', 'Project manager'],
        'RT': ['Rate', '12'],
        'EM': ['Email', 'anton.puppet@u-tor.com'],
        'PHT': ['Photo', '../engineers_photo/333.jpg']
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
    info_template['DL'][1] = 'November 2, 2020'
    info_template['CD'][1] = 'November 29, 2020'
    info_template['PB'][1] = 'Alex'

    proposal.content_dict = content_template
    proposal.info_dict = info_template
    print('CONTENT DICT BEFORE COLLORING :', proposal.content_dict)
    return {
        'content_dict': proposal.get_colored_titles(),
        'info_dict': info_template,
        'engineers_list': puppet_engineers
    }
