# setup.py for cfsssh-setup
# Copyright 2020 Hewlett Packard Enterprise Development LP
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read().strip()

with open(".version", "r") as fh:
    version_str = fh.read().strip()

package_dir = {'cfsssh':                        'src/cfsssh',
               'cfsssh.cloudinit':              'src/cfsssh/cloudinit',
               'cfsssh.setup':                  'src/cfsssh/setup',
               'cfsssh.setup.service':          'src/cfsssh/setup/service',
               'cfsssh.setup.service.liveness': 'src/cfsssh/setup/service/liveness',
               'cfsssh.setup.client':           'src/cfsssh/setup/client',}

setuptools.setup(
    name="cfs-ssh-trust",
    version=version_str,
    author="HPE Development LP",
    author_email="sps@cray.com",
    description="CFS Trust Setup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://stash.us.cray.com/projects/SCMS/repos/cfs-trust/browse",
    package_dir = package_dir,
    packages = list(package_dir.keys()),
    keywords="vault ssh cfs kubernetes trust certificates",
    classifiers=(
        "Programming Language :: Python :: 3.8",
        "License :: Other/Proprietary License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ),
)
