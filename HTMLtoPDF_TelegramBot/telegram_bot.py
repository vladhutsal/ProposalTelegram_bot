#!/usr/bin/env python3

import telegram
import logging

from credentials import token
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


STORE_HEADER, OVERVIEW, SELECT_ACTION = map(chr, range(3))
CREATE_NEW_PROPOSAL, HELP, CREATE_PDF = map(chr, range(3, 6))


def start(update, context):
    # Dict looks like this: 'header key': ['header title', 'header content']'
    context.user_data['headers'] = {
                                    'MCG': ['Main current goal', ''],
                                    'CE_list': ['Client Expectations', ''],
                                    'NPS_list': ['Next potential steps', ''],
                                    'TOPS': ['Type of provided services', ''],
                                    'RT_line': ['Report types', ''],
                                    'EHPW_line': ['Expected hours per week', ''],
                                    'VA_list': ['Value-added', '']
                                }
    context.user_data['header_updater'] = (header for header in context.user_data['headers'].keys())
    context.user_data['first_header'] = True
    context.user_data['chat_id'] = update.message.chat_id

    buttons = [[
        InlineKeyboardButton(text='Create new proposal',
                             callback_data=str(CREATE_NEW_PROPOSAL)),
        InlineKeyboardButton(text='Help',
                             callback_data=str(HELP))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Hi, I`ll help you to complete the proposal.')
    update.message.reply_text(text='What do you want to do?',
                              reply_markup=keyboard)

    return SELECT_ACTION


def show_header_name(update, context):
    if context.user_data['first_header']:
        update.callback_query.answer()
        context.user_data['first_header'] = False

    try:
        context.user_data['status'] = next(context.user_data['header_updater'])
    except StopIteration:
        return overview(update, context)

    c_id = context.user_data['chat_id']
    status = context.user_data['status']
    header = context.user_data['headers'][status][0]
    context.bot.send_message(chat_id=c_id,
                             text=f'Write content for header, named {header}')

    return STORE_HEADER


def fill_data(update, context):
    status = context.user_data['status']
    user_text = update.message.text
    context.user_data['headers'][status][1] = user_text

    return show_header_name(update, context)


def overview(update, context):
    headers = context.user_data['headers']
    update.message.reply_text('Your headers are:')
    for header in headers.keys():
        header_name = headers[header][0]
        header_content = headers[header][1]
        text = f'<b>{header_name}</b>\n{header_content}'
        update.message.reply_text(text=text,
                                  parse_mode=telegram.ParseMode.HTML)
    buttons = [[
        InlineKeyboardButton(text='Create PDF', callback_data=str(CREATE_PDF))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text='All good?', reply_markup=keyboard)

    return SELECT_ACTION


def html_to_pdf(update, context):
    update.callback_query.answer()
    env = Environment(loader=FileSystemLoader('static/'))
    template = env.get_template('index.html')
    html_out = template.render(headers=context.user_data['headers'])

    with open('static/result.html', 'w+') as html:
        html.write(html_out)

    HTML('static/result.html').write_pdf('static/result.pdf',
                                         stylesheets=[CSS('static/main.css')])

    return send_pdf(context, update)


def send_pdf(context, update):
    c_id = context.user_data['chat_id']
    with open('static/result.pdf', 'rb') as pdf:
        context.bot.send_document(chat_id=c_id, document=pdf)

    return ConversationHandler.END


def user_help(update, context):
    pass


def end():
    pass


def main():
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_ACTION: [CallbackQueryHandler(show_header_name,
                            pattern='^' + str(CREATE_NEW_PROPOSAL) + '$'),

                            CallbackQueryHandler(user_help,
                            pattern='^' + str(HELP) + '$'),

                            CallbackQueryHandler(html_to_pdf,
                            pattern='^' + str(CREATE_PDF) + '$')],

            STORE_HEADER: [MessageHandler(Filters.text, fill_data)]
        },
        fallbacks=[CommandHandler('end', end)]
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
