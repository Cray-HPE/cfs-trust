'''
# Copyright 2020 Hewlett Packard Enterprise Development LP

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