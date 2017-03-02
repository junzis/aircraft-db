#!/usr/bin/python

import sys
import os
from flup.server.fcgi import WSGIServer

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from webserver import app

if __name__ == '__main__':
    WSGIServer(app).run()
