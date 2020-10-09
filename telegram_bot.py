#!/usr/bin/env python3

import re
import telegram
import logging

from bs4 import BeautifulSoup
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

# create an overview and editing function
# create possibility to restart the bot from Telegram


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
    context.user_data['headers'] = to_search
    context.user_data['header_updater'] = (header for header in to_search.keys())
    context.user_data['first_header'] = True
    context.user_data['chat_id'] = update.message.chat_id

    buttons = [[
        InlineKeyboardButton(text='Create new proposal', callback_data=str(CREATE_NEW_PROPOSAL)),
        InlineKeyboardButton(text='Help', callback_data=str(HELP))
    ]]
    
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Hi, I`ll help you to complete the proposal.')
    update.message.reply_text(text='What do you want to do?', reply_markup=keyboard)
    
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
    context.bot.send_message(chat_id=c_id, text=f'Write content for header, named {header_name}')

    return STORE_HEADER    


def fill_data(update, context):
    status = context.user_data['status']

    if re.search(r'\w+_list$', status):
        user_text = update.message.text.split('\n')
    else:
        user_text = update.message.text

    context.user_data['headers'][status] = user_text

    st = context.user_data['headers']
    logger.info(f'fill_data report dict: {st}\n')

    return show_header_name(update, context)


def overview(update, context):
    headers = context.user_data['headers']
    update.message.reply_text(f'Your headers are \n {headers}')

    return change_text(update, context)


def change_text(update, context):
    with open('static/index.html', 'r+') as input_html:
        parser = BeautifulSoup(input_html, 'html.parser')
    
    headers = context.user_data['headers']
    for header in headers.keys():
        find_header = parser.find(tgname=f'{header}')
        find_header.string.replace_with(headers[header])

    res_content = parser.prettify()
    with open('static/result.html', 'w+') as output_html:
        output_html.write(res_content)
    
    return ConversationHandler.END


def html_to_pdf(context, update):
    HTML('static/result.html').write_pdf('static/result.pdf', stylesheets=CSS('static/main.css'))


def user_help(update, context):
    pass


def end():
    pass


def main():
    updater = Updater(token='1259603530:AAHRWl9xHFeoLncdt1jhXLC2ddFLh0YMHBg', use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states=
        {
            SELECT_ACTION: [CallbackQueryHandler(show_header_name, pattern='^' + str(CREATE_NEW_PROPOSAL) + '$'),
                            CallbackQueryHandler(user_help, pattern='^' + str(HELP) + '$')],

            STORE_HEADER: [MessageHandler(Filters.text, fill_data)],

        },
        fallbacks=[CommandHandler('end', end)]
    )
    dispatcher.add_handler(conv_handler)  
    updater.start_polling()


if __name__ == "__main__":
    main()
