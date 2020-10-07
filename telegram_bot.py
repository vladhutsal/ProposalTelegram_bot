#!/usr/bin/env python3

from bs4 import BeautifulSoup
import telegram
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
 
logger = logging.getLogger(__name__)

ASK_HEADER, FILL_DATA, OVERVIEW, SELECT_ACTION = map(chr, range(4))
CREATE_NEW_PROPOSAL, HELP, FIRST_HEADER = map(chr, range(4, 7))

to_search = {
    'name1': 'Name 1',
    'name2': 'Name 2',
    'name3': 'Name 3',
    'name4': 'Name 4'
}

def start(update, context):
    # Creating a generator for going through all of the to_search headers and assign it to user_context
    context.user_data['headers'] = to_search
    context.user_data['header_updater'] = (header for header in context.user_data['headers'].keys())

    context.user_data['first_header'] = True

    buttons = [[
        InlineKeyboardButton(text='Create new proposal', callback_data=str(CREATE_NEW_PROPOSAL)),
        InlineKeyboardButton(text='Help', callback_data=str(HELP))
    ]]
    
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Hi, I`ll help you to complete the proposal.')
    update.message.reply_text(text='What do you want to do?', reply_markup=keyboard)
    
    return SELECT_ACTION


def ask_header_content(update, context):
    logger.info(f'ask_header_content report: {update.callback_query}\n')

    try:
        context.user_data['status'] = next(context.user_data['header_updater'])
        status = context.user_data['status']

        update.message.reply_text(f'Type {status}')
        logger.info(f'status 56: {status}\n')
        fill_data(update, context)
        return ASK_HEADER

    except StopIteration:
        return OVERVIEW


def fill_data(update, context):
    status = context.user_data['status']
    context.user_data['headers'][status] = update.message.text
    st = context.user_data['headers']
    logger.info(f'fill_data report: {st}\n')
    

def overview(update, context):
    st = context.user_data['headers']
    logger.info(f'overview report: {st}\n')

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


def user_help(update, context):
    pass


def end():
    pass


def main():
    updater = Updater(token='1259603530:AAHRWl9xHFeoLncdt1jhXLC2ddFLh0YMHBg', use_context=True)
    dispatcher = updater.dispatcher

    # CREATE PROPOSAL HANDLER
    proposal_creation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_header_content, pattern='^' + str(CREATE_NEW_PROPOSAL) + '$')],

        states=
        {
            ASK_HEADER: [MessageHandler(Filters.text, ask_header_content)],
            FILL_DATA: [MessageHandler(Filters.text, fill_data)],
            OVERVIEW: [MessageHandler(Filters.text, overview)]
        },

        fallbacks=[CommandHandler('end', end)],
    )

    # START HANDLER
    top_lvl_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states=
        {
            SELECT_ACTION: [proposal_creation_handler,
                            CallbackQueryHandler(user_help, pattern='^' + str(HELP) + '$')]
        },

        fallbacks=[CommandHandler('end', end)]
    )

    dispatcher.add_handler(top_lvl_handler)  
    updater.start_polling()


if __name__ == "__main__":
    main()
