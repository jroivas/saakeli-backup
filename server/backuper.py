#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import Response
from werkzeug import secure_filename
import os
import uuid
import hashlib

app = Flask(__name__)

app.config['STORAGE'] = './store'

@app.route('/')
def index():
    res = """<html>
    <head>
        <title>Backup server</title>
        <style>
        div {
            margin-bottom: 1em;
        }
        pre {
            padding-left: 1em;
        }
        </style>
    </head>

    <body>
        <h1>Backup server</h1>

        <div>Provides simple API to load and store files.
        </div>

        <h2>Storing</h2>
        <div>Storing files may be done with GET or POST:
        <pre>POST: https://host:port/store/DIGEST
POST: https://host:port/store
GET : https://host:port/store/DIGEST?filename=FILENAME&data=CONTENTS</pre>
        In POST method, when providing "filename" in form and contents as multipart data "filedata".
        If not providing DIGEST in url, POST must be used and provide "digest" key in form data.
        </div>

        <h2>Retrieving files</h2>
        <div>Similar way retrieving files happend with GET or POST:
        <pre>POST: https://host:port/load/DIGEST/VERIFY/FILENAME
GET : https://host:port/load/DIGEST/VERIFY/FILENAME?challenge=CHALLENGE</pre>
        In case of POST, key "challenge" must be provided in form data.
        </div>

        <h2>Updating files</h2>
        <div>One may update files with GET or POST:
        <pre>POST: https://host:port/update/DIGEST/VERIFY/FILENAME
GET : https://host:port/update/DIGEST/VERIFY/FILENAME?data=CONTENTS&challenge=CHALLENGE</pre>
        In case of POST, key "challenge" must be provided in form data.
        </div>

        <h2>Get public URL for files</h2>
        <div>One may update files with GET or POST:
        <pre>POST: https://host:port/public/DIGEST/VERIFY/FILENAME
GET : https://host:port/public/DIGEST/VERIFY/FILENAME?data=CONTENTS&challenge=CHALLENGE</pre>
        In case of POST, key "challenge" must be provided in form data.

        Will return URL for public access.
        </div>

        <h2>Deleting files</h2>
        <div>One may update files with POST only:
        <pre>POST: https://host:port/remove/DIGEST/VERIFY/FILENAME</pre>
        Key "challenge" must be provided in form data.

        This will return a confirmation request formatted as:
        <pre>CONFIRM xxxx</pre>

        Where xxxx is a key. You must perform a new query with same data,
        but now with "confirm=xxxx" in form data.
        As extra verify, your challenge MUST NOT be same as in first query.
        </div>


        <h2>Authentication</h2>
        <div>Authentication consists few schemes:
<pre>DIGEST    = Digest value of target folder, identifies the target resource
CHALLENGE = Random challenge for authentication, generated by client
VERIFY    = SHA256(PASSKEY + CHALLENGE)
</pre>
        This means that DIGEST and PASSKEY are needed on server side.
        Challenge is provided either in POST form data or in url in GET scheme.
        It's always recommended to use POST scheme if possible.
        </div>

        <h2>Return codes</h2>
        <div>
        Valid return codes:
        <pre>OK xxxx    = File stored, accessible name 'xxxx'
401        = Error occured (failed credentials, digest, etc.)
404        = Failed to perform the action, file not found, etc.
DELETED xx = Deleted file named 'xx'
CONFIRM xx = Confirm deletion by providing 'xx' back to server
</pre>
        </div>

    </body>
</html>
    """
    return res

def error_auth():
    return Response('Unauthorized', status=401)

def error_found():
    return Response('Not found', status=404)

def verify_challenge(challenge, verify, passwd):
    if not challenge or len(challenge) < 8:
        return False

    h = hashlib.sha256()
    mysum = passwd + challenge
    h.update(mysum)
    mysum = h.hexdigest()
    return (mysum == verify)

