# -*- coding: utf-8 -*-
# --------------------------------------------------------
# alfa_assistant tools
# --------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import base64
import json
import re
import xbmc

from platformcode import config
from core import httptools
from platformcode import logger
if not PY3:
    from lib import alfaresolver
else:
    from lib import alfaresolver_py3 as alfaresolver


EXTRA_TIMEOUT = 10000

ASSISTANT_SERVER = "http://127.0.0.1"

isAlfaAssistantOpen = False

if config.get_setting("assistant_mode") == "otro":
    if config.get_setting("assistant_custom_address"):
        ASSISTANT_SERVER = "http://%s" % config.get_setting("assistant_custom_address")


JS_CODE_CLICK_ON_VJS_BIG_PLAY_BUTTON = """
((() => {
    
    try {
        document.documentElement.getElementsByClassName('vjs-big-play-button')[0].click();
    } catch (e) {
        console.error('##Error getting vjs-big-play-button', e);
    };
}))();
"""

JS_CODE_CLICK_ON_JWPLAYER = """
    ((() => {
    
    try {
        document.documentElement.getElementsByClassName('jwplayer')[0].click();
    } catch (e) {
        console.error('##Error getting jwplayer', e);
    };
}))();
"""

def get_source_by_page_finished(url=None, timeout=None, jsCode=None, jsDirectCodeNoReturn=None, jsDirectCode2NoReturn=None, extraPostDelay=None, userAgent=None, debug=None, headers=None, malwareWhiteList=None, disableCache = None, closeAfter = None):
    return get_generic_call('getSourceByPageFinished', url, timeout, jsCode, jsDirectCodeNoReturn, jsDirectCode2NoReturn, extraPostDelay, userAgent, debug, headers, malwareWhiteList, disableCache, closeAfter)

def get_urls_by_page_finished(url=None, timeout=None, jsCode=None, jsDirectCodeNoReturn=None, jsDirectCode2NoReturn=None, extraPostDelay=None, userAgent=None, debug=None, headers=None, malwareWhiteList=None, disableCache = None, closeAfter = None):
    return get_generic_call('getUrlsByPageFinished', url, timeout, jsCode, jsDirectCodeNoReturn, jsDirectCode2NoReturn, extraPostDelay, userAgent, debug, headers, malwareWhiteList, disableCache, closeAfter)

def get_generic_call(endpoint, url=None, timeout=None, jsCode=None, jsDirectCodeNoReturn=None, jsDirectCode2NoReturn=None, extraPostDelay=None, userAgent=None, debug=None, headers=None, malwareWhiteList=None, disableCache = None, closeAfter = None):
    open_alfa_assistant(closeAfter)
    logger.info('##Assistant Endpoint: %s' % endpoint)
    if url:
        logger.info('##Assistant URL: %s' % url)
    else:
        url = 'about:blank'
    if timeout:
        logger.info('##Assistant delay-after-html-load: %s' % timeout)
    else:
        timeout = 0
    serverCall = '%s:48884/%s?url=%s&time=%s' % (ASSISTANT_SERVER, endpoint, base64.b64encode(url), timeout)
    if jsCode:
        serverCall += '&jsCode=%s' % base64.b64encode(jsCode)
        logger.info('##Assistant js-to-run-directly-with-return: %s' % jsCode)
    if jsDirectCodeNoReturn:
        serverCall += '&jsDirectCodeNoReturn=%s' % base64.b64encode(jsDirectCodeNoReturn)
        logger.info('##Assistant js-to-run-directly-with-no-return(type I): %s' % jsDirectCodeNoReturn)
    if jsDirectCode2NoReturn:
        serverCall += '&jsDirectCode2NoReturn=%s' % base64.b64encode(jsDirectCode2NoReturn)
        logger.info('##Assistant js-to-run-directly-with-no-return(type II): %s' % jsDirectCode2NoReturn)
    if extraPostDelay:
        serverCall += '&extraPostDelay=%s' % extraPostDelay
        logger.info('##Assistant delay-after-js-load: %s' % extraPostDelay)
    if userAgent:
        serverCall += '&userAgent=%s' % base64.b64encode(userAgent)
        logger.info('##Assistant user-agent: %s' % userAgent)
    if debug:
        serverCall += '&debug=%s' % debug
        logger.info('##Assistant debug-mode: %s' % debug)
    ## Por defecto se usa la caché pero en casos como mixdrop es mejor no usarla
    if disableCache:
        serverCall += '&cache=false'
        logger.info('##Assistant cache: False')
    if headers:
        serverCall += '&headers=%s' % base64.b64encode(headers)
        logger.info('##Assistant headers: %s' % headers)
    if malwareWhiteList:
        serverCall += '&malwareWhiteList=%s' % base64.b64encode(malwareWhiteList)
        logger.info('##Assistant malware-white-list: %s' % malwareWhiteList)

    logger.info('##Assistant Alfa Assistant URL: ' + serverCall)
    data = httptools.downloadpage(serverCall, timeout=timeout + EXTRA_TIMEOUT).data

    #if closeAfter:
    #    close_alfa_assistant()

    if data:
        return string_to_json(data)
    else:
        return data


