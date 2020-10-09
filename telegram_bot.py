#!/usr/bin/env python3

import re
import telegram
import logging

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

# create an overview
# create edit function
# create restart function
# create errors handling
# create loger with line number


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

STORE_HEADER, FILL_DATA, OVERVIEW, SELECT_ACTION = map(chr, range(4))
CREATE_NEW_PROPOSAL, HELP, FIRST_HEADER = map(chr, range(4, 7))

to_search = {
    'MCG': 'Main current goal',
    'CE_list': 'Client Expectations',
    'NPS_list': 'Next potential steps',
    'TOPS': 'Type of provided services',
    'RT': 'Report types',
    'EHPW': 'Expected hours per week',
    'VA_list': 'Value-added'
}


def start(update, context):
    context.user_data['headers'] = {
                                    'MCG': 'Main current goal',
                                    'CE_list': 'Client Expectations',
                                    'NPS_list': 'Next potential steps',
                                    'TOPS': 'Type of provided services',
                                    'RT': 'Report types',
                                    'EHPW': 'Expected hours per week',
                                    'VA_list': 'Value-added'
                                    }
    context.user_data['header_updater'] = (header for header in to_search.keys())
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
    header_name = to_search[status]
    context.bot.send_message(chat_id=c_id,
                             text=f'Write content for header, named {header_name}')

    return STORE_HEADER


def fill_data(update, context):
    status = context.user_data['status']
    user_text = update.message.text
    context.user_data['headers'][status] = user_text

    st = context.user_data['headers']
    logger.info(f'fill_data report dict: {st}\n')

    return show_header_name(update, context)


def overview(update, context):
    headers = context.user_data['headers']
    update.message.reply_text('Your headers are:')
    for header in to_search.keys():
        header_content = headers[header]
        text = f'<b>{to_search[header]}</b>\n{header_content}'
        update.message.reply_text(text=text,
                                  parse_mode=telegram.ParseMode.HTML)

    return ConversationHandler.END


def html_to_pdf(context, update):
    env = Environment(loader=FileSystemLoader('static/'))
    template = env.get_template('index.html')
    html_out = template.render(headers=context.user_data['headers'])

    with open('static/result.html', 'w+') as html:
        html.write(html_out)

    HTML('static/result.html').write_pdf('static/result.pdf',
                                         stylesheets=CSS('static/main.css'))


def user_help(update, context):
    pass


def end():
    pass


def main():
    updater = Updater(token='1259603530:AAHRWl9xHFeoLncdt1jhXLC2ddFLh0YMHBg',
                      use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states=
        {
            SELECT_ACTION: [CallbackQueryHandler(show_header_name,
                            pattern='^' + str(CREATE_NEW_PROPOSAL) + '$'),

                            CallbackQueryHandler(user_help,
                            pattern='^' + str(HELP) + '$')],

            STORE_HEADER: [MessageHandler(Filters.text, fill_data)],

        },
        fallbacks=[CommandHandler('end', end)]
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
