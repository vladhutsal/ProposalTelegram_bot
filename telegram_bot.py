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

ASK_HEADER, FILL_DATA, OVERVIEW = range(3)

to_search = {
    'name1': 'Name 1',
    'name2': 'Name 2',
    'name3': 'Name 3',
    'name4': 'Name 4'
}

def start(update, context):
    context.user_data['headers'] = to_search
    context.user_data['count'] = 0

    context.bot.send_message(chat_id=update.effective_chat.id, text='I`ll help you to complete the proposal. Type something to start.')
    context.user_data['status_updater'] = (header for header in context.user_data['headers'].keys())
    
    return ASK_HEADER


def ask_header_content(update, context):
    try:
        context.user_data['status'] = next(context.user_data['status_updater'])
        status = context.user_data['status']

        update.message.reply_text(f'Type {status}')
        logger.info(f'status 39: {status}')
        fill_data(update, context)
        return ASK_HEADER

    except StopIteration:
        return OVERVIEW


def fill_data(update, context):
    status = context.user_data['status']
    context.user_data['headers'][status] = update.message.text
    

def overview(context):
    print(context.user_data['headers'])

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
            ASK_HEADER: [MessageHandler(Filters.text, ask_header_content)],
            FILL_DATA: [MessageHandler(Filters.text, fill_data)],
            OVERVIEW: [MessageHandler(Filters.text, overview)],
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
