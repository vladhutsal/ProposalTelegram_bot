#!/usr/bin/env python3

import telegram
import logging
import tempfile

from credentials import token
from tests.test_pdf import create_lorem_dict
from Proposal import Proposal

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler
)

logging.getLogger('apscheduler.scheduler').propagate = False

proposal = Proposal()

STORE_DATA, OVERVIEW, SELECT_ACTION = map(chr, range(3))
CREATE_NEW_PROPOSAL, TEST, CREATE_PDF, EDIT_CHOOSE, EDIT_HEADER = map(chr, range(3, 8))


def start(update, context):
    context.user_data['chat_id'] = update.message.chat_id

    buttons = [[
        InlineKeyboardButton(text='Create new proposal',
                             callback_data=str(CREATE_NEW_PROPOSAL)),
        InlineKeyboardButton(text='Test',
                             callback_data=str(TEST))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Hi, I`ll help you to complete the proposal.')
    update.message.reply_text(text='What do you want to do?',
                              reply_markup=keyboard)

    return SELECT_ACTION


# crutch
def query_answer(update, context):
    update.callback_query.answer()

    if proposal.edit_all:
        return fill_all_hdrs(update, context)
    elif not proposal.edit_all:
        return show_header_name(update, context)


def fill_all_hdrs(update, context):
    try:
        proposal.current_hdr = proposal.get_next_header()
    except StopIteration:
        return overview(update, context)

    return show_header_name(update, context)


def edit_header(update, context):
    query = update.callback_query
    proposal.current_hdr = query.data.split(',')[0]
    proposal.edit_all = False

    return query_answer(update, context)


# bad decision to handle one function using objects of different class
def show_header_name(update, context):
    header = proposal.get_hdr_name()
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text=f'Write content for header, named {header}')
    return STORE_DATA


def store_data(update, context):
    user_text = update.message.text
    proposal.store_text(user_text)

    if proposal.edit_all:
        return fill_all_hdrs(update, context)
    elif not proposal.edit_all:
        return overview(update, context)


def edit_choose(update, context):
    hdr_dict = proposal.hdr_dict
    buttons = []
    for hdr_id in proposal.headers_id:
        button = [InlineKeyboardButton(text=f'{hdr_dict[hdr_id][0]}',
                                       callback_data=f'{hdr_id}, {str(EDIT_HEADER)}')]
        buttons.append(button)

    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text='Choose:', reply_markup=keyboard)

    return SELECT_ACTION


def overview(update, context):
    update.message.reply_text('Your headers are:')
    for hdr_id in proposal.headers_id:
        text = proposal.hdr_overview(hdr_id)
        update.message.reply_text(text=text,
                                  parse_mode=telegram.ParseMode.HTML)

    buttons = [[
        InlineKeyboardButton(text='Create PDF', callback_data=str(CREATE_PDF)),
        InlineKeyboardButton(text='Edit', callback_data=str(EDIT_CHOOSE))]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text='All good?', reply_markup=keyboard)

    return SELECT_ACTION


# generate tmp file instead of hardocded one
def html_to_pdf(update, context):
    env = Environment(loader=FileSystemLoader('static/'))
    template = env.get_template('index.html')
    jinja_rendered_html = template.render(headers=proposal.hdr_dict)

    tmp_html_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
    tmp_pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)

    with open(tmp_html_file.name, 'w+') as html:
        html.write(jinja_rendered_html)

    HTML(tmp_html_file.name).write_pdf(tmp_pdf_file.name,
                                       stylesheets=[CSS('static/main.css')])
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
    proposal.hdr_dict = create_lorem_dict(proposal.hdr_dict)
    update.callback_query.answer()

    return html_to_pdf(update, context)


def end():
    pass


def check_if_text(update, context):
    update


def main():
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_ACTION: [CallbackQueryHandler(query_answer,
                            pattern='^' + str(CREATE_NEW_PROPOSAL) + '$'),

                            CallbackQueryHandler(get_test_pdf_dict,
                            pattern='^' + str(TEST) + '$'),

                            CallbackQueryHandler(html_to_pdf,
                            pattern='^' + str(CREATE_PDF) + '$'),
                     
                            CallbackQueryHandler(edit_choose,
                            pattern="^" + str(EDIT_CHOOSE) + '$'),

                            CallbackQueryHandler(edit_header,
                            pattern=f'.+{EDIT_HEADER}$')],

            STORE_DATA: [MessageHandler(Filters.text, store_data)]
        },
        fallbacks=[CommandHandler('end', end)],

        allow_reentry=True
     )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
