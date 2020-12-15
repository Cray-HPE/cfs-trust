# Copyright 2020 Hewlett Packard Enterprise Development LP

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