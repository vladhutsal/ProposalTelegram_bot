#!/usr/bin/env python3

import telegram
import logging
import tempfile

from credentials import token
from tests.test_pdf import create_lorem_dict

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
CREATE_NEW_PROPOSAL, TEST, CREATE_PDF, EDIT = map(chr, range(3, 7))


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
        InlineKeyboardButton(text='Test',
                             callback_data=str(TEST))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Hi, I`ll help you to complete the proposal.')
    update.message.reply_text(text='What do you want to do?',
                              reply_markup=keyboard)

    return SELECT_ACTION
    

# bad decision to handle one function using objects of different class
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
        InlineKeyboardButton(text='Create PDF', callback_data=str(CREATE_PDF)),
        InlineKeyboardButton(text='Edit', callback_data=str(EDIT))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text='All good?', reply_markup=keyboard)

    return SELECT_ACTION


def edit(update, context):
    hdrs = context.user_data['headers']
    hdr_codes = context.user_data['headers'].keys()

    buttons = []
    for hdr_code in hdr_codes:
        button = [InlineKeyboardButton(text=f'{hdrs[hdr_code][0]}', callback_data=f'{hdr_code}')]
        buttons.append(button)

    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text='Choose:', reply_markup=keyboard)

    return ConversationHandler.END
    

# generate tmp file instead of hardocded one
def html_to_pdf(update, context):
    env = Environment(loader=FileSystemLoader('static/'))
    template = env.get_template('index.html')
    jinja_rendered_html = template.render(headers=context.user_data['headers'])

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
    user_dict = context.user_data['headers']
    context.user_data['headers'] = create_lorem_dict(user_dict)
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
            SELECT_ACTION: [CallbackQueryHandler(show_header_name,
                            pattern='^' + str(CREATE_NEW_PROPOSAL) + '$'),

                            CallbackQueryHandler(get_test_pdf_dict,
                            pattern='^' + str(TEST) + '$'),

                            CallbackQueryHandler(html_to_pdf,
                            pattern='^' + str(CREATE_PDF) + '$'),
                     
                            CallbackQueryHandler(edit,
                            pattern="^" + str(EDIT) + '$')],

            STORE_HEADER: [MessageHandler(Filters.text, fill_data)]
        },
        fallbacks=[CommandHandler('end', end)],

        allow_reentry=True
     )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
