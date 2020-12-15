'''
# Copyright 2020 Hewlett Packard Enterprise Development LP

This is a QOL entrypoint to the cfsssh.setup.client module. It only
imports content from run so that this is possible:
  > python3 -m cfsssh.setup.client

Created on Nov 2, 2020

@author: jsl
'''

from cfsssh.setup.client.run import main

if __name__ == '__main__':
    main()
