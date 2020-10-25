#!/usr/bin/env python3

import telegram
import logging
import tempfile

from credentials import token
from test_pdf import create_lorem_dict
from Proposal import Proposal
from ProposalDBHandler import ProposalDBHandler

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler)

logging.getLogger('apscheduler.scheduler').propagate = False
proposal = Proposal()
db_handler = ProposalDBHandler('proposal.db')

# add query constats, eg CREATE_PROPOSAL ADD_ENGINEER CHOOSE_ENGINEER ADD_INFO ADD_ENGINEER_TO_PROPOSAL
STORE_DATA, SELECT_ACTION = map(chr, range(2))
CREATE_PROPOSAL, TEST, CREATE_PDF, OVERVIEW = map(chr, range(3, 7))
CHOOSE_TITLE_TO_EDIT, EDIT_TITLE, ADD_ENGINEER, CHOOSE_ENGINEER, ADD_INFO, ADD_ENGINEER_TO_PROPOSAL, ADD_NEW_ENGINEER, INIT_TEMP, STORE_PHOTO, ADD_ENGINEERS_RATE= map(chr, range(8, 18))

templates = {
    CREATE_PROPOSAL:    proposal.content_template,
    ADD_INFO:           proposal.info_template,
    ADD_NEW_ENGINEER:   proposal.engineer_template,
    ADD_ENGINEERS_RATE: db_handler.engineers_rates
}


def start(update, context):

    # reset content dict when restarting proposal
    context.user_data['chat_id'] = update.message.chat_id

    buttons = [[
        InlineKeyboardButton(text='Create new proposal',
                             callback_data=f'{CREATE_PROPOSAL}, {INIT_TEMP}'),
        InlineKeyboardButton(text='Test',
                             callback_data=str(TEST))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Hi, I`ll help you to complete the proposal.')
    update.message.reply_text(text='What do you want to do?',
                              reply_markup=keyboard)

    return SELECT_ACTION


def initialize_template(update, context):
    query = update.callback_query

    template = detach_id_from_callback(query.data)
    proposal.current_template = template
    proposal.current_dict = templates[template]
    proposal.reset_iter()
    query.answer()

    return next_title(update, context)


# use callback query answer to show notification on top of the bots chat
def show_error_message(update, context):
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text='This engineer is already in db')


# ================ FILL TEMPLATES WITH DATA
def next_title(update, context):
    try:
        proposal.current_title_id = proposal.get_next_title_id()
        return show_title(update, context)
    except StopIteration:
        if proposal.current_template == ADD_NEW_ENGINEER:

            # telegram_bot.py is no need to know about db_handler class
            err = db_handler.store_new_engineer_to_db(proposal.current_dict)
            proposal.reset_engineer_template()
            if err:
                show_error_message(update, context)

        return overview(update, context)


def show_title(update, context):
    title_id = proposal.current_title_id
    title_name = proposal.get_bold_title(title_id)
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text=title_name,
                             parse_mode=telegram.ParseMode.HTML)
    return STORE_DATA


def store_photo(update, context):
    photo_info = update.message.photo[-1]
    file_id = photo_info.file_id
    File_obj = context.bot.get_file(file_id=file_id)

    dir_path = 'engineers_photo/'
    name = proposal.get_random_name()
    photo_path = f'{dir_path}{name}.jpg'
    save_path = f'"../{dir_path}{name}.jpg"'
    File_obj.download(custom_path=photo_path)
    proposal.store_content(save_path)

    return next_title(update, context)


def store_data(update, context):
    user_content = update.message.text
    proposal.store_content(user_content)

    if proposal.edit_all:
        return next_title(update, context)

    elif not proposal.edit_all:
        proposal.edit_all = True
        if proposal.add_rate:
            proposal.add_rate = False
            return choose_engineers(update, context)

        return overview(update, context)


# ================ EDIT AND OVERVIEW
def overview(update, context):
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text='Info you`ve provided:')
    for title_id in proposal.current_dict.keys():
        title = proposal.get_bold_title(title_id)
        content = proposal.get_title_content(title_id)
        context.bot.send_message(chat_id=context.user_data['chat_id'],
                                 text=f'{title}\n{content}',
                                 parse_mode=telegram.ParseMode.HTML)

    if proposal.current_template == CREATE_PROPOSAL:
        text = 'Add info'
        callback_data = f'{ADD_INFO}, {INIT_TEMP}'
    else:
        text = 'Choose engineers'
        callback_data = CHOOSE_ENGINEER

    buttons = [[
        InlineKeyboardButton(text=text,
                             callback_data=callback_data),
        InlineKeyboardButton(text='Edit',
                             callback_data=str(CHOOSE_TITLE_TO_EDIT))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text='All good?',
                             reply_markup=keyboard)
    return SELECT_ACTION


def choose_title_to_edit(update, context):
    query = update.callback_query
    current_dict = proposal.current_dict

    buttons = []
    for title_id in proposal.current_dict.keys():
        btn = [InlineKeyboardButton(text=f'{current_dict[title_id][0]}',
                                    callback_data=f'{title_id}, {EDIT_TITLE}')]
        buttons.append(btn)

    buttons = add_button('<< Go back', OVERVIEW, buttons)

    keyboard = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='Choose a title you want to edit:',
                            reply_markup=keyboard)
    query.answer()

    return SELECT_ACTION


def edit_title(update, context):
    query = update.callback_query
    proposal.current_title_id = detach_id_from_callback(query.data)

    if ADD_ENGINEERS_RATE in query.data:
        add_engineer_to_proposal()
        proposal.current_dict = db_handler.engineers_rates
        print('EDIT TITLE', db_handler.engineers_rates)
    proposal.edit_all = False

    return show_title(update, context)


# ================ ENGINEERS
def choose_engineers(update, context):
    query = update.callback_query
    engineers = db_handler.get_all_engineers_id()

    buttons = []
    if engineers:
        for engineer_id in engineers:
            engineer_name = db_handler.get_field_info(engineer_id, 'N')
            if engineer_id not in db_handler.engineers_in_proposal_id:
                buttons = add_button(engineer_name,
                                     f'{engineer_id}, {ADD_ENGINEERS_RATE}, {EDIT_TITLE}',
                                     buttons)

    help_btns = [
        InlineKeyboardButton(text='Add new engineer',
                             callback_data=f'{ADD_NEW_ENGINEER}, {INIT_TEMP}'),
        InlineKeyboardButton(text='Continue',
                             callback_data=CREATE_PDF)
    ]
    buttons.append(help_btns)

    keyboard = InlineKeyboardMarkup(buttons)
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text='Choose engineers: ',
                             reply_markup=keyboard)
    if query:
        query.answer()

    return SELECT_ACTION


def add_engineer_to_proposal():
    # add engineers id to list of engineers in current proposal:
    engineer_id = proposal.current_title_id
    curr_list = db_handler.engineers_in_proposal_id
    curr_list.append(int(engineer_id))

    # add engineers id to dictionary as key {'engn_id': ['name', 'rate']}
    engineer_name = db_handler.get_field_info(engineer_id, 'N')
    db_handler.engineers_rates[engineer_id] = [f'Current rate for {engineer_name}', '']
    print(db_handler.engineers_rates)
    proposal.add_rate = True


# ================ HELPERS
def detach_id_from_callback(query_data):
    additional_query_data = query_data.split(',')[0]
    return additional_query_data


def add_button(text, callback, buttons):
    btn = [InlineKeyboardButton(text=text,
                                callback_data=callback)]
    buttons.append(btn)
    return buttons


# ================ HTML TO PDF
def html_to_pdf(update, context):
    content_dict = proposal.content_template
    info_dict = proposal.info_template

    #to make both test and regular modes work
    if proposal.engineers:
        engineers = proposal.engineers
    
    engineers = db_handler.get_all_engineers_in_proposal()

    colored_titles_dict = proposal.get_colored_titles(content_dict)
    env = Environment(loader=FileSystemLoader('static/'))
    template = env.get_template('index.html')
    jinja_rendered_html = template.render(content_dict=colored_titles_dict,
                                          info_dict=info_dict,
                                          engineers_list_of_dicts=engineers)

    tmp_html_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
    print(tmp_html_file.name)
    tmp_pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)

    with open(tmp_html_file.name, 'w+') as html:
        html.write(jinja_rendered_html)

    pdf_doc = HTML(tmp_html_file.name)
    pdf_doc_rndr = pdf_doc.render(stylesheets=['static/main.css'])
    page = pdf_doc_rndr.pages[0]
    child_list = []
    for child in page._page_box.descendants():
        child_list.append(child)
    body_height = child_list[2].height
    page.height = body_height

    pdf_doc_rndr.write_pdf(tmp_pdf_file.name)

    context.user_data['tmpfile'] = tmp_pdf_file
    update.callback_query.answer()

    return send_pdf(context, update)


