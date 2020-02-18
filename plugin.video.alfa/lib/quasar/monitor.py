from future import standard_library
standard_library.install_aliases()

import os
import xbmc
import base64
import urllib.request
import threading
from quasar.daemon import shutdown
from quasar.config import QUASARD_HOST


class QuasarMonitor(xbmc.Monitor):
    def __init__(self):
        self._closing = threading.Event()

    @property
    def closing(self):
        return self._closing

    def onAbortRequested(self):
        # Only when closing Kodi
        if xbmc.abortRequested:
            xbmc.executebuiltin("Dialog.Close(all, true)")
            shutdown()
            try:
                self._closing.set()
                self._closing.clear()
            except SystemExit as e:
                if e.code != 0:
                    os._exit(0)
                pass

    def onSettingsChanged(self):
        try:
            urllib.request.urlopen("%s/reload" % QUASARD_HOST)
            urllib.request.urlopen("%s/cmd/clear_page_cache" % QUASARD_HOST)
        except:
            pass

    def onNotification(self, sender, method, data):
        try:
            urllib.request.urlopen("%s/notification?sender=%s&method=%s&data=%s" % (
                QUASARD_HOST,
                sender,
                method,
                base64.b64encode(data)))
        except:
            pass
