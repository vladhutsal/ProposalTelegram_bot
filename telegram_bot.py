#!/usr/bin/env python3

from bs4 import BeautifulSoup
import telegram
import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
 
logger = logging.getLogger(__name__)

RUN_THROUGH_HEADERS, FILL_DATA = range(2)

to_search = {
    'name1': 'Name 1',
    'name2': 'Name 2',
    'name3': 'Name 3',
    'name4': 'Name 4'
}

def start(update, context):
    context.user_data['headers'] = to_search
    context.user_data['count'] = 0

    context.bot.send_message(chat_id=update.effective_chat.id, text='I`ll help you to complete the proposal. Type something to begin.')

    return RUN_THROUGH_HEADERS


def run_through_headers(update, context):
    count = context.user_data['count']

    current_header = f'name{count}'
    context.user_data['headers'][current_header] = update.message.text
    update.message.reply_text('Type next name')
    context.user_data['count'] += 1
    if context.user_data['count'] < 4:
        return RUN_THROUGH_HEADERS
    
    return fill_data(context)
    

def fill_data(context):
    print(context.user_data['answers_arr'])

    return ConversationHandler.END


def change_text(update, context):
    with open('static/index.html', 'r+') as page:
        parser = BeautifulSoup(page, 'html.parser')
    
    for header in context.user_data['headers'].keys():
        pass

    tag_data = parser.find('p', tgname='name1')
    tag_data.string.replace_with('bar')
    res_content = parser.prettify()

    with open('static/result.html', 'w+') as res_doc:
        res_doc.write(res_content)


def end():
    pass


def main():
    updater = Updater(token='1259603530:AAHRWl9xHFeoLncdt1jhXLC2ddFLh0YMHBg', use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=
        [
            CommandHandler('start', start)
        ],

        states=
        {
            RUN_THROUGH_HEADERS: [MessageHandler(Filters.text, run_through_headers)],
            FILL_DATA: [MessageHandler(Filters.text, fill_data)],
        },

        fallbacks=
        [
            CommandHandler('end', end)
        ]
    )

    dispatcher.add_handler(conv_handler)  
    updater.start_polling()


if __name__ == "__main__":
    main()
