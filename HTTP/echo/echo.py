#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'edward'

import os
import BaseHTTPServer
import json
import urlparse
import random
class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    Page ="""\
    <htme>
    <body>
    <p>
    Hello, World!
    </p>
    </body>
    </html>
    """
    """
    handle GET request
    """
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type","Text/html")
        self.send_header("Content-Length",str(len(self.Page)))
        self.end_headers()
        self.wfile.write(self.Page)

if __name__ == '__main__':
    serverAddress = ('',8080)
    server = BaseHTTPServer.HTTPServer(serverAddress,RequestHandler)
    server.serve_forever()