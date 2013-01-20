#!/usr/bin/env python

import sys
import os
import base64

def gen_key():
    data = os.urandom(128)
    return base64.b64encode(data)

if __name__ == '__main__':
    print gen_key()
