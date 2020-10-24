from lorem_text import lorem
from random import randint


def create_lorem_dict(db_handler, proposal):
    db_handler.table = 'test'
    db_handler.create_table(name='test')

    cntnt_tmplt = proposal.content_template
    info_tmplt = proposal.info_template
    db_handler.engineers_in_proposal_id = [1, 2]
    print(db_handler.engineers_in_proposal_id)

    puppet = {
        'N': ['Name', 'Puppet Vasya'],
        'P': ['Position', 'QA engineer'],
        'EM': ['Email', 'vasya.puppet@u-tor.com'],
        'PHT': ['Photo', 'engineers_photo/111.jpg']
    }

    puppet2 = {
        'N': ['Name', 'Puppet Petya'],
        'P': ['Position', 'Team lead'],
        'EM': ['Email', 'petya.puppet@u-tor.com'],
        'PHT': ['Photo', 'engineers_photo/222.jpg']
    }
    engineers = [puppet, puppet2]
    for engineer in engineers:
        db_handler.store_new_engineer_to_db(engineer)

    for title_id in cntnt_tmplt.keys():
        if '_list' in title_id:
            for x in range(randint(1, 4)):
                cntnt_tmplt[title_id][1] += f'{lorem.sentence()}\n'
        else:
            cntnt_tmplt[title_id][1] = lorem.sentence()

    for title_id in info_tmplt.keys():
        info_tmplt[title_id][1] = lorem.words(randint(2, 5))

    engineers = db_handler.get_all_engineers_in_proposal()

    db_handler.table = 'proposal'
    return cntnt_tmplt, info_tmplt, engineers
