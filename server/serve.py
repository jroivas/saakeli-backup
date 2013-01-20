#!/usr/bin/env python

from gevent.pywsgi import WSGIServer
from backuper import app

http_server = WSGIServer(('', 5000), app, keyfile='host.key', certfile='host.pem')
http_server.serve_forever()
