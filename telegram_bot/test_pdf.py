from lorem_text import lorem
from random import randint
from . templates import (
    content_template,
    info_template
)


def create_lorem_dict(db_handler, proposal):
    db_handler.table = 'test'
    db_handler.create_table(name='test')

    db_handler.engineers_in_proposal_id = [1, 2]

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
    for engineer in puppet_engineers:
        db_handler.store_new_engineer_to_db(engineer)

    for title_id in content_template.keys():
        if '_list' in title_id:
            for x in range(randint(1, 4)):
                content_template[title_id][1] += f'{lorem.sentence()}\n'
        else:
            content_template[title_id][1] = lorem.sentence()
    print(content_template)

    for title_id in info_template.keys():
        info_template[title_id][1] = lorem.words(randint(2, 5))

    db_handler.table = 'engineers'
    return {
        'content_dict': proposal.get_colored_titles(content_template),
        'info_dict': info_template,
        'engineers_list': puppet_engineers
    }