def validate_digest(digest, challenge=None, verify=None):
    if digest is None or not digest:
        return False
    if digest[0] == '.':
        return False

    folders = os.listdir(app.config['STORAGE'])
    if not digest in folders:
        return False

    if challenge is not None and verify is not None:
        passfile = os.path.join(app.config['STORAGE'], digest, '.pass')
        if not os.path.isfile(passfile):
            return False
        fd = open(passfile, 'r')
        res = fd.read()
        fd.close()
        res = res.strip()
        return verify_challenge(challenge, verify, res)

    return True

def unique_name(digest, fname):
    fname = secure_filename(fname)
    fpath = os.path.join(app.config['STORAGE'], digest, fname)
    index = 1
    tmp = fpath
    while os.path.exists(tmp):
        tmp = fpath + '%s' % (index)
        index += 1
    return tmp

def form_name(digest, fname):
    if fname is None or not fname:
        return None
    if fname[0] == '.':
        return None

    fname = secure_filename(fname)
    fpath = os.path.join(app.config['STORAGE'], digest, fname)
    if os.path.isfile(fpath):
        return fpath

    return None

def solve_challenge():
    challenge = None
    if request.method == 'POST':
        if 'challenge' in request.form:
            challenge = request.form['challenge']
    else:
        challenge = request.args.get('challenge', None)

    return challenge

@app.route('/load/<digest>/<verify>/<key>', methods=['GET', 'POST'])
def load(digest, verify, key):
    challenge = solve_challenge()

    ok = validate_digest(digest, challenge, verify)
    if not ok:
        return error_auth()

    if not key:
        return error_auth()

    if key[0] == '.':
        return error_found()

    fname = form_name(digest, key) 
    if fname is None:
        return error_found()
        
    fd = None
    try:
        fd = open(fname, 'r')
        res = fd.read()
    except:
        return error_found()
    finally:
        if fd is not None:
            fd.close()
    return Response(res, mimetype='application/octet-stream')

@app.route('/update/<digest>/<verify>/<key>', methods=['GET', 'POST'])
def update(digest, verify, key):
    challenge = solve_challenge()

    ok = validate_digest(digest, challenge, verify)
    if not ok:
        return error_auth()

    if not key:
        return error_auth()

    if key[0] == '.':
        return error_found()

    fname = form_name(digest, key) 
    if fname is None:
        return error_found()
        
    if request.method == 'POST':
        if not 'filedata' in request.files:
            return error_found()
        f = request.files['filedata']
        if f:
            f.save(fname)
            res = True
        else:
            res = False
    else:
        data = request.args.get('data', '')
        if data:
            res = write_file(fname, data)

    index = os.path.basename(fname)
    if res:
        return 'OK %s' % (index)
    else:
        return error_found()

@app.route('/get/<digest>/<key>', methods=['GET', 'POST'])
@app.route('/get/<digest>/<key>/<anything>', methods=['GET', 'POST'])
def get(digest, key, anything=None):
    if digest is None or key is None or not digest or not key:
        return error_found()

    publicfile = os.path.join(app.config['STORAGE'], digest, '.public_%s' % (key))
    if not os.path.isfile(publicfile):
        return error_found()

    try:
        fd = open(publicfile, 'r')
        destfile = fd.read()
        fd.close()
        destfile = destfile.strip()

        if os.path.isfile(destfile):
            fd = open(destfile, 'r')
            res = fd.read()
            fd.close()
            return Response(res, mimetype='application/octet-stream')
    except:
        pass

    return error_found()