def send_pdf(context, update):
    c_id = context.user_data['chat_id']
    pdf = context.user_data['tmpfile']

    with open(pdf.name, 'rb') as pdf:
        context.bot.send_document(chat_id=c_id, document=pdf)

    return ConversationHandler.END


# ================ GENERATE TEST PDF
def get_test_pdf_dict(update, context):
    content_template, info_template, engineers = create_lorem_dict(db_handler, proposal)
    proposal.engineers = engineers
    proposal.content_template = content_template
    proposal.info_template = info_template
    update.callback_query.answer()

    return html_to_pdf(update, context)


def end():
    pass


def main():
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_ACTION: [CallbackQueryHandler(initialize_template,
                            pattern=f'.+{INIT_TEMP}$'),


                            CallbackQueryHandler(choose_engineers,
                            pattern='^' + str(CHOOSE_ENGINEER) + '$'),

                            CallbackQueryHandler(add_engineer_to_proposal,
                            pattern=f'.+{ADD_ENGINEER_TO_PROPOSAL}$'),


                            CallbackQueryHandler(edit_title,
                            pattern=f'.+{EDIT_TITLE}$'),

                            CallbackQueryHandler(get_test_pdf_dict,
                            pattern=TEST),

                            CallbackQueryHandler(html_to_pdf,
                            pattern='^' + str(CREATE_PDF) + '$'),

                            CallbackQueryHandler(choose_title_to_edit,
                            pattern='^' + str(CHOOSE_TITLE_TO_EDIT) + '$'),

                            CallbackQueryHandler(overview,
                            pattern='^' + str(OVERVIEW) + '$')],

            STORE_DATA: [MessageHandler(Filters.text, store_data),
                         MessageHandler(Filters.photo, store_photo)]
        },

        fallbacks=[CommandHandler('end', end)],

        allow_reentry=True
     )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