def string_to_json(data):
    return json.loads(data)


def find_htmlsource_by_url_pattern(data, pattern):
    if not data:
        logger.info('##Assistant NOT received data from Alfa Mobile Helper')
    else:
        logger.info('##Assistant Received data from Alfa Mobile Helper')
        if data['htmlSources'] and len(data['htmlSources']) > 1:
            for attrs in data['htmlSources']:
                if re.search(pattern, attrs['url']):
                    logger.info('##Assistant iFrame URL found: ' + attrs['url'])
                    return {
                        'url': attrs['url'],
                        'source': base64.b64decode(attrs['source'])
                    }
                else:
                    logger.info('##Assistant The data found in Alfa Assistant has not the right info')
    return

def getInlineRequestedHeaders(requestHeaders, namesExceptionList = None):
    res = ""
    try:
        count = 0
        if requestHeaders:
            for requestHeader in requestHeaders:
                name = requestHeader["name"]
                if not namesExceptionList or name not in namesExceptionList:
                    value = requestHeader["value"]
                    if count == 0:
                        res += "|%s=%s" % (name, value)
                    else:
                        res += "&%s=%s" % (name, value)
                    count += 1

    except:
        logger.error('##Assistant getInlineRequestedHeaders Error')
        pass

    return res

def open_alfa_assistant(closeAfter = None):
    global isAlfaAssistantOpen
    if not isAlfaAssistantOpen:
        try:
            if (ASSISTANT_SERVER == "http://127.0.0.1" or ASSISTANT_SERVER == "http://localhost") and is_alfa_installed():
                logger.info('##Assistant Open Assistant at ' + ASSISTANT_SERVER)

                if closeAfter:
                    res = execute_in_alfa_assistant_with_cmd('openAndQuit')
                    isAlfaAssistantOpen = True
                else:
                    res = execute_in_alfa_assistant_with_cmd('open')
                    isAlfaAssistantOpen = True
                import time
                time.sleep(3)
                return res

            else:
                logger.info('##Assistant Assistant don\'t need to be open if not local. IP: ' + ASSISTANT_SERVER)
        except:
            logger.error('##Assistant Error opening it')
            pass
    else:
        logger.info('##Assistant Already was Assistant')

def close_alfa_assistant():
    global isAlfaAssistantOpen
    isAlfaAssistantOpen = False
    try:
        if (ASSISTANT_SERVER == "http://127.0.0.1" or ASSISTANT_SERVER == "http://localhost") and is_alfa_installed():
            return get_generic_call('quit')
        else:
            logger.info('##Assistant Assistant don\'t need to be closed if not local. IP: ' + ASSISTANT_SERVER)
    except:
        logger.error('##Assistant Error closing Assistant')
        pass

def is_alfa_installed():
    respuesta, app_name = alfaresolver.install_alfa_assistant(update=False)
    return respuesta

def update_alfa_assistant():
    #return execute_in_alfa_assistant_with_cmd('update')
    return alfaresolver.install_alfa_assistant(update=True)
    
def check_permissions_alfa_assistant():
    return execute_in_alfa_assistant_with_cmd('checkPermissions')

def execute_in_alfa_assistant_with_cmd(cmd):
    if xbmc.getCondVisibility("system.platform.Android"):
        # try:
        #     ANDROID_STORAGE = os.getenv('ANDROID_STORAGE')
        # except:
        #     ANDROID_STORAGE = ''
        # if not ANDROID_STORAGE:
        #     if "'HOME'" in os.environ:
        #         ANDROID_STORAGE = scrapertools.find_single_match(os.getenv('HOME'), '^(\/.*?)\/')
        #         if not ANDROID_STORAGE:
        #             ANDROID_STORAGE = '/storage'
        #     else:
        #         ANDROID_STORAGE = '/storage'

        # path = '/emulated/0/Android/data/com.alfa.alfamobilehelper'
        # xbmc.executebuiltin("StartAndroidActivity(%s,,,%s)" % ('com.alfa.alfamobilehelper', 'open'))
        # xbmc.executebuiltin("StartAndroidActivity(%s,,,%s)" % (filetools.basename(path), 'open'))
        # xbmc.executebuiltin("StartAndroidActivity(%s,%s,,%s)" % ('com.alfa.alfamobilehelper', 'android.intent.action.VIEW', 'open'))
        try:
            app = 'com.alfa.alfamobileassistant'
            intent = ''  # com.alfa.alfamobilehelper.MainActivity'
            dataType = cmd
            # dataType = 'openForDebug'
            dataURI = 'about:blank'
            cmd = 'StartAndroidActivity("%s", "%s", "%s", "%s")' % (app, intent, dataType, dataURI)
            xbmc.executebuiltin(cmd)
            return True
        except:
            return False
