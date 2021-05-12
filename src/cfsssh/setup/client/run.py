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
The purpose of this package is to bootstrap a trust relationship to the
service half of the cfs-trust domain. In order for trust to be established, a
node must wait for the cluster metadata values to be populated. Then, this
service injects those appropriate values into the local environment (via a file),
injects references to those values into the local SSHD configuration, and then
conditionally reloads the running instance of SSHD to pick up the new configuration.

Created on Nov 2, 2020

@author: jsl
'''

import logging
import sys
import os
import time

from requests.exceptions import RequestException, ConnectionError
from json.decoder import JSONDecodeError

from cfsssh.cloudinit.bss import get_global_metadata_key, BSSException
from cfsssh.setup.client.values import CERTIFICATE_PATH
from cfsssh.sshd import SSHD_CONFIG_PATH, reload
from cfsssh.setup.service.values import VAULT_GLOBAL_KEY

MAX_SLEEP_TIME = 16

LOG_LEVEL = logging.DEBUG
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
lh = logging.StreamHandler(sys.stdout)
lh.setLevel(LOG_LEVEL)
LOGGER.addHandler(lh)


def write_certificate():
    """
    We want to be able to write the key to our known location of CERTIFICATE_PATH,
    but it may not exist yet. When it doesn't exist, we get a key error. Keep trying.
    """
    raw_certificate = None
    sleep_time = 0
    max_sleep = 10
    while not raw_certificate:
        if sleep_time >= max_sleep:
            sleep_time = max_sleep
        try:
            raw_certificate = get_global_metadata_key(VAULT_GLOBAL_KEY)
        except (BSSException, KeyError, RequestException, ConnectionError, JSONDecodeError):
            LOGGER.info("Waiting for metadata service certificate.")
            if sleep_time != MAX_SLEEP_TIME:
                sleep_time += 1
            time.sleep(sleep_time)
    LOGGER.info("Obtained certificate from metadata service.")
    with open(CERTIFICATE_PATH, 'w') as certificate_file:
        certificate_file.write(raw_certificate)
    LOGGER.info("Wrote vault certificate to '%s'.",CERTIFICATE_PATH)

def conditionally_write_certificate():
    """
    Checks for the certificate on the local root filesystem; if its
    there, it does nothing. Otherwise, the key is written to disk.
    """
    if os.path.exists(CERTIFICATE_PATH):
        LOGGER.info("Local certificate exists; skipping.")
        return
    write_certificate()

def configure_sshd():
    """
    The SSHD service may be running, or it may not be. In either case,
    if we end up configuring the service, we need to reload it. This function
    injects necessary values into sshd and then conditionally reloads it.
    """
    expected_entry = 'TrustedUserCAKeys %s' % (CERTIFICATE_PATH)
    with open(SSHD_CONFIG_PATH, 'r') as sshd_config_file:
        sshd_configuration = sshd_config_file.read()
    if expected_entry not in sshd_configuration:
        LOGGER.info("'%s' requires bootstrapping; injecting values.", CERTIFICATE_PATH)
        ssh_configuration = '%s\n\n%s' %(sshd_configuration, expected_entry)
        with open(SSHD_CONFIG_PATH, 'w') as sshd_config_file:
            sshd_config_file.write(ssh_configuration)
    else:
        LOGGER.info("No change in sshd configuration indicated; correct values already exist.")
    reload()
    # There could be a race condition here where our PID snapshot does
    # not capture sshd. The window is small but theoretically possible.
    # We simply reload again to cover it.
    reload()
    LOGGER.info("SSHD now trusts cfstrust certificates.")

def main():
    LOGGER.info("CFS Trust Bootstrapping Setup started.")
    conditionally_write_certificate()
    configure_sshd()
    LOGGER.info("CFS Trust Bootstrapping Setup complete.")
