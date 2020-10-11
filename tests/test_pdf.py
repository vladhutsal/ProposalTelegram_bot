from lorem_text import lorem


def create_lorem_dict(user_dict):
    lorem_snt = lorem.words(13)
    lorem_snt = lorem_snt.title()
    lorem_list = ''
    for x in range(4, 8):
        lorem_list += f'{lorem.words(x)}\n'.title()
    lorem_list = lorem_list.rstrip()

    for code in user_dict.keys():
        if '_list' in code:
            user_dict[code][1] = lorem_list
        else:
            user_dict[code][1] = lorem_snt

    return user_dict
