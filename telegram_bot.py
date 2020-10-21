#!/usr/bin/env python3

import telegram
import logging
import tempfile

from credentials import token
from tests.test_pdf import create_lorem_dict
from Proposal import Proposal

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler)

logging.getLogger('apscheduler.scheduler').propagate = False
proposal = Proposal()

STORE_DATA, SELECT_ACTION = map(chr, range(2))
CREATE_PROPOSAL, TEST, CREATE_PDF, OVERVIEW = map(chr, range(3, 7))
CHOOSE_TITLE_TO_EDIT, EDIT_TITLE, ADD_ENGINEER, CHOOSE_ENGINEER, ADD_INFO, ADD_ENGINEER_TO_PROPOSAL = map(chr, range(8, 14))

stages = {
    CREATE_PROPOSAL: proposal.content_dict,
    ADD_INFO: proposal.info_dict,
    ADD_ENGINEER: proposal.new_engineer_dict
}


def start(update, context):
    # reset content dict when restarting proposal
    context.user_data['chat_id'] = update.message.chat_id

    buttons = [[
        InlineKeyboardButton(text='Create new proposal',
                             callback_data=str(CREATE_PROPOSAL)),
        InlineKeyboardButton(text='Test',
                             callback_data=str(TEST))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Hi, I`ll help you to complete the proposal.')
    update.message.reply_text(text='What do you want to do?',
                              reply_markup=keyboard)

    return SELECT_ACTION


def query_handler(update, context):
    update.callback_query.answer()
    query = update.callback_query

    if EDIT_TITLE in query.data:
        query = update.callback_query
        proposal.current_title_id = query.data.split(',')[0]
        proposal.edit_all = False
        return show_title(update, context)

    proposal.current_dict = stages[query.data]
    context.user_data['stage'] = query.data
    proposal.reset_iter()

    if ADD_INFO in query.data:
        context.user_data['stage'] = CHOOSE_ENGINEER

    return next_title(update, context)


def next_title(update, context):
    try:
        proposal.current_title_id = proposal.get_next_title_id()
        return show_title(update, context)
    except StopIteration:
        return overview(update, context)


def show_title(update, context):
    title_id = proposal.current_title_id
    title_name = proposal.get_bold_title(title_id)
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text=title_name)
    return STORE_DATA


def store_data(update, context):
    user_text = update.message.text
    proposal.store_content(user_text)

    if proposal.edit_all:
        return next_title(update, context)
    elif not proposal.edit_all:
        proposal.edit_all = True
        return overview(update, context)


def overview(update, context):
    c_id = context.user_data['chat_id']
    context.bot.send_message(chat_id=c_id, text='Your titles are:')
    for title_id in proposal.current_dict.keys():
        title_name = proposal.get_bold_title(title_id)
        context.bot.send_message(chat_id=c_id, text=title_name,
                                 parse_mode=telegram.ParseMode.HTML)

    if context.user_data['stage'] == CHOOSE_ENGINEER:
        text = 'Choose engineers'
        callback_data = CHOOSE_ENGINEER
    else:
        text = 'Continue'
        callback_data = ADD_INFO

    buttons = [[
        InlineKeyboardButton(text=text, callback_data=callback_data),
        InlineKeyboardButton(text='Edit', callback_data=str(CHOOSE_TITLE_TO_EDIT))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    context.bot.send_message(chat_id=c_id, text='All good?',
                             reply_markup=keyboard)
    return SELECT_ACTION


def choose_title_to_edit(update, context):
    query = update.callback_query
    current_dict = proposal.current_dict

# show buttons for all titles of current dictionary
    buttons = []
    for title_id in proposal.current_dict.keys():
        btn = [InlineKeyboardButton(text=f'{current_dict[title_id][0]}',
                                    callback_data=f'{title_id}, {str(EDIT_TITLE)}')]
        buttons.append(btn)

    back_btn = [InlineKeyboardButton(text='<< GO BACK',
                                     callback_data=str(OVERVIEW))]
    buttons.append(back_btn)
    keyboard = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='Choose a title you want to edit:',
                            reply_markup=keyboard)
    query.answer()

    return SELECT_ACTION


def choose_engineers(update, context):
    query = update.callback_query
    engineers = proposal.get_engineers_dict()
    buttons = []
    for engineer in engineers.keys():
        engineer_id = engineers.get(engineer)['id']
        if str(engineer_id) not in proposal.engineers_in_proposal:
            print('ENGINEER ID: ', engineer_id)
            btn = [InlineKeyboardButton(text=engineer,
                                        callback_data=f'{engineer_id}, {str(ADD_ENGINEER_TO_PROPOSAL)}')]
            buttons.append(btn)
    back_btn = [InlineKeyboardButton(text='Continue',
                                    callback_data=str(CREATE_PDF))]
    buttons.append(back_btn)

    keyboard = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='Choose engineers: ',
                            reply_markup=keyboard)
    query.answer()

    return SELECT_ACTION


def add_engineer_to_proposal(update, context):
    query = update.callback_query
    proposal.engineers_in_proposal += query.data.split(',')[0]
    print('ENGINEER IN PROPOSAL NOW: ', proposal.engineers_in_proposal)

    query.answer()
    return choose_engineers(update, context)


def html_to_pdf(update, context):
    proposal.get_colored_titles()
    env = Environment(loader=FileSystemLoader('static/'))
    template = env.get_template('index.html')
    jinja_rendered_html = template.render(titles=proposal.colored_titles_dict)

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
            SELECT_ACTION: [CallbackQueryHandler(query_handler,
                            pattern='^' + str(CREATE_PROPOSAL) + '$'),

                            CallbackQueryHandler(query_handler,
                            pattern=f'.+{EDIT_TITLE}$'),

                            CallbackQueryHandler(query_handler,
                            pattern='^' + str(ADD_ENGINEER) + '$'),

                            CallbackQueryHandler(query_handler,
                            pattern='^' + str(ADD_INFO) + '$'),


                            CallbackQueryHandler(choose_engineers,
                            pattern='^' + str(CHOOSE_ENGINEER) + '$'),

                            CallbackQueryHandler(add_engineer_to_proposal,
                            pattern=f'.+{ADD_ENGINEER_TO_PROPOSAL}$'),


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
