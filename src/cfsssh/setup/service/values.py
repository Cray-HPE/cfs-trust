'''
Created on Nov 17, 2020

@author: jsl
'''

VAULT_GLOBAL_KEY = 'cfs_public_key'
VAULT_SIGNING_KEY_NAME = 'ssh_user_certs_compute'
VAULT_CLIENT_ROLE = 'ssh-user-certs-compute'

CFS_KEY_NAME = 'cfstrust'
CFS_PRIVATE_KEY_NAME = 'private'
CFS_PUBLIC_KEY_NAME = 'public'

CFS_SIGNED_KEY_NAME = 'cfstrustcertificate'
CFS_SIGNED_KEY_NAME_KEY = 'certificate'

K8S_NAMESPACE = 'services'
REFRESH_PERIOD = 60*60*6