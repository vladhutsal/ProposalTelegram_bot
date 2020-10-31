#!/usr/bin/env python3

import telegram
import logging
import tempfile
from telegram_bot.credentials import TOKEN

from telegram_bot.Proposal import Proposal
from telegram_bot.ProposalDBHandler import ProposalDBHandler

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML     # import CSS
from docx import Document
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler)


logging.getLogger('apscheduler.scheduler').propagate = False
db_handler = ProposalDBHandler()
proposal = Proposal(db_handler)

# set pattern constatnts

# States for ConversationHandler:
STORE_DATA, SELECT_ACTION, STORE_DOCX, STORE_PHOTO = map(chr, range(4))
# Templates constatns:
ADD_DOCX, ADD_INFO, ADD_NEW_ENGINEER, ADD_ENGINEERS_RATE,  = map(chr, range(5, 9))
# States of the proposal fill process, to show in what state bot is right now:
EDIT_TITLE, CHOOSE_ENGINEER, OVERVIEW, INIT_TEMP, CREATE_PDF, TEST = map(chr, range(10, 16))

SHOW_BUTTONS, CHOOSE_TITLE_TO_EDIT, ADD_ENGINEER_TO_PROPOSAL = map(chr, range(17, 20))

templates = {
    ADD_DOCX:           proposal.content_dict,
    ADD_INFO:           proposal.info_dict,
    ADD_NEW_ENGINEER:   proposal.engineer_dict,
    ADD_ENGINEERS_RATE: db_handler.engineers_rates
}