@app.route('/public/<digest>/<verify>/<key>', methods=['GET', 'POST'])
def public(digest, verify, key):
    challenge = solve_challenge()

    ok = validate_digest(digest, challenge, verify)
    if not ok:
        return error_auth()

    if not key:
        return error_auth()

    if key[0] == '.':
        return error_found()

    fname = form_name(digest, key) 
    if fname is None:
        return error_found()
        
    pubkey = generate_unique_hash()
    destdir = os.path.dirname(fname)
    destname = os.path.basename(fname)
    publicfile = os.path.join(destdir, '.public_%s' % pubkey)
    publicfilemap = os.path.join(destdir, '.public_%s' % destname)
    if os.path.isfile(publicfilemap):
        oldpublic = None
        try:
            fd = open(publicfilemap)
            old_pubkey = fd.read()
            fd.close()
            
            oldpublic = os.path.join(destdir, '.public_%s' % old_pubkey.strip())
            if os.path.isfile(oldpublic):
                os.remove(oldpublic)
        except:
            pass

    try:
        fd = open(publicfile, 'w')
        fd.write('%s\n' % (fname))
        fd.close()

        fd = open(publicfilemap, 'w')
        fd.write('%s\n' % (pubkey))
        fd.close()
    except:
        return error_found()

    return 'URL /get/%s/%s/%s' % (digest, pubkey, destname)

def generate_unique_hash():
    u = uuid.uuid4()
    return u.get_hex()

def generate_confirm(size=32):
    h = hashlib.sha256()
    h.update(os.urandom(size))
    return h.hexdigest()

@app.route('/remove/<digest>/<verify>/<key>', methods=['POST'])
def remove(digest, verify, key):
    challenge = solve_challenge()

    ok = validate_digest(digest, challenge, verify)
    if not ok:
        return error_auth()

    if not key:
        return error_auth()

    if key[0] == '.':
        return error_found()

    fname = form_name(digest, key) 
    if fname is None:
        return error_found()
        
    can_delete = False
    if request.method == 'POST':
        destdir = os.path.dirname(fname)
        destname = os.path.basename(fname)
        deletefile = os.path.join(destdir, '.delete_%s' % destname)
        if os.path.isfile(deletefile) and 'confirm' in request.form:
            confirm = request.form['confirm']
            try:
                fd = open(deletefile, 'r')
                data = fd.readlines()
                fd.close()
            except:
                data = None
            if data is not None and len(data) >= 2 and confirm == data[1].strip() and challenge != data[0].strip():
                os.remove(deletefile)
                can_delete = True
            else:
                return error_found()
        else:
            confirm = generate_confirm()
            fd = None
            try:
                fd = open(deletefile, 'w')
                fd.write('%s\n' % (challenge))
                fd.write('%s\n' % (confirm))
                fd.close()
            except:
                return error_found()
            finally:
                if fd is not None:
                    fd.close()
            return 'CONFIRM %s' % (confirm)

    else:
        return error_found()

    if can_delete:
        try:
            os.remove(fname)
        except:
            return error_found()
        return 'DELETED %s' % (key)

    return error_found()

def write_file(fname, data):
    fd = None
    res = True
    try:
        fd = open(fname, 'w')
        fd.write(data)
    except:
        res = False
    finally:
        if fd is not None:
            fd.close()

    return res

@app.route('/store', methods=['GET', 'POST'])
@app.route('/store/<digest>', methods=['GET', 'POST'])
def store(digest=None):
    if request.method == 'POST':
        if digest is None:
            digest = request.form['digest']
    
        ok = validate_digest(digest)
        if not ok:
            return error_auth()
        if not 'filedata' in request.files:
            return error_found()
        f = request.files['filedata']
        if f:
            if 'filename' in request.form:
                fname = request.form['filename']
            else:
                fname = f.filename
            fname = unique_name(digest, fname)
            f.save(fname)
            res = True
        else:
            res = False
    else:
        ok = validate_digest(digest)
        if not ok:
            return error_auth()
        data = request.args.get('data', '')
        fname = request.args.get('filename', '')
        fname = unique_name(digest, fname)
        if data and fname:
            res = write_file(fname, data)

    index = os.path.basename(fname)
    if res:
        return 'OK %s' % (index)
    else:
        return error_found()

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9999)