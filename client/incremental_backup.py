#!/usr/bin/env python

import sys
import os
import argparse
import subprocess

def solve_path(script):
    mypath = os.path.dirname(__file__)

    tmp = os.path.join(mypath, script)
    if os.path.isfile(tmp):
        return tmp

    testpaths = [ '..', '../client' ]

    for path in testpaths:
        tmp = os.path.join(mypath, path, script)
        if os.path.isfile(tmp):
            return tmp

    return None

def client_call(script, flags):
    tmp = solve_path(script)
    if tmp is None:
        return None

    if 'host' in flags:
        return subprocess.check_output([tmp, flags['storage'], flags['keyfile'], flags['password'], flags['host']])
    else:
        return subprocess.check_output([tmp, flags['storage'], flags['keyfile'], flags['password']])

def receive_status_file(flags):
    client_call('loadfile.sh', flags)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Incremental backup')
    parser.add_argument('-P', '--path', required=True, default=[], action='append', help='Define a path or file to backup')
    parser.add_argument('--host', action='store', help='Saakeli-backup server URL')
    parser.add_argument('--storage', action='store', required=True, help='Digest name')
    parser.add_argument('--password', action='store', required=True, help='Password for saakeli-server')
    parser.add_argument('--keyfile', action='store', required=True, help='Keyfile to use for symmetric encryption before sending file')
    parser.add_argument('-i', '--incremental', default=False, action='store_true', help='Make incremental backup')
    args = parser.parse_args()
    flags = vars(args)
    print flags
    #main()
