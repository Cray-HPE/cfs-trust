# Copyright 2021 Hewlett Packard Enterprise Development LP
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