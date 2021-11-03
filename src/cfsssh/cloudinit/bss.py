# Copyright 2020-2021 Hewlett Packard Enterprise Development LP
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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# (MIT License)

'''
Created on Nov 17, 2020

@author: jsl
'''

import json
from cfsssh.connection import requests_retry_session
from cfsssh.context import in_cluster

BOOT_PARAM_SUFFIX = 'boot/v1/bootparameters'
METADATA_SUFFIX = 'meta-data'
if in_cluster():
    PROTOCOL = 'http'
    DNS_NAME = 'cray-bss'
    SERVICE_ENDPOINT = '%s://%s' %(PROTOCOL, DNS_NAME)
    PARAMETERS_ENDPOINT = '%s://%s/%s' % (PROTOCOL, DNS_NAME, BOOT_PARAM_SUFFIX)
    METADATA_ENDPOINT = '%s/%s' % (SERVICE_ENDPOINT, METADATA_SUFFIX)
else:
    PROTOCOL = 'http'
    DNS_NAME = 'api-gw-service-nmn.local'
    PARAMETERS_ENDPOINT = '%s://%s/%s' % (PROTOCOL, DNS_NAME, BOOT_PARAM_SUFFIX)
    METADATA_ENDPOINT = '%s://%s:8888/%s' %(PROTOCOL, DNS_NAME, METADATA_SUFFIX)

class BSSException(Exception):
    """
    Anything goes wrong here during interaction with BSS, we raise this exception.
    This allows us a clean way to retry these interactions.
    """

def get_global_metadata_key(key, session=None):
    session = session or requests_retry_session()
    get_payload = {'key': 'Global.%s' %(key)}
    response = session.get(METADATA_ENDPOINT, json=get_payload)
    try:
        response.raise_for_status()
    except Exception as exc:
        raise BSSException(exc) from exc
    obj = json.loads(response.text)
    # This will raise a key error if it isn't defined!
    return obj['Global'][key]

def put_global_metadata_key(key, value, session=None):
    session = session or requests_retry_session()
    put_payload = {"hosts" : ["Global"], 'cloud-init': {'meta-data': {key: value}}}
    response = session.put(PARAMETERS_ENDPOINT, json=put_payload)
    try:
        response.raise_for_status()
    except Exception as exc:
        raise BSSException(exc) from exc
