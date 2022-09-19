# https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.error import NetworkError, Unauthorized
import json
import handlers
from loguru import logger
from utils import load_config


config = load_config()


def main():
    bot_token = config.get('token', None)
    poll_interval = config.get('poll_interval', 1)

    logger.info('Init updates...')
    updater = Updater(bot_token, request_kwargs=dict(proxy_url=config.get('proxy')))

    logger.info('Add handlers...')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", handlers.start))
    dp.add_handler(CommandHandler("help", handlers.help_command))
    dp.add_handler(CallbackQueryHandler(handlers.handle_response))
    dp.add_handler(MessageHandler(Filters.text, handlers.echo))
    dp.add_error_handler(handlers.error)

    # Start the Bot
    logger.info('Start polling...')
    updater.start_polling(poll_interval=poll_interval)

    logger.info('Start idle')
    updater.idle()


if __name__ == '__main__':
    main()
