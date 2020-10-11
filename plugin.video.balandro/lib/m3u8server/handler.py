# -*- coding: utf-8 -*-

import BaseHTTPServer, urllib2, base64
from platformcode import logger
from core import httptools

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.server._client.connected = True
        try:
            # ~ logger.info(self.path)
            url = base64.b64decode(self.path[1:])
            # ~ logger.info(url)
            data = httptools.downloadpage(url).data
            self.wfile.write(data)
            self.wfile.close()

        except Exception as e:
            logger.error(e)
