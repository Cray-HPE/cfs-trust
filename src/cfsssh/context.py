# Copyright 2020 Hewlett Packard Enterprise Development LP

"""
This module provides lookup functionality for determining where code is being
executed; this is useful for when default values are not provided during code
execution.

Where possible, be explicit and not use these.
"""

import os

def in_cluster():
    """
    Returns True if the current running context is within a k8s pod as part of a cluster.
    """
    return "KUBERNETES_SERVICE_HOST" in os.environ
