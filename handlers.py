from datetime import datetime
import json
import logging
from utils import load_config
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from loguru import logger
import traceback
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from backend import Backend


config = load_config()
backend = Backend(config['mongo'])

HELP_TEXT = """
Правило клуба диванных разметчиков.
1. Никому не рассказывать про бота для разметки.
2. Никому никогда не рассказывать про бота для разметки.

...

1. Алиэкспресс не размечаем?
2. 
"""

label_form_template = '''
id: {sample_id}
Текст:
"{text}"
'''


def prepare_markup():
    instance = backend.get_sample()
    if instance is None:
        return 'Now new samples', InlineKeyboardMarkup(inline_keyboard=[])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton('+', callback_data=json.dumps({'_id': instance['_id'], 'label': '+'})),
        InlineKeyboardButton('-', callback_data=json.dumps({'_id': instance['_id'], 'label': '-'})),
        InlineKeyboardButton('?', callback_data=json.dumps({'_id': instance['_id'], 'label': '?'})),
    ]])
    text_data =label_form_template.format(sample_id=instance['_id'], text=instance['text'])
    return text_data, keyboard


def start(bot, update):
    logger.info('Start request handled')
    text_data, keyboard = prepare_markup()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_data[:4094], reply_markup=keyboard)


def handle_response(bot, update):
    query = update.callback_query
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[])
    payback = json.loads(query.data)
    backend.label_sample(sample_id=payback['_id'], label=payback['label'])
    query.edit_message_reply_markup(reply_markup)

    # Send new
    text_data, keyboard = prepare_markup()
    bot.sendMessage(chat_id=update.effective_chat['id'], text=text_data, reply_markup=keyboard)


def echo(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='Я работаю')


def help_command(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=HELP_TEXT)


def error(bot, update, error):
    try:
        raise error
    except (Unauthorized, BadRequest, TimedOut,
            NetworkError, ChatMigrated, TelegramError) as e:
        logger.warning(f'Telegram related error occured: {e}')
        # handle all other telegram related errors
    except Exception as e:
        # print(traceback.extract_stack())
        logger.warning(f'Non telegram related error occured: {e}.')
        traceback.print_exc()