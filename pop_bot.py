#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import subprocess
from popwatch import config
from threading import Thread
from popwatch.storeStock import storeStock
from popwatch.telegram_utils import telegramUtils
from telegram.ext import Updater, CommandHandler

_LOG = logging.getLogger(__name__)


def startfunc(stkObj):
    stkObj.pop_search()


def main():
    # Create the EventHandler and pass it your bot's token.
    UPDATER = Updater(config.TELEGRAM_TOKEN)

    stkObj = storeStock(UPDATER)
    gramObj = telegramUtils(stkObj)

    _LOG.info('Starting bot threads')
    t = Thread(target=startfunc, args=(stkObj,))
    t.start()

    # Get the dispatcher to register handlers
    dp = UPDATER.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", gramObj.start))
    dp.add_handler(CommandHandler('add', gramObj.add))
    dp.add_handler(CommandHandler('list', gramObj.list))
    dp.add_handler(CommandHandler('delete', gramObj.delete))
    dp.add_handler(CommandHandler('stop', gramObj.stop))
    dp.add_handler(CommandHandler("help", gramObj.help))

    # log all errors
    dp.add_error_handler(gramObj.error)

    # Start the Bot
    _LOG.info('Starting telegram')
    UPDATER.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    UPDATER.idle()


if __name__ == '__main__':
    try:
        main()
    except Exception as excp:
        _LOG.error('Received exception: {0}'.format(excp))
        import traceback
        traceback.print_exc()
