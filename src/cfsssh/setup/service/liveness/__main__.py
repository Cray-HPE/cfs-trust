#!/usr/bin/env python
#
# MIT License
#
# (C) Copyright 2020-2022 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
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
    timestamp = Timestamp.byref(path=TIMESTAMP_PATH)
    if timestamp.alive:
        LOGGER.info("%s is considered valid; the application is alive!" , timestamp)
        sys.exit(0)
    else:
        LOGGER.warning("Timestamp is no longer considered valid.")
        sys.exit(1)
