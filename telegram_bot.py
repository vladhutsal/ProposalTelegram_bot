#!/usr/bin/env python3

import telegram
import logging
import tempfile

from credentials import token
from tests.test_pdf import create_lorem_dict
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
CHOOSE_TITLE_TO_EDIT, EDIT_TITLE, ADD_ENGINEER, CHOOSE_ENGINEER, ADD_INFO, ADD_ENGINEER_TO_PROPOSAL, ADD_NEW_ENGINEER, INIT_TEMP= map(chr, range(8, 16))

templates = {
    CREATE_PROPOSAL: proposal.get_template_dict('content_dict'),
    ADD_INFO: proposal.get_template_dict('info_dict'),
    ADD_NEW_ENGINEER: proposal.get_template_dict('new_engineer_dict')
}


def start(update, context):
    # reset content dict when restarting proposal
    context.user_data['chat_id'] = update.message.chat_id

    buttons = [[
        InlineKeyboardButton(text='Create new proposal',
                             callback_data=f'{ADD_NEW_ENGINEER}, {INIT_TEMP}'),
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


def edit_title(update, context):
    query = update.callback_query
    proposal.current_title_id = detach_id_from_callback(query)
    proposal.edit_all = False
    return show_title(update, context)


# ================ FILL TEMPLATES WITH DATA
def next_title(update, context):
    try:
        proposal.current_title_id = proposal.get_next_title_id()
        return show_title(update, context)
    except StopIteration:
        if proposal.current_template == ADD_NEW_ENGINEER:
            db_handler.save_new_engineer_to_db(proposal.current_dict)
        return overview(update, context)


def show_title(update, context):
    title_id = proposal.current_title_id
    title_name = proposal.get_bold_title(title_id)
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text=title_name,
                             parse_mode=telegram.ParseMode.HTML)
    return STORE_DATA


def store_data(update, context):
    user_text = update.message.text
    proposal.store_content(user_text)

    if proposal.edit_all:
        return next_title(update, context)
    elif not proposal.edit_all:
        proposal.edit_all = True
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

# show buttons for all titles of current dictionary
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


# ================ ENGINEERS
def choose_engineers(update, context):
    query = update.callback_query
    engineers = db_handler.get_all_engineers_id()
    print('ENGINEERS ID LIST:::', engineers)

    buttons = []
    if engineers:
        for engineer_id in engineers:
            engineer_name = db_handler.get_engineer_info(engineer_id, 'name')
            print('ENGINEER NAME', engineer_name)
            if engineer_id not in proposal.engineers_in_proposal:
                buttons = add_button(engineer_name,
                                     f'{engineer_id}, {ADD_ENGINEER_TO_PROPOSAL}',
                                     buttons)

    buttons = add_button('Continue', CREATE_PDF, buttons)
    buttons = add_button('Add new engineer',
                         f'{ADD_NEW_ENGINEER}, {INIT_TEMP}',
                         buttons)

    keyboard = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='Choose engineers: ',
                            reply_markup=keyboard)
    query.answer()

    return SELECT_ACTION


def add_engineer_to_proposal(update, context):
    query = update.callback_query
    proposal.engineers_in_proposal += detach_id_from_callback(query.data)

    query.answer()
    return choose_engineers(update, context)


# ================ HELPERS
def detach_id_from_callback(query_data):
    return query_data.split(',')[0]


def add_button(text, callback, buttons):
    btn = [InlineKeyboardButton(text=text,
                                callback_data=callback)]
    buttons.append(btn)
    return buttons


# ================ HTML TO PDF
def html_to_pdf(update, context):
    colored_titles_dict = proposal.get_colored_titles()
    env = Environment(loader=FileSystemLoader('static/'))
    template = env.get_template('index.html')
    jinja_rendered_html = template.render(titles=colored_titles_dict)

    tmp_html_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
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


def get_test_pdf_dict(update, context):
    proposal.content_dict = create_lorem_dict(proposal.content_dict)
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
                            pattern='^' + str(TEST) + '$'),

                            CallbackQueryHandler(html_to_pdf,
                            pattern='^' + str(CREATE_PDF) + '$'),

                            CallbackQueryHandler(choose_title_to_edit,
                            pattern='^' + str(CHOOSE_TITLE_TO_EDIT) + '$'),

                            CallbackQueryHandler(overview,
                            pattern='^' + str(OVERVIEW) + '$')],

            STORE_DATA: [MessageHandler(Filters.text, store_data)],
        },

        fallbacks=[CommandHandler('end', end)],

        allow_reentry=True
     )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
