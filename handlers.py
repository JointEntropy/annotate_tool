from datetime import datetime
import json
import logging
from utils import load_config
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from loguru import logger
import traceback
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

config = load_config()

samples_to_annotate = [
    {'idx': 1, 'text': 'citilink'},
    {'idx': 2, 'text': 'puk minnnnn'},
]
idx = 0

chad_ids = dict()


def get_sample_to_annotate():
    global idx
    if idx < len(samples_to_annotate):
        item = samples_to_annotate[idx]
        idx += 1
        return item


def prepare_markup():
    instance = get_sample_to_annotate()
    if instance is None:
        return 'Now new samples', InlineKeyboardMarkup(inline_keyboard=[])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton('+', callback_data=json.dumps({instance['idx']: '+'})),
        InlineKeyboardButton('-', callback_data=json.dumps({instance['idx']: '-'}))
    ]])
    text_data = instance['text']
    return text_data, keyboard


def start(bot, update):
    logger.info('Start request handled')
    # chad_ids[update.message.chat_id] = instance_idx

    text_data, keyboard = prepare_markup()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_data, reply_markup=keyboard)


def handle_response(bot, update):
    query = update.callback_query
    # print(query.answer())
    # reply_markup = query.message.reply_markup
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[])
    answer = query.data
    print(answer)
    query.edit_message_reply_markup(reply_markup)

    # Send new
    text_data, keyboard = prepare_markup()
    bot.sendMessage(chat_id=update.effective_chat['id'], text=text_data, reply_markup=keyboard)


def echo(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='Я работаю')





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