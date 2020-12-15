# Copyright 2020 Hewlett Packard Enterprise Development LP

import subprocess
import requests
import json
import os
import tempfile
from requests.exceptions import HTTPError

from cfsssh.context import in_cluster

VAULT_SERVICE_ENDPOINT_CLUSTER = 'http://cray-vault.vault:8200'
VAULT_SERVICE_ENDPOINT_EXTERNAL = 'https://api-gw-service-nmn.local/apis/vault'
VAULT_VERSION = 'v1'

"""
# kubectl run test --namespace services --rm -i --tty --image alpine:3.7
 
/ # apk add jq curl openssh-client 
 
# Get auth token
 
/ # KUBE_TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
/ # VAULT_TOKEN=$(curl -s --request POST --data '{"jwt": "'"$KUBE_TOKEN"'", "role": "cfsssh-user-certs-compute"}' http://cray-vault.vault:8200/v1/auth/kubernetes/login | jq -r '.auth.client_token')
 
# Create exportable key
/ # curl --header "X-Vault-Token: $VAULT_TOKEN" --request POST --data '{"type": "ecdsa-p384", "exportable": true}' http://cray-vault.vault:8200/v1/transit/keys/ecdsa-p384-compute-cfsssh-key
/ # curl --header "X-Vault-Token: $VAULT_TOKEN"  --request LIST http://cray-vault.vault:8200/v1/transit/keys | jq
 
# Export private key
/ # curl --header "X-Vault-Token: $VAULT_TOKEN"  http://cray-vault.vault:8200/v1/transit/export/signing-key/ecdsa-p384-compute-cfsssh-key | jq '.data.keys["1"]' | sed -e 's/"//g' -e 's/\\n/\n/g' > id_ecdsa
 
# Extract the public key from the private and covert to SSH format
/ # chmod 600 id_ecdsa
/ # cfsssh-keygen -y -f id_ecdsa > id_ecdsa.pub
 
# Sign the public key/create the cert
/ # curl --header "X-Vault-Token: $VAULT_TOKEN" --request POST --data '{"public_key" : "'"$(tr -d '\n' < id_ecdsa.pub)"'", "ttl": "87600h", "valid_principals": "root", "key_id": "compute node root"}'  http://cray-vault.vault:8200/v1/ssh_user_certs_compute/sign/compute| jq '.data.signed_key' | sed -e 's/"//g' -e 's/\\n//g' > id_ecdsa-cert.pub
 
# Show the resulting certificate 
/ # cfsssh-keygen -Lf id_ecdsa-cert.pub 
"""

class VaultClient(object):
    """
    A VaultToken can be obtained by logging into an established vault instance with a provided JWT.
    and a role.
    """
    def __init__(self, jwt, role):
        """
        Creates a new vault token by logging in.
        """
        self.jwt = jwt
        self.role = role
        self.in_cluster = in_cluster()

        # Cacheable Properties
        self._base_endpoint = None
        self._token_payload = None
        self._login_endpoint = None
        self._token = None
        self._token_header = None

    @property
    def base_endpoint(self):
        if self._base_endpoint:
            return self._base_endpoint
        if in_cluster():
            self._base_endpoint = '%s/%s' %(VAULT_SERVICE_ENDPOINT_CLUSTER, VAULT_VERSION)
        else:
            self._base_endpoint = '%s/%s' %(VAULT_SERVICE_ENDPOINT_EXTERNAL, VAULT_VERSION)
        return self._base_endpoint

    @property
    def login_endpoint(self):
        if self._login_endpoint:
            return self._login_endpoint
        self._login_endpoint = '%s/auth/kubernetes/login' %(self.base_endpoint)
        return self._login_endpoint

    @property
    def token_payload(self):
        if self._token_payload:
            return self._token_payload
        self._token_payload = {'jwt': self.jwt, 'role': self.role}
        return self._token_payload

    @property
    def token(self):
        """
        Creates a vault token by requesting one using the provided jwt and role. Upon first
        access, a token is cached for subsequent use.
        """
        if self._token:
            return self._token
        response = requests.post(self.login_endpoint, json=self.token_payload)
        response.raise_for_status()
        json_obj = json.loads(response.text)
        self._token = json_obj['auth']['client_token']
        return self._token

    @property
    def token_header(self):
        """
        A dictionary to use with subsequent calls into Vault.
        """
        if self._token_header:
            return self._token_header
        self._token_header = {'X-Vault-Token': self.token}
        return self._token_header


class SigningKey(object):
    """
    A signing key is provided by vault configuration and is required to configure client nodes;
    nodes with the public key are 'hosts', using the vault documentation parlance. That means, a
    host must have the public half and the trusted CA from the vault provided SigningKey
    for any other agent process to authenticate to them.

    However, getting this information and making it available to downstream nodes can present
    a bit of a challenge, as not all nodes have a direct authentication mechanism. For this reason,
    it may make the most sense for a one-time setup operation to expose this publicly available
    information and expose it for consumption.
    """
    def __init__(self, vault_client, name='ssh_user_certs_compute'):
        self.name = name
        self.vault_client = vault_client

        # Cacheables
        self._endpoint = None

    @property
    def endpoint(self):
        if self._endpoint:
            return self._endpoint
        self._endpoint = '%s/%s' % (self.vault_client.base_endpoint, self.name)
        return self._endpoint

    @property
    def public_key(self):
        uri = '%s/public_key' %(self.endpoint)
        # This is an unauthenticated endpoint, no need for a vault client authentication token
        response = requests.get(uri)
        response.raise_for_status()
        return response.text

    @property
    def trusted_user_ca_key(self):
        uri = '%s/config/ca' %(self.endpoint)
        response = requests.get(uri, headers=self.vault_client.token_header)
        return response

    def write_local_public_key(self, destination):
        """
        Opens <destination>, writes the contents of the key to disk.
        """
        with open(destination, 'w') as dest_file:
            dest_file.write(self.public_key)
        os.chmod(destination, 0o600)

class VaultSshKey(object):
    """
    This is the representation of an SSH key, as created by a vault instance. This is a client binding
    for keys that are stateful to the vault API, although we do expose additional methods that allow for
    the creation of local file artifacts where necessary.
    """
    def __init__(self, name, vault_client, key_type="ecdsa-p384", exportable=True):
        self.name = name
        self.vault_client = vault_client
        self.key_type = key_type
        self.exportable = exportable

        # Cached Attributes
        self._creation_endpoint = None
        self._signing_endpoint = None
        self._endpoint = None

    @staticmethod
    def defined(transit_key, vault_client):
        """
        Queries the vault API for the existence of a known specific transport key through a get
        operation. If the endpoint exists, then it is defined and we return true; otherwise
        false.
        """
        resource_uri = '%s/transit/keys/%s' %(vault_client.base_endpoint, transit_key)
        response = requests.get(resource_uri, headers=vault_client.token_header)
        try:
            response.raise_for_status()
            return True
        except HTTPError:
            return False

    @classmethod
    def Create(cls, name, *args, **kwargs):
        """
        Initilizes a new VaultSSHKey record and creates it using Vault.
        """
        self = cls(name, *args, **kwargs)
        response = requests.post(self.creation_endpoint, headers=self.vault_client.token_header,
                                 json={'type': self.key_type, 'exportable': self.exportable})
        response.raise_for_status()
        return self

    @property
    def creation_endpoint(self):
        #http://cray-vault.vault:8200/v1/transit/keys/
        if self._creation_endpoint:
            return self._creation_endpoint
        self._creation_endpoint = '%s/transit/keys/%s' %(self.vault_client.base_endpoint, self.name)
        return self._creation_endpoint

    @classmethod
    def Reference(cls, name, *args, **kwargs):
        """
        Create a new reference to a VaultSshKey without creating it.
        """
        self = cls(name, *args, **kwargs)
        return self

    @classmethod
    def CreateOrReference(cls, name, vault_client, *args, **kwargs):
        """
        Create a named transport key in vault; if it already exists, simply
        re-use it.
        """
        if not cls.defined(name, vault_client):
            return cls.Create(name, vault_client=vault_client, *args, **kwargs)
        else:
            return cls.Reference(name, vault_client=vault_client, *args, **kwargs)

    @property
    def endpoint(self):
        if self._endpoint:
            return self._endpoint
        self._endpoint = '%s/%s' % (self.creation_endpoint, self.name)

    @property
    def signing_endpoint(self):
        #http://cray-vault.vault:8200/v1/transit/export/signing-key/ecdsa-p384-compute-cfsssh-key
        if self._signing_endpoint:
            return self._signing_endpoint
        self._signing_endpoint = '%s/%s/%s' %(self.vault_client.base_endpoint, 'transit/export/signing-key', self.name)
        return self._signing_endpoint

    @property
    def private_key(self):
        """
        Returns a string representing the private key.
        """
        #curl --header "X-Vault-Token: $VAULT_TOKEN"  http://cray-vault.vault:8200/v1/transit/export/signing-key/ecdsa-p384-compute-cfsssh-key | jq '.data.keys["1"]' | sed -e 's/"//g' -e 's/\\n/\n/g' > id_ecdsa
        response = requests.get(self.signing_endpoint, headers=self.vault_client.token_header)
        response.raise_for_status()
        values = json.loads(response.text)
        return values['data']['keys']["1"]

    def export_private_key(self, destination=None):
        """
        Saves a private copy of the cfsssh key locally to <destination>.

        Returns <destination>, which is where the key was written to.
        
        WARNING: If you write this file to disk, you are responsible for cleaning it up and ensuring
        that it is cleaned up.
        """
        if not destination:
            destination = tempfile.NamedTemporaryFile(prefix=self.name, suffix='_key', delete=True).name
        with open(destination, 'w') as local_private_key:
            # Secure it
            os.chmod(destination, 0o600)
            local_private_key.write(self.private_key)
        return destination

    @property
    def public_key(self):
        """
        The public half of this key.
        """
        try:
            private_key_path = self.export_private_key()
            proc = subprocess.Popen(['ssh-keygen', '-y', '-f', private_key_path], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            out, _ = proc.communicate()
            return out.decode('utf-8')
        finally:
            if os.path.exists(private_key_path):
                os.unlink(private_key_path)

    def export_public_key(self, destination=None):
        """
        Writes the public half of the certificate to disk.
        """
        if not destination:
            destination = tempfile.NamedTemporaryFile(prefix=self.name, suffix='_key.pub', delete=True).name
        with open(destination, 'w') as local_public_key:
            # Secure it
            os.chmod(destination, 0o600)
            local_public_key.write(self.public_key)


class SshPublicKeyCert(object):
    """
    Creates a signed public key/certificate from a locally available SshPublicKey.

    When a public key is signed using a known upstream Vault SSH Key, all environments that
    trust the public half of the parent key also trust the signed public key.

    vault_ssh_key: An instance of VaultSshKey
    role_name: The name of the role to use to sign the key
    signing_key: A SigningKey Instance

    API Documentation:
        https://www.vaultproject.io/api/secret/cfsssh#sign-cfsssh-key
    """
    def __init__(self, 
                 vault_ssh_key,
                 signing_key,
                 role_name,
                 vault_client,
                 ttl='87600h', valid_principals='root', key_id='compute node root'):
        self.vault_ssh_key = vault_ssh_key
        self.signing_key = signing_key
        self.role_name = role_name
        self.vault_client = vault_client
        self.ttl = ttl
        self.valid_principals = valid_principals
        self.key_id = key_id
        # / # curl --header "X-Vault-Token: $VAULT_TOKEN" --request POST --data '{"public_key" : "'"$(tr -d '\n' < id_ecdsa.pub)"'", "ttl": "87600h", "valid_principals": "root", "key_id": "compute node root"}'  http://cray-vault.vault:8200/v1/ssh_user_certs_compute/sign/compute| jq '.data.signed_key' | sed -e 's/"//g' -e 's/\\n//g' > id_ecdsa-cert.pub

        # Cachable properties
        self._signing_endpoint = None
        self._pubkey_value = None
        self._value = None

    @property
    def signing_endpoint(self):
        """
        The service location we look to in order to sign a locally available public key
        with a known upstream key already in vault.
        """
        # http://cray-vault.vault:8200/v1/ssh_user_certs_compute/sign/compute
        if self._signing_endpoint:
            return self._signing_endpoint
        else:
            self._signing_endpoint = '%s/%s/sign/%s' %(self.vault_client.base_endpoint, self.signing_key.name, self.role_name)
        return self._signing_endpoint

    @property
    def value(self):
        """
        Calls the vault endpoint to sign a public key. Returns all values; caches them for reference.
        """
        if self._value:
            return self._value
        payload = {'public_key': str(self.vault_ssh_key.public_key)}
        for attribute in ('valid_principals', 'ttl', 'key_id'):
            if getattr(self, attribute):
                payload[attribute] = getattr(self, attribute)
        response = requests.post(self.signing_endpoint, json=payload, headers=self.vault_client.token_header)
        response.raise_for_status()
        self._value = json.loads(response.text)
        return self._value

    @property
    def signed_key(self):
        return self.value['data']['signed_key']

    def write_certificate(self, destination=None):
        """
        Creates a signed certificate at destination.
        """
        destination = destination or tempfile.NamedTemporaryFile(prefix=self.role_name,
                                                                 suffix='id_ecdsa-cert.pub',
                                                                 delete=True).name
        with open(destination, 'w') as certificate_file:
            certificate_file.write(self.signed_key)
        os.chmod(destination, 0o640)
        return destination




if __name__ == '__main__':
    pass
"""
from cfsssh.vault import VaultClient, VaultSshKey, SshPublicKeyCert, SigningKey
from cfsssh.kubernetes import KubeToken
kt = KubeToken.from_pod()
vc = VaultClient(kt.value, 'cfsssh-user-certs-compute')
signing_key = SigningKey(vc)

# Client Workflow
print("Public Cert: %s" %(signing_key.public_key))

# Granting Workflow for keys
vssh = VaultSshKey.CreateOrReference('bar', vault_client=vc)
vssh.export_private_key('/root/id_ecdsa')
vssh.export_public_key('/root/id_ecdsa.pub')
ssh_pubkey_cert = SshPublicKeyCert(vssh, signing_key, 'compute', vc)
ssh_pubkey_cert.write_certificate('/root/id_ecdsa-cert.pub')


"""