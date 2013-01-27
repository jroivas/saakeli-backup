#!/usr/bin/env python

import sys
import os
import argparse
import subprocess
import tempfile
import shutil
import hashlib
import tarfile
import datetime

class TempDir:
    def __init__(self):
        self.res = None

    def open(self):
        self.res = tempfile.mkdtemp('_saakeli')
        return self.res

    def close(self):
        if os.path.isdir(self.res):
            shutil.rmtree(self.res)

    def __enter__(self):
        return self.open()

    def __exit__(self, ctype, value, traceback):
        self.close()

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

def client_call(script, remotefile, flags):
    tmp = solve_path(script)
    if tmp is None:
        return None

    try:
        if 'host' in flags:
            return subprocess.check_output([tmp, flags['storage'], remotefile, flags['keyfile'], flags['password'], flags['host']])
        else:
            return subprocess.check_output([tmp, flags['storage'], remotefile, flags['keyfile'], flags['password']])
    except Exception as e:
        print ("Failed: %s" % (e)) 
        return None

def receive_status_file(flags):
    res = client_call('loadfile.sh', 'incremental_status', flags)
    if res is not None and 'Not found' in res:
        return None
    return res

def store_file(flags, fpath):
    return client_call('storefile.sh', fpath, flags)

def update_file(flags, fpath):
    return client_call('updatefile.sh', fpath, flags)

def store_status_file(flags, content, old=None):
    res = 'FAIL'
    with TempDir() as tt:
        fpath = os.path.join(tt, 'incremental_status')
        fd = open(fpath, 'w')
        fd.write(content)
        fd.close()
        if old is None:
            res = store_file(flags, fpath)
        else:
            res = update_file(flags, fpath)
    return res

def get_filelist(srcpath):
    if os.path.isfile(srcpath):
        return [srcpath]
    if not os.path.isdir(srcpath):
        return []
    res = []
    for (path, dirs, files) in os.walk(srcpath):
        for filename in files:
            fname = os.path.join(path, filename)
            res.append(fname)

    return res

def walk_paths(paths):
    res = []
    for path in paths:
        res += get_filelist(path)
    return res

def calc_sha1(fname):
    h = hashlib.sha1()
    fd = None
    try:
        fd = open(fname, 'rb')
        h.update(fd.read())
        ok = True
    except:
        ok = False
    finally:
        if fd is not None:
            fd.close()

    if ok:
        return h.hexdigest()
    return None

def generate_incfile(status):
    f = ''
    for st in status:
        f += '%s %s\n' % st
    return f

def generate_status(files):
    status = []
    for f in files:
        sha1sum = calc_sha1(f)
        status.append((sha1sum, f))
    return status

def create_package(files, tmpname):
    fname = os.path.join(tmpname, 'backup.tar.gz')
    tar = tarfile.open(fname, mode='w:gz')
    for f in files:
        if os.path.isfile(f) or os.path.isdir(f):
            tar.add(f)

    tar.close()
    return fname

def add_file_to_package(tar, filename, old_status):
    if not os.path.isfile(filename):
        return (None, None, 0)

    sha1sum = calc_sha1(filename)
    cnt = 0
    if sha1sum is not None:
        if not sha1sum in old_status.keys():
            print "adding: ", filename
            tar.add(filename)
            cnt += 1
        else:
            print "skipping: ", filename
        return (sha1sum, filename, cnt)

    return (None, None, cnt)

def add_path_to_package(tar, srcpath, old_status):
    status = []
    cnt = 0
    if os.path.isdir(srcpath):
        for (path, dirs, files) in os.walk(srcpath):
            for filename in files:
                fname = os.path.join(path, filename)
                res = add_file_to_package(tar, fname, old_status)
                if res[0] is not None:
                    status.append(res[:2])
                    cnt += res[2]
    return (status, cnt)

def create_package_and_status(paths, tmpdir, old_status):
    if not paths:
        return (None, None)

    if not old_status:
        postfix = '_full'
    else:
        postfix = '_inc'

    tmp = datetime.datetime.now()
    datestamp = '%.4d%.2d%.2d-%.2d%.2d%.2d' % (tmp.year, tmp.month, tmp.day, tmp.hour, tmp.minute, tmp.second)

    fname = os.path.join(tmpdir, 'backup%s-%s.tar.gz' % (postfix, datestamp))
    status = []
    cnt = 0
    try:
        tar = tarfile.open(fname, mode='w:gz')

        for srcpath in paths:
            if os.path.isfile(srcpath):
                res = add_file_to_package(tar, srcpath, old_status)
                if res[0] is not None:
                    status.append(res[:2])
                    cnt += res[2]
            if os.path.isdir(srcpath):
                res = add_path_to_package(tar, srcpath, old_status)
                status += res[0]
                cnt += res[1]
                #status += add_path_to_package(tar, srcpath, old_status)

        tar.close()
    except tarfile.TarError:
        print ('Error creating tar file!')
        return (None, None, 0)

    return (fname, status, cnt)
    #filelist = walk_paths(flags['path'])
    #(tmpobj, tmpdir) = get_temp()
    #status = generate_status(filelist)
    #incdata = generate_incfile(status)

def parse_status(status):
    res = {}
    if status is None:
        return res
    statuses = status.split('\n')
    for line in statuses:
        tmp = line.split()
        if len(tmp) >= 2:
            a = tmp[0].strip()
            b = (' '.join(tmp[1:])).strip()
            res[a] = b
            #res.append((a, b))
    return res

def get_temp():
    tmp = TempDir()
    tmpname = tmp.open()        
    return (tmp, tmpname)

def close_temp(tmp):
    tmp.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Incremental backup')
    parser.add_argument('-P', '--path', required=True, default=[], action='append', help='Define a path or file to backup')
    parser.add_argument('--host', action='store', help='Saakeli-backup server URL')
    parser.add_argument('--storage', action='store', required=True, help='Digest name')
    parser.add_argument('--password', action='store', required=True, help='Password for saakeli-server')
    parser.add_argument('--keyfile', action='store', required=True, help='Keyfile to use for symmetric encryption before sending file')
    parser.add_argument('-f', '--full', default=False, action='store_true', help='Make full backup')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Verbosal output')
    #parser.add_argument('-i', '--incremental', default=True, action='store_false', help='Make incremental backup')
    args = parser.parse_args()
    flags = vars(args)

    status_res = receive_status_file(flags)
    old_status = parse_status(status_res)
    full_backup = flags['full']
    if status_res is None:
        full_backup = True
    if full_backup:
        old_status = {}

    ok = False
    res = 'fail'
    res2 = 'fail'
    with TempDir() as tmpdir:
        #pack = create_package(filelist, tmpdir)
        (pack, status, cnt) = create_package_and_status(flags['path'], tmpdir, old_status)
        if pack is not None:
            if cnt == 0:
                print ('Files not changed, skipping')
            else:
                incdata = generate_incfile(status)
                res = store_file(flags, pack)
                res2 = store_status_file(flags, incdata, status_res)
                print res
                print res2