def start(update, context):
    # reset content dict when restarting proposal
    context.user_data['chat_id'] = update.message.chat_id
    context.user_data['test'] = False

    buttons = [[
        InlineKeyboardButton(text='Create new proposal',
                             callback_data=ADD_DOCX),
        InlineKeyboardButton(text='Test',
                             callback_data=str(TEST))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Hi, I`ll help you to complete the proposal.')
    update.message.reply_text(text='What do you want to do?',
                              reply_markup=keyboard)

    return SELECT_ACTION


def init_add_info(update, context):
    proposal.current_dict = templates[ADD_INFO]
    proposal.reset_iter()

    return next_title(update, context)


def init_add_docx(update, context):
    proposal.current_dict = templates[ADD_DOCX]
    proposal.reset_iter()

    return ask_for_docx(update, context)


def init_add_engineers_rate(update, context):
    proposal.current_dict = templates[ADD_ENGINEERS_RATE]
    proposal.reset_iter()

    return next_title(update, context)


def init_add_new_engineer(update, context):
    proposal.current_dict = templates[ADD_NEW_ENGINEER]
    proposal.reset_iter()

    return next_title(update, context)


def ask_for_docx(update, context):
    query = update.callback_query
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text='Send me your DOCX file with main content')
    query.answer(text='Waiting for your docx')
    return STORE_DOCX


def store_docx(update, context):
    file_id = update.message.document.file_id
    name = proposal.get_random_name()
    docx_path = f'media/{name}.docx'
    proposal.current_doc_name = docx_path

    Docx_obj = context.bot.get_file(file_id=file_id)
    Docx_obj.download(custom_path=docx_path)
    proposal.content_dict = docx_parser(proposal)

    return init_add_info(update, context)


def docx_parser(proposal):
    doc = Document(proposal.current_doc_name)

    for content in doc.paragraphs:
        if content.style.name == 'Heading 2':
            try:
                proposal.get_next_title_id()
            except StopIteration:
                return True
        elif not content.text:
            pass
        else:
            proposal.store_content(content.text)
    return proposal.current_dict


def show_buttons(update, context):
    buttons = []
    btn1 = add_button('Edit info', CHOOSE_TITLE_TO_EDIT)
    btn2 = add_button('Choose engineer', CHOOSE_ENGINEER)
    buttons = append_btns(buttons, btn1, btn2)

    text = '<b>What`s next?</b>'
    if getattr(update, 'callback_query'):
        update.callback_query.answer()
        keyboard = InlineKeyboardMarkup.from_row(buttons)
        update.callback_query.edit_message_text(text=text,
                                                reply_markup=keyboard,
                                                parse_mode=telegram.ParseMode.HTML)
        print('show buttons - QUERY')
    else:
        keyboard = InlineKeyboardMarkup.from_row(buttons)
        context.bot.send_message(chat_id=context.user_data['chat_id'],
                                 text=text,
                                 reply_markup=keyboard,
                                 parse_mode=telegram.ParseMode.HTML)
        print('show buttons - UPDATE')
    return SELECT_ACTION


def append_btns(buttons, *args):
    for btn in args:
        buttons.append(btn)
    return buttons


def add_button(text=None, callback=None):
    btn = InlineKeyboardButton(text=text, callback_data=callback)
    return btn


# ================ FILL TEMPLATES WITH DATA
def next_title(update, context):
    try:
        proposal.get_next_title_id()
        return show_title(update, context)
    except StopIteration:
        if proposal.current_template == ADD_NEW_ENGINEER:

            # telegram_bot.py is no need to know about db_handler class
            err = db_handler.store_new_engineer_to_db(proposal.current_dict)
            proposal.reset_engineer_dict()
            if err:
                show_error_message(update, context)

        return show_buttons(update, context)


def show_title(update, context):
    title_id = proposal.current_title_id
    title_name = proposal.get_bold_title(title_id)
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text=title_name,
                             parse_mode=telegram.ParseMode.HTML)
    if title_id == 'PHT':
        return STORE_PHOTO

    return STORE_DATA


def edit_title(update, context):
    query = update.callback_query
    proposal.current_title_id = detach_id_from_callback(query.data)
    proposal.edit_all = False
    query.answer()

    if ADD_ENGINEERS_RATE in query.data:
        add_engineer_to_proposal()
        proposal.current_dict = db_handler.engineers_rates

    return show_title(update, context)


def store_photo(update, context):
    photo_info = update.message.photo[-1]
    file_id = photo_info.file_id
    File_obj = context.bot.get_file(file_id=file_id)

    dir_path = 'engineers_photo/'
    name = proposal.get_random_name()
    photo_path = f'{dir_path}{name}.jpg'
    save_path = f'"./{dir_path}{name}.jpg"'
    File_obj.download(custom_path=photo_path)
    proposal.store_content(save_path)

    return next_title(update, context)


def store_data(update, context):
    user_content = update.message.text
    proposal.store_content(user_content)

    if proposal.edit_all:
        return next_title(update, context)

    elif not proposal.edit_all:
        proposal.edit_all = True
        if proposal.add_rate:
            proposal.add_rate = False
            return choose_engineers(update, context)
        return overview(update, context)


# ================ EDIT AND OVERVIEW
# there will be two buttons - "Edit" and "Add info"/"Choose engineers"
def overview(update, context):
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text='<b>Info you`ve provided:</b>',
                             parse_mode=telegram.ParseMode.HTML)
    for title_id in proposal.current_dict.keys():
        title = proposal.get_bold_title(title_id)
        content = proposal.get_title_content(title_id)
        context.bot.send_message(chat_id=context.user_data['chat_id'],
                                 text=f'{title}\n{content}',
                                 parse_mode=telegram.ParseMode.HTML)

    return show_buttons(update, context)


def choose_title_to_edit(update, context):
    query = update.callback_query
    current_dict = proposal.current_dict

    buttons = []
    for title_id in proposal.current_dict.keys():
        text = f'{current_dict[title_id][0]}'
        callback_data = f'{title_id}, {EDIT_TITLE}'
        btn = [add_button(text, callback_data)]
        append_btns(buttons, btn)

    append_btns(buttons, [add_button('<< Go back', SHOW_BUTTONS)])

    context.user_data['update_id'] = query.id
    query.answer()
    keyboard = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='Choose a title you want to edit:',
                            reply_markup=keyboard)

    return SELECT_ACTION


# ================ ENGINEERS
def choose_engineers(update, context):
    query = update.callback_query
    engineers = db_handler.get_engineers_id_list()

    buttons = []
    if engineers:
        for engineer_id in engineers:
            engineer_name = db_handler.get_field_info(engineer_id, 'N')
            if engineer_id not in db_handler.engineers_in_proposal_id:
                callback_data = f'{engineer_id}, {ADD_ENGINEER_TO_PROPOSAL}'
                btn = [add_button(engineer_name, callback_data)]
                buttons.append(btn)

    help_btns = [add_button('Add new engineer', ADD_NEW_ENGINEER),
                 add_button('Continue', CREATE_PDF)]
    buttons.append(help_btns)

    keyboard = InlineKeyboardMarkup(buttons)
    text = 'Choose engineers: '
    if query:
        query.edit_message_text(text=text,
                                reply_markup=keyboard)
        query.answer()
    else:
        context.bot.send_message(chat_id=context.user_data['chat_id'],
                                 text=text,
                                 reply_markup=keyboard)

    return SELECT_ACTION


