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

updater = Updater(token='', use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def header(update, context):
    pass

def start_callback(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=f'*{header}*', parse_mode=telegram.ParseMode.MARKDOWN_V2)

dispatcher.add_handler(CommandHandler("start", start_callback))


# def bold(update, context):
#     text = ' '.join(context.args)
#     chat_id = update.effective_chat.id
#     context.bot.send_message(chat_id=chat_id, text=f'*{text}*', parse_mode=telegram.ParseMode.MARKDOWN_V2)

# bold_handler = CommandHandler('bold', bold)
# dispatcher.add_handler(bold_handler)


updater.start_polling()
