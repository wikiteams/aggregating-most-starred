import sys
import logging
import logging.handlers
import logging.config

DISABLE__STD = False
stargazzers_verbose = False
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


def log(s):
    if stargazzers_verbose:
        logger.info(s)


def say(s):
    print s


def ssay(s):
    if stargazzers_verbose:
        print s
        logger.info(s)


def log_error(s):
    if stargazzers_verbose:
        logger.error(s)
        print s


def log_warning(s):
    if stargazzers_verbose:
        logger.warning(s)
        print s


def log_debug(s):
    if stargazzers_verbose:
        logger.debug(s)


def std_write(s):
    if (stargazzers_verbose) and (not DISABLE__STD):
        sys.stdout.write(s)
        sys.stdout.flush()
