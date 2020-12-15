#!/usr/bin/env python
#Copyright 2020 Hewlett Packard Enterprise Development LP

'''
This entrypoint is used to determine if this service is still active/alive
from a kubernetes liveness probe perspective.

Created on Dec 15, 2020

@author: jsl
'''

import sys
import logging
import os

from cfsssh.setup.service.liveness import TIMESTAMP_PATH
from cfsssh.setup.service.liveness.timestamp import Timestamp


LOGGER = logging.getLogger('cfsssh.setup.service.liveness')
DEFAULT_LOG_LEVEL = logging.INFO


def setup_logging():
    log_format = "%(asctime)-15s - %(levelname)-7s - %(name)s - %(message)s"
    requested_log_level = os.environ.get('CFS_LOG_LEVEL', DEFAULT_LOG_LEVEL)
    log_level = logging.getLevelName(requested_log_level)
    logging.basicConfig(level=log_level, format=log_format)


if __name__ == '__main__':
    setup_logging()
    timestamp = Timestamp.byref(TIMESTAMP_PATH)
    if timestamp.alive:
        LOGGER.info("%s is considered valid; the application is alive!" , timestamp)
        sys.exit(0)
    else:
        LOGGER.warning("Timestamp is no longer considered valid.")
        sys.exit(1)
