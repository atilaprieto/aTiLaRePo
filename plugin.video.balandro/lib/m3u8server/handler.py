# -*- coding: utf-8 -*-

import sys, base64
from platformcode import logger
from core import httptools
PY3 = False
if sys.version_info[0] < 3:
    from BaseHTTPServer import BaseHTTPRequestHandler
else:
    PY3 = True
    from http.server import BaseHTTPRequestHandler
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
            self.server._client.connected = True
            # ~ logger.info(self.path)
            if not PY3:
                url = base64.b64decode(self.path[1:])
            else:
                url = base64.b64decode(self.path[1:].encode('utf-8')).decode('utf-8')
            logger.info(url)
            data = httptools.downloadpage(url).data
            if not isinstance(data, bytes):
                data = data.encode('utf-8')
            self.wfile.write(data)

