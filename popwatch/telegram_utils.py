import json
import logging
import threading
import validators
import portalocker

from popwatch import config
from urlparse import urlparse

_LOG = logging.getLogger(__name__)


class telegramUtils(object):

    def __init__(self, stkObj):
        self.stkObj = stkObj

    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        self.stkObj.THREAD_ALIVE = True
        update.message.reply_text('Starting bot search.')

    def stop(self, bot, update):
        """Send a message when the command /stop is issued."""
        self.stkObj.THREAD_ALIVE = False
        update.message.reply_text('Stopping bot search.')

    def add(self, bot, update):
        """Send a message when the command /add is issued."""
        if not len(update.message.text.split()) == 2:
            _LOG.error('Wrong number of parameters passed.')
            update.message.reply_text('Wrong number of parameters passed.')

        if not validators.url(update.message.text.split()[1]):
            _LOG.error('URL exception {0}'.format(update.message.text.split()[1]))
            update.message.reply_text('URL exception {0}'.format(update.message.text.split()[1]))

        parsed = urlparse(update.message.text.split()[1])
        store = parsed.netloc.split('.')[-2]

        with portalocker.Lock(config.FUNKO_POP_LIST, "r", timeout=1) as data_file:
            funkopop_links = json.load(data_file)

        url = update.message.text.split()[1]
        if not [x for x in funkopop_links if x['url'] == url]:
            funkopop_links.append({"store": store, "url": url})
        else:
            _LOG.info('Duplicate entry ignored {0}'.format(url))
            update.message.reply_text('Duplicate entry was not added to bot search.')
            return

        with portalocker.Lock(config.FUNKO_POP_LIST, "w", timeout=1) as data_file:
            json.dump(funkopop_links, data_file, sort_keys=True, indent=4, separators=(',', ': '))

        update.message.reply_text('Added entry into bot search.')

    def delete(self, bot, update):
        """Send a message when the command /delete is issued."""
        with portalocker.Lock(config.FUNKO_POP_LIST, "r", timeout=1) as data_file:
            funkopop_links = json.load(data_file)

        url = update.message.text.split()[1]
        if [x for x in funkopop_links if x['url'] == url]:
            new_list = []
            for idx, elem in enumerate(funkopop_links):
                if not elem["url"] == url:
                    new_list.append(elem)
        else:
            _LOG.info('Entry not found in search list {0}'.format(url))
            update.message.reply_text('Entry not found in bot search.')
            return

        with portalocker.Lock(config.FUNKO_POP_LIST, "w", timeout=1) as data_file:
            json.dump(new_list, data_file, sort_keys=True, indent=4, separators=(',', ': '))

        update.message.reply_text('Deleted entry in bot search.')

    def list(self, bot, update):
        """Send a message when the command /list is issued."""
        with portalocker.Lock(config.FUNKO_POP_LIST, "r", timeout=1) as data_file:
            funkopop_links = json.load(data_file)

        if not funkopop_links:
            update.message.reply_text('No entries in search.')

        for elem in funkopop_links:
            update.message.reply_text(elem["url"])

    def help(self, bot, update):
        """Send a message when the command /help is issued."""
        update.message.reply_text("Bot Commands:\n"
                                  "/start - start searching for pops\n"
                                  "/stop - stops seatching for pops\n"
                                  "/add - takes a parameter URL and adds it to search list\n"
                                  "/delete - takes a parameter URL and deletes it from the search list\n"
                                  "/list - lists current pop search list\n")
                                  #"/setup - Creates User Profile for Auto Checkout\n"

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        _LOG.error('Update "%s" caused error "%s"', update, error)
