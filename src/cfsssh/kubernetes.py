#
# MIT License
#
# (C) Copyright 2020-2022 Hewlett Packard Enterprise Development LP
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

