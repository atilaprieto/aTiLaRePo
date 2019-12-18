# -*- coding: utf-8 -*-

import BaseHTTPServer, urllib2, base64
from platformcode import logger

default_headers = dict()
default_headers["User-Agent"] = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3163.100 Safari/537.36"
default_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
default_headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
default_headers["Accept-Charset"] = "UTF-8"
default_headers["Accept-Encoding"] = "gzip"


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.server._client.connected = True
        try:
            # ~ logger.info(self.path)
            url = base64.b64decode(self.path[1:])
            # ~ logger.info(url)
            
            req = urllib2.Request(url, None, default_headers)
            handle = urllib2.urlopen(req)
            
            self.wfile.write(handle.read())
            self.wfile.close()

        except Exception as e:
            logger.error(e)
