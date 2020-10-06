#!/usr/bin/env python3

import telegram
import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
headers = ['header1', 'header2', 'header3', 'header4']

updater = Updater(token='1259603530:AAHRWl9xHFeoLncdt1jhXLC2ddFLh0YMHBg', use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="hello")

def get_text(update, context):
    update = update.message.text
    change_text(update)

def change_text(text):
    with open('static/index.html', 'r+') as page:
        doc_content = page.read()
        print(doc_content)


def main():
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    get_text_handler = MessageHandler(Filters.text & (~Filters.command), get_text)
    dispatcher.add_handler(get_text_handler)
    
    updater.start_polling()


if __name__ == "__main__":
    main()
