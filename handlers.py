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
from typing import Optional

config = load_config()
backend = Backend(config['mongo'])

HELP_TEXT = """
Размечаем описания, в котором есть отсылка на товары из интернета-магазина.
Цель разметить данные так, чтобы модель, обученная  на размеченных данных,  могла по тексту понять и подстветить примеры, где есть упоминания 
интернет-магазина.

1. Лучше разметить меньше, но точнее. Если нет уверенности, то ставим "?". 
2. Часть ссылок в описании поломана по техничесикм причинам. Это не должно влиять на логику разметки.
Если из текста ясно, что это ссылка на товар в интернет магазине => `+`
3. Если например обозревают игрушки с алиэксперсс и есть ссылка на товар => `+`
4. Продажа услуг(курсы английского, курсы эзотерики и т.п.) не относятся к целевому сегменту => `-`
5. Функционала исправления ошибки пока нет. Если допустил ошибку переслать сообщение разработчку этой белеберды.

Примеров много, нет цели разметить всё  поэтому делаем не до победного конца.

Для начала запускаем `/start`. Если поток прервётся - повторно `/start`.

"""

label_form_template = '''
id: {sample_id}
Текст:
"{text}"
'''


def construct_keyboard(instance_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton('+', callback_data=json.dumps({'_id': instance_id, 'label': '+'})),
        InlineKeyboardButton('-', callback_data=json.dumps({'_id': instance_id, 'label': '-'})),
        InlineKeyboardButton('?', callback_data=json.dumps({'_id': instance_id, 'label': '?'})),
    ]])
    return keyboard


def prepare_markup():
    instance = backend.get_sample()
    if instance is None:
        return 'Now new samples', InlineKeyboardMarkup(inline_keyboard=[])
    keyboard = construct_keyboard(instance['_id'])
    text_data = label_form_template.format(sample_id=instance['_id'], text=instance['text'])
    return text_data[:4094], keyboard


def start(bot, update):
    logger.info('Start request handled')
    text_data, keyboard = prepare_markup()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_data, reply_markup=keyboard)


def handle_response(bot, update):
    query = update.callback_query
    payback = json.loads(query.data)
    if payback.get('remove', False):
        backend.delete_label(sample_id=payback['_id'])
        bot.deleteMessage(chat_id=query.message['chat_id'], message_id=query.message['message_id'])
        return

    backend.label_sample(sample_id=payback['_id'], label=payback['label'], labeler=update.effective_chat['username'])

    fix_mistake_markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton('Удалить разметку', callback_data=json.dumps({'_id': payback['_id'], 'remove': True})),
    ]])
    query.edit_message_reply_markup(fix_mistake_markup)
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
        print(traceback.extract_stack())
        logger.warning(f'Non telegram related error occured: {e}.')
        traceback.print_exc()