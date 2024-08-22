#
# MIT License
#
# (C) Copyright 2020-2022, 2024 Hewlett Packard Enterprise Development LP
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
The purpose of this module is to provide a unified way of creating or
updating a requests retry connection whenever interacting with a
microservice; these connections are exposed as a requests session
with an HTTP retry adapter attached to it.

Created on Nov 2, 2020

@author: jsl
'''

import logging

from cfsssh.requests_retry_session import requests_retry_session as base_requests_retry_session

LOGGER = logging.getLogger(__name__)
PROTOCOL = 'http'

def requests_retry_session(retries=128, backoff_factor=0.01, **kwargs):
    return base_requests_retry_session(protocol=PROTOCOL,
                                       retries=retries,
                                       backoff_factor=backoff_factor,
                                       **kwargs)


if __name__ == '__main__':
    import sys
    lh = logging.StreamHandler(sys.stdout)
    lh.setLevel(logging.DEBUG)
    LOGGER.addHandler(lh)
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.info("Running")
    retry_session = requests_retry_session()
    LOGGER.info(retry_session.get('https://httpstat.us/200').status_code)
    retry_session = requests_retry_session(retries=5)
    LOGGER.info(retry_session.get('https://httpstat.us/503').status_code)
