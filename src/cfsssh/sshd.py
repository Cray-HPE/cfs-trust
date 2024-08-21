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
A collection of routines used to interact with an sshd instance (locally).

Created on Nov 19, 2020

@author: jsl
'''

import os
import subprocess

SSHD_PATH = '/usr/sbin/sshd'
SSHD_CONFIG_PATH = '/etc/ssh/sshd_config'


def is_running():
    """
    Examines the list of PIDs to determine if sshd is running.
    If it is running, return True, otherwise False.
    """
    pids = get_sshd_pids()
    return bool(pids)


def reload(pid=None):
    """
    Reloads a running sshd to pick up new values.
    """
    for pid in get_sshd_pids():
        subprocess.check_call(['kill', '-HUP', pid])


def get_sshd_pids():
    """
    Examines the running system for SSHD's process id and returns it as a string.
    """
    sshd_pids = []
    for pid in [pid for pid in os.listdir('/proc') if pid.isdigit()]:

        try:
            with open('/proc/%s/cmdline' %(pid), 'r') as cmdfile:
                if SSHD_PATH in cmdfile.read():
                    sshd_pids.append(pid)
        except IOError: # proc has already terminated
            continue
    return sshd_pids

if __name__ == '__main__':
    reload()