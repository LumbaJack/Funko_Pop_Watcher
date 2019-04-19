from __future__ import absolute_import
import os
import yaml
import yaml.error
import logging
import logging.config
import platform
from operator import itemgetter

_LOG = logging.getLogger(__name__)

def get_distro():
    # Checking Distrobution before passing in connection string
    distroName = platform.system()
    return distroName

global GLOBAL_CONFIG
global CONFIG_FILE
global CONFIG_FILE_ERROR

if get_distro() == "Raspbian GNU/Linux":
    CONFIG_FILE = os.environ.get('FUNKO_POP_WATCH_CONFIG', '/root/FunkoATCBot/examples/pop_watch.yaml')
elif get_distro() == "Windows":
    CONFIG_FILE = os.environ.get('FUNKO_POP_WATCH_CONFIG', './examples/pop_watch_windows.yaml')
else:
    CONFIG_FILE = os.environ.get('FUNKO_POP_WATCH_CONFIG', './examples/pop_watch.yaml')

try:
    with open(CONFIG_FILE, "r") as f:
        GLOBAL_CONFIG = yaml.load(f)
    if not isinstance(GLOBAL_CONFIG, dict):
        config_type = type(GLOBAL_CONFIG)
        GLOBAL_CONFIG = None
        raise TypeError('YAML file came back as a {type}, should be a dictionary'.format(type=config_type))
    print("Loaded config file {filename}".format(filename=CONFIG_FILE))

except yaml.error.YAMLError as yaml_exc:
    _LOG.error("WARNING: Bad YAML with {config_file}: {exc}".format(config_file=CONFIG_FILE, exc=str(yaml_exc)))
    CONFIG_FILE_ERROR = yaml_exc
except IOError as exc:
    _LOG.error(
        "WARNING: Missing configuration at {config_file}: {exc}".format(config_file=CONFIG_FILE, exc=str(exc)))
    CONFIG_FILE_ERROR = exc
except TypeError as exc:
    _LOG.error("WARNING: Bad YAML with {config_file}: {exc}".format(config_file=CONFIG_FILE, exc=str(exc)))
    CONFIG_FILE_ERROR = exc

if GLOBAL_CONFIG is None:
    if CONFIG_FILE is not None:
        print("Unable to load config file {filename}".format(filename=CONFIG_FILE))
    if CONFIG_FILE_ERROR is not None:
        raise CONFIG_FILE_ERROR

LOGGING_CONFIG = GLOBAL_CONFIG.get('logging_config')

if LOGGING_CONFIG is None:
    import yaml

    # Using an example in yaml for reference.
    LOGGING_CONFIG = """
version: 1
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: simple
    stream: ext://sys.stdout
loggers:
  simpleExample:
    level: INFO
    handlers: [console]
    propagate: no
root:
  level: INFO
  handlers: [console]
"""
    LOGGING_CONFIG = yaml.safe_load(LOGGING_CONFIG)

logging.config.dictConfig(LOGGING_CONFIG)

# Telegram Settings
TELEGRAM_TOKEN = GLOBAL_CONFIG.get('TELEGRAM_TOKEN', os.environ['TELEGRAM_TOKEN'])
TELEGRAM_CHAT_ID = GLOBAL_CONFIG.get('TELEGRAM_CHAT_ID', os.environ['TELEGRAM_CHATID'])

# Pops Settings
FUNKO_POP_LIST = GLOBAL_CONFIG.get('FUNKO_POP_LIST')
USER_INFO = GLOBAL_CONFIG.get('USER_INFO')

# Chrome Driver Settings
if get_distro() == "Linux":
    DRIVER_LOCATION = GLOBAL_CONFIG.get('DRIVER_LOCATION', './chromedriver')
elif get_distro() == "Windows":
    DRIVER_LOCATION = GLOBAL_CONFIG.get('DRIVER_LOCATION', './chromedriver.exe')
elif get_distro() == "Darwin":
    DRIVER_LOCATION = GLOBAL_CONFIG.get('DRIVER_LOCATION', '/usr/bin/chromedriver')