def add_engineer_to_proposal(update, context):
    # add engineers id to list of engineers in current proposal:
    query = update.callback_query
    engineer_id = detach_id_from_callback(query.data)
    curr_list = db_handler.engineers_in_proposal_id
    curr_list.append(int(engineer_id))

    # add engineers id to dictionary as key {'engn_id': ['name', 'rate']}
    engineer_name = db_handler.get_field_info(engineer_id, 'N')
    db_handler.engineers_rates[engineer_id] = [f'Current rate for {engineer_name}', '']

    return choose_engineers(update, context)


# ================ HELPERS
def detach_id_from_callback(query_data):
    additional_query_data = query_data.split(',')[0]
    return additional_query_data


# use callback query answer to show notification on top of the bots chat
def show_error_message(update, context):
    context.bot.send_message(chat_id=context.user_data['chat_id'],
                             text='This engineer is already in db')


def generate_tmp_files(*args):
    res = []
    for suffix in args:
        tmp_file = tempfile.NamedTemporaryFile(suffix=suffix, dir='.')
        res.append(tmp_file)
    return res


# ================ HTML TO PDF
# how to call all next functions without update and context args?
def generate_html(update, contex):
    print('FINAL CONTENT DICT', proposal.content_dict)
    collected_data = proposal.collect_user_data_for_html()

    env = Environment(loader=FileSystemLoader('static/'))
    template = env.get_template('index.html')
    jinja_rendered_html = template.render(**collected_data)
    proposal.html = generate_tmp_files('.html')[0]

    with open(proposal.html.name, 'w+') as html:
        html.write(jinja_rendered_html)

    return generate_pdf(update, contex)


def generate_pdf(update, context):
    pdf_doc = HTML(proposal.html.name)
    pdf_doc_rndr = pdf_doc.render(stylesheets=['static/main.css'])
    page = pdf_doc_rndr.pages[0]
    child_list = [child for child in page._page_box.descendants()]

    body_height = child_list[2].height
    page.height = body_height
    proposal.pdf = generate_tmp_files('.pdf')[0]
    pdf_doc_rndr.write_pdf(proposal.pdf.name)

    update.callback_query.answer()

    return send_pdf(context, update)


def send_pdf(context, update):
    chat_id = context.user_data['chat_id']

    with open(proposal.pdf.name, 'rb') as pdf:
        context.bot.send_document(chat_id=chat_id, document=pdf)

    return ConversationHandler.END


# ================ GENERATE TEST PDF
def get_test_pdf_dict(update, context):
    proposal.test = True
    update.callback_query.answer()

    return generate_html(update, context)


def end():
    pass


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_ACTION: [CallbackQueryHandler(init_add_docx,
                            pattern=ADD_DOCX),

                            CallbackQueryHandler(show_buttons,
                            pattern=SHOW_BUTTONS),

                            CallbackQueryHandler(choose_engineers,
                            pattern='^' + str(CHOOSE_ENGINEER) + '$'),

                            CallbackQueryHandler(init_add_new_engineer,
                            pattern=ADD_NEW_ENGINEER),

                            CallbackQueryHandler(add_engineer_to_proposal,
                            pattern=f'.+{ADD_ENGINEER_TO_PROPOSAL}$'),

                            CallbackQueryHandler(edit_title,
                            pattern=f'.+{EDIT_TITLE}$'),

                            CallbackQueryHandler(get_test_pdf_dict,
                            pattern=TEST),

                            CallbackQueryHandler(generate_html,
                            pattern='^' + str(CREATE_PDF) + '$'),

                            CallbackQueryHandler(choose_title_to_edit,
                            pattern=CHOOSE_TITLE_TO_EDIT),

                            CallbackQueryHandler(overview,
                            pattern='^' + str(OVERVIEW) + '$')],

            STORE_DATA: [MessageHandler(Filters.text, store_data)],

            STORE_PHOTO: [MessageHandler(Filters.photo, store_photo)],

            STORE_DOCX: [MessageHandler(Filters.document.docx, store_docx)],
        },

        fallbacks=[CommandHandler('end', end)],

        allow_reentry=True,
         
        per_message=False
     )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
