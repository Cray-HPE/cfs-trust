# Copyright 2020 Hewlett Packard Enterprise Development LP

'''
A set of routines for creating or reading from an existing timestamp file.
Created on Dec 15, 2020

@author: jsl
'''

from datetime import timedelta

from liveness.timestamp import Timestamp as BaseTimestamp
from cfsssh.setup.service.values import REFRESH_PERIOD

class Timestamp(BaseTimestamp):
    @property
    def max_age(self):
        """
        The maximum amount of time that can elapse before we consider the timestamp
        as invalid.

        This value is returned as a timedelta object.
        """
        computation_time = timedelta(seconds=REFRESH_PERIOD+120)
        # That is, we expect a new timestamp at at least 2 minutes after the cert is resigned
        return computation_time
