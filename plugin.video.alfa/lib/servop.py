# -*- coding: utf-8 -*-
# --------------------------------------------------------
# By Alfa development Group
# --------------------------------------------------------

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib2
import thread
import xbmc
from platformcode import logger



class S(BaseHTTPRequestHandler):
    def do_GET(self):
        while 1:
            url = "https://lh3.googleusercontent.com/%s" %  self.path
            try:
                data = urllib2.urlopen(url)
            except:
                logger.error('Fallo data')
                break

            try:
                chunk = data.read()[4:]
                self.wfile.write(chunk)
                self.wfile.close()
 
            except Exception as e:
                logger.error(e)
                break

        
        
def run(server_class=HTTPServer, handler_class=S, port=8781):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    monitor = xbmc.Monitor()
    httpd.timeout = 1
    while not monitor.abortRequested():
        try:
            httpd.handle_request()
        except Exception as e:
            logger.error(e)
    httpd.socket.close()

def start():

    thread.start_new_thread(run, tuple())