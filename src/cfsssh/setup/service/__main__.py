# Copyright 2020-2022 Hewlett Packard Enterprise Development LP
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
This is a series of instructions used to configure a local copy of sshd so that it
may trust the k8s cluster resident vault client cfs key.

These operations are staging in nature, and should only need to be run once as part
of CFS initialization. It can be safely re-run should the values go missing for whatever
reason, however, if upstream values in vault have changed, there are no guarantees that
newly populated values provided here will work until sometime after the configured
nodes have been rebooted or reconfigured with the new trust.

Created on Nov 2, 2020

@author: jsl
'''

import logging
import sys
import time
import base64
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from kubernetes.client.rest import ApiException
from requests.exceptions import HTTPError

from cfsssh.cloudinit.bss import patch_global_metadata_key, get_global_metadata_key, BSSException
from cfsssh.kubernetes import KubeToken
from cfsssh.connection import requests_retry_session
from cfsssh.vault import VaultClient, VaultSshKey, SshPublicKeyCert, SigningKey
from .values import VAULT_GLOBAL_KEY, VAULT_CLIENT_ROLE
from .values import CFS_KEY_NAME, CFS_PRIVATE_KEY_NAME, CFS_PUBLIC_KEY_NAME, \
    CFS_SIGNED_KEY_NAME, K8S_NAMESPACE, CFS_SIGNED_KEY_NAME_KEY, REFRESH_PERIOD
from cfsssh.setup.service.liveness.timestamp import Timestamp

# Log setup
LOG_LEVEL = logging.DEBUG
lh = logging.StreamHandler(sys.stdout)
lh.setLevel(LOG_LEVEL)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(lh)

#Bootstrapping k8s client
try:
    config.load_incluster_config()
except ConfigException:  # pragma: no cover
    config.load_kube_config()  # Development


def conditionally_populate_bss_trust(public_key, session=None):
    session = session or requests_retry_session()
    defined = True
    try:
        value = get_global_metadata_key(VAULT_GLOBAL_KEY, session)
    except KeyError:
        defined = False
    if defined:
        LOGGER.info("BSS metadata already set for global key '%s'", VAULT_GLOBAL_KEY)
        if value != public_key:
            LOGGER.warning("Public key provided by BSS '%s' does not match expected key '%s'; it will be overwritten.",
                           value, public_key)
        else:
            return
    unset = True
    while unset:
        try:
            patch_global_metadata_key(VAULT_GLOBAL_KEY, public_key, session)
        except BSSException:
            time.sleep(1)
            continue
        unset = False


def run():
    api_version = 'v1'
    kt = KubeToken.from_pod()
    vc = VaultClient(kt.value, VAULT_CLIENT_ROLE)
    sk = SigningKey(vc)
    signing_key_public_key = sk.public_key
    conditionally_populate_bss_trust(signing_key_public_key)

    # Create a vault SSH key for CFS; dynamically creating it if it
    # doesn't yet exist.
    vssh = VaultSshKey.CreateOrReference(CFS_KEY_NAME, vault_client=vc)

    # Store the key halves in kubernetes secrets regardless of if those
    # keys have been populated as secrets before. This should be a no-op
    # if the keys are already created in vault.
    v1 = client.CoreV1Api()
    metadata = {'name': CFS_KEY_NAME, 'namespace': K8S_NAMESPACE}
    data=  {CFS_PUBLIC_KEY_NAME: base64.b64encode(vssh.public_key.strip().encode('utf-8')).decode('utf-8'), 
            CFS_PRIVATE_KEY_NAME: base64.b64encode(vssh.private_key.strip().encode('utf-8')).decode('utf-8')}
    # To decode these values back then:
    #  base64.b64decode(value.encode('utf-8')).decode('utf-8')
    body = client.V1Secret(api_version=api_version, kind='Secret', type='Opaque',
                           metadata=metadata, data=data)
    try:
        v1.create_namespaced_secret(K8S_NAMESPACE, body)
    except ApiException:
        # It already exists, just replace it instead
        v1.replace_namespaced_secret(name=CFS_KEY_NAME, namespace=K8S_NAMESPACE, body=body)
    LOGGER.info("CFS Keypair registered!")
    LOGGER.info("Signing CFS Keypair for authentication.")
    while True:
        LOGGER.info("Signing new certificate...")
        try:
            ssh_pubkey_cert = SshPublicKeyCert(vssh, sk, 'compute', vc,
                                               ttl='12h')
            metadata = {'name': CFS_SIGNED_KEY_NAME, 'namespace': K8S_NAMESPACE}
            data = {CFS_SIGNED_KEY_NAME_KEY: base64.b64encode(ssh_pubkey_cert.signed_key.strip().encode('utf-8')).decode('utf-8')}
        except HTTPError as hpe:
            # When we get an HTTP Error, it means that our vault login token has expired. We need to resign it and try again soon.
            LOGGER.info("Vault credentials have expired:\n\t%s\n creating a new login context and retrying.", hpe)
            vc = VaultClient(kt.value, VAULT_CLIENT_ROLE)
            sk = SigningKey(vc)
            vssh = VaultSshKey.CreateOrReference(CFS_KEY_NAME, vault_client=vc)
            # A small sleep prevents hitting the same API repeatedly in case the 403 issue is transient with how we're reading
            # in credentials, or for other non-403 related HTTPErrors.
            time.sleep(2)
            continue
        body = client.V1Secret(api_version=api_version, kind='Secret', type='Opaque',
                               metadata=metadata, data=data)
        try:
            v1.create_namespaced_secret(K8S_NAMESPACE, body)
        except ApiException:
            LOGGER.info("Replacing expiring certificate...")
            v1.replace_namespaced_secret(name=CFS_SIGNED_KEY_NAME, namespace=K8S_NAMESPACE, body=body)

        # Heal BSS metadata service in case our key has gone missing for whatever reason
        LOGGER.info("Re-patching BSS metadata if needed...")
        conditionally_populate_bss_trust(signing_key_public_key)

        # Wait 6 Hours to refresh our token
        LOGGER.info("Signed secret created; waiting 6 hours to renew.")

        Timestamp()
        time.sleep(REFRESH_PERIOD)

if __name__ == '__main__':
    # We do this once to give indication to the deployment that we're healthy and starting up.
    Timestamp()
    run()
