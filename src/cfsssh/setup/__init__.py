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
This is a series of instructions used to configure a local copy of sshd so that it
may trust the upstream vault client instance. This setup procedure involves pulling
the public_key from the vault service, injecting a value into sshd config, and then
optionally reloading the sshd service to pick up the new values.

This is considered a one-time setup operation, intended primarily to be exercised
with low frequency for diskful and ephemerally provisioned root filesystems; the
goal is to be as nice as possible to the vault instance until we can scale this
up at a later point in time for a more dynamic credentialing workflow.

There are two primary intended entrypoints for this script:
- Diskful NCNs (systemd service)
- Diskless nodes provisioned with CFS (IMS/CFS imageroot bootstrapping, primary consumer)

Created on Nov 2, 2020

@author: jsl
'''