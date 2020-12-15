# Copyright 2020 Hewlett Packard Enterprise Development LP

"""
Obtaining information from a k8s cluster.
"""

from cfsssh.context import in_cluster


class KubeToken(object):
    """
    A Kube Token is a string representing an authentication string; it is exposed
    in various locations within the management plane.
    """
    @classmethod
    def from_pod(cls):
        """
        A KubeToken is automatically injected into running pods; it can be obtained
        by simply reading the associated file.
        """
        self = cls.__new__(cls)
        if in_cluster():
            with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as token_file:
                self.value = token_file.read().strip()
        else:
            raise ValueError("KubeToken cannot be obtained using this method")
        return self

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)

