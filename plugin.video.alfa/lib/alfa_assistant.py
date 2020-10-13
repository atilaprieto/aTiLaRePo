# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# alfa_assistant tools - Requiere al menos Assistant v. 1.0.498 (del 09/10/2020)
# ------------------------------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import base64
import json
import re
import xbmc
import subprocess
import time
import os
import traceback

from core import httptools
from core import filetools
from core import scrapertools
from core import jsontools
from platformcode import logger
from platformcode import config
from platformcode import platformtools


EXTRA_TIMEOUT = 10

ASSISTANT_SERVER = "http://127.0.0.1"
ASSISTANT_MODE = config.get_setting("assistant_mode")

isAlfaAssistantOpen = False

if ASSISTANT_MODE == "otro":
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

## Comunica con el navegador Alfa Assistant ##################################################################################################################################
#
# Recupera el código fuente de los recursos visitados y las URLS
#
def get_source_by_page_finished(url=None, timeout=None, jsCode=None, jsDirectCodeNoReturn=None, jsDirectCode2NoReturn=None, extraPostDelay=None, userAgent=None, debug=None, headers=None, malwareWhiteList=None, disableCache = None, closeAfter = None, getData = None, postData = None, getCookies = None, update = None, alfa_s=False, version=None, clearWebCache = False, removeAllCookies = False, hardResetWebView = False, keep_alive = False):
    return get_generic_call('getSourceByPageFinished', url, timeout, jsCode, jsDirectCodeNoReturn, jsDirectCode2NoReturn, extraPostDelay, userAgent, debug, headers, malwareWhiteList, disableCache, closeAfter, getData, postData, getCookies, update, alfa_s, version, clearWebCache, removeAllCookies, hardResetWebView, keep_alive)
##############################################################################################################################################################################

## Comunica con el navegador Alfa Assistant ##################################################################################################################################
#
# Recupera las URLS de los recursos visitados
#
def get_urls_by_page_finished(url=None, timeout=None, jsCode=None, jsDirectCodeNoReturn=None, jsDirectCode2NoReturn=None, extraPostDelay=None, userAgent=None, debug=None, headers=None, malwareWhiteList=None, disableCache = None, closeAfter = None, getData = None, postData = None, getCookies = None, update = None, alfa_s=False, version=None, clearWebCache = False, removeAllCookies = False, hardResetWebView = False, keep_alive = False):
    return get_generic_call('getUrlsByPageFinished', url, timeout, jsCode, jsDirectCodeNoReturn, jsDirectCode2NoReturn, extraPostDelay, userAgent, debug, headers, malwareWhiteList, disableCache, closeAfter, getData, postData, getCookies, update, alfa_s, version, clearWebCache, removeAllCookies, hardResetWebView, keep_alive)
##############################################################################################################################################################################

## Comunica con el navegador Alfa Assistant ##################################################################################################################################
#
# [Uso de parámetros]
#
# - Dirección Web donde Assistant va a navegar (GET) usando "url". Para usar POST ver "postData". El audio de la Web se silenciará para no molestar al usuario.
#   Ejemplo:
#       url = "https://www.myhost.com"
#
# - Configurar tiempo extra de espera tras la carga de la Web (para permitir que JS realice tareas).
#   Ejemplo (segundos):
#       timeout = 1
#
# - Envío de datos JSON a través de POST usando "postData". Esto se realiza cargando la Web en un iFrame (es útil porque hay Webs que lo requieren).
#   Ejemplo:
#       postData = '{"jsonKey1":"jsonValue1", "jsonKey2":"jsonValue2"}'
#
# - Envío de datos de formulario a través de POST usando "postData". Esto se realiza cargando la Web en un iFrame (es útil porque hay Webs que lo requieren).
#   Ejemplo:
#       postData = 'formKey1=formValue1&formkey2=formValue2'
#
# - Envío de datos de formulario a través de GET usando "getData": mismos ejemplos de uso que "postData". Esto se realiza cargando la Web en un iFrame (es útil porque hay Webs que lo requieren).
#
# - Configurar "UserAgent" para TODA la navegación en Assistant.
#   Ejemplo:
#       userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
#
# - Añadir "headers" a la URL inicial. El User Agent no se debería indicar aquí pues solo valdría para la URL inicial y no el resto (usar mejor parámetro "useAgent").
#   Ejemplo 1:
#       headers = '''[
#       {"name": "referer", "value": "https://www.myWebsite.com/"},
#       {"name": "otherKey", "value": "otherValue"},
#       ]'''
#
#   Ejemplo 2:
#       headers = '''[
#       {"name": "referer", "value": "{0}"},
#       {"name": "otherKey", "value": "{1}"},
#       ]'''
#       print(headers.format("value0", "value1"))
#
# - Ejecución de Javascript (CON retorno opcional) usando "jsCode".
#   Ejemplo:
#       jsCode = """
#           ((() => {
#               try {
#                   document.documentElement.getElementsByClassName('myClass')[0].click();
#                   return 'OK';    //LÍNEA OPCIONAL!!
#               } catch (e) {
#                   console.error('##Error getting jwplayer', e);
#                   return 'KO';    //LÍNEA OPCIONAL!!
#               };
#           }))();
#       """
#
# - Ejecución de Javascript SIN retorno usando "jsDirectCodeNoReturn": mismo uso y ejemplos que jsCode pero sin "return".
#
# - Ejecución de Javascript SIN retorno usando jsDirectCode2NoReturn: mismo uso y ejemplos que jsCode pero sin "return".
#
# - Espera tras ejecución de JS (o sea tras "jsCode", "jsDirectCodeNoReturn" o "jsDirectCode2NoReturn") usando "extraPostDelay".
#   Ejemplo (segundos):
#       extraPostDelay = 1
#
# - Recibir cookies (por defecto False).
#   Ejemplo:
#       getCookies = True
#   Posible respuesta:
#       ...
#       "cookies":
#           {
#               "cookiesList": "cookie1; cookie2=valor2; cookie3="
#               "urls": [
#                   "http://www.myweb1.com",
#                   "http://www.myweb2.com"    
#               ]
#           
#           }
#       ...
#
# - Por defecto y para acelerar las consultas repetitivas, Assistant usa caché de respuestas (con caducidad de 24 horas).
#   Ejemplo de desactivación:
#       disableCache = True
#
# - Cierre automático de Assistant tras su uso (sino queda abierto -aunque no en primer plano sino de fondo-).
#   Ejemplo de cierre tras uso de Assistant:
#       closeAfter = True
#
# - Assistant filtra los recursos que se intentan usar en la navegación a partir de varios repositorios online anti-malware, anti-mining, etc. Se pueden añadir exclusiones a esta lista a través del parámetro "malwareWhiteList" (usando Regex de tipo Java).
#   Ejemplo:
#       malwareWhiteList = '''[
#       ".*google.*com",
#       ".*yahoo.*com",
#       ]'''
#
#
#
# - NUNCA USAR EN PRODUCCIÓN: PARA AYUDAR A LOS DESARROLLADORES se puede mostrar lo que el navegador Assistant está haciendo. Cuidado: ni limpia recursos ni se cierra, además se puede incluso oir el audio de la Web visitada.
#   Ejemplo de activación de depuración:
#       debug = true
#
def get_generic_call(endpoint, url=None, timeout=None, jsCode=None, jsDirectCodeNoReturn=None, jsDirectCode2NoReturn=None, extraPostDelay=None, userAgent=None, debug=None, headers=None, malwareWhiteList=None, disableCache = None, closeAfter = None, getData = None, postData = None, getCookies = None, update = None, alfa_s = False, version = None, clearWebCache = False, removeAllCookies = False, hardResetWebView = False, keep_alive = False):
    if endpoint not in ['ping', 'getWebViewInfo', 'update', 'quit']:
        res = open_alfa_assistant(closeAfter)
        logger.info('##Assistant Endpoint: %s, Status: %s' % (endpoint, str(res)))
        if not res:
            return False
    if url:
        logger.info('##Assistant URL: %s' % url)
    else:
        url = 'about:blank'
    if timeout and endpoint not in ['ping', 'getWebViewInfo', 'update', 'quit']:
        logger.info('##Assistant delay-after-html-load: %s' % str(timeout*1000))
    elif not timeout:
        timeout = 0
    if endpoint == 'getWebViewInfo':
        serverCall = '%s:48884/%s' % (ASSISTANT_SERVER, 'ping')
    else:
        serverCall = '%s:48884/%s' % (ASSISTANT_SERVER, endpoint)
    if endpoint == 'update':
        serverCall += '?version=%s' % version
    if endpoint not in ['ping', 'getWebViewInfo', 'update', 'quit']:
        serverCall += '?url=%s&time=%s' % (base64.b64encode(url.encode('utf8')).decode('utf8'), str(timeout*1000))
    
    if jsCode:
        serverCall += '&jsCode=%s' % base64.b64encode(jsCode.encode('utf8')).decode('utf8')
        logger.info('##Assistant js-to-run-directly-with-return: %s' % jsCode)
    if jsDirectCodeNoReturn:
        serverCall += '&jsDirectCodeNoReturn=%s' % base64.b64encode(jsDirectCodeNoReturn.encode('utf8')).decode('utf8')
        logger.info('##Assistant js-to-run-directly-with-no-return(type I): %s' % jsDirectCodeNoReturn)
    if jsDirectCode2NoReturn:
        serverCall += '&jsDirectCode2NoReturn=%s' % base64.b64encode(jsDirectCode2NoReturn.encode('utf8')).decode('utf8')
        logger.info('##Assistant js-to-run-directly-with-no-return(type II): %s' % jsDirectCode2NoReturn)
    if extraPostDelay:
        timeout += extraPostDelay
        serverCall += '&extraPostDelay=%s' % (extraPostDelay*1000)
        logger.info('##Assistant delay-after-js-load: %s' % str(extraPostDelay*1000))
    if userAgent:
        serverCall += '&userAgent=%s' % base64.b64encode(userAgent.encode('utf8')).decode('utf8')
        logger.info('##Assistant user-agent: %s' % userAgent)
    ## Por defecto "debug" es False y debe serlo siempre en Producción
    if debug:
        serverCall += '&debug=%s' % debug
        logger.info('##Assistant debug-mode: %s' % str(debug))
    ## Por defecto "getCookies" es False
    if getCookies:
        serverCall += '&getCookies=%s' % getCookies
        logger.info('##Assistant get-cookies: %s' % str(getCookies)      )  
    ## Por defecto "cache" es True pero en casos como mixdrop es mejor no usarla
    if disableCache:
        serverCall += '&cache=False'
        logger.info('##Assistant disableCache: %s' % str(disableCache))
    if headers:
        serverCall += '&headers=%s' % base64.b64encode(headers.encode('utf8')).decode('utf8')
        logger.info('##Assistant headers: %s' % headers)
    if malwareWhiteList:
        serverCall += '&malwareWhiteList=%s' % base64.b64encode(malwareWhiteList.encode('utf8')).decode('utf8')
        logger.info('##Assistant malware-white-list: %s' % malwareWhiteList)
    if getData:
        serverCall += '&getData=%s' % base64.b64encode(getData.encode('utf8')).decode('utf8')
        logger.info('##Assistant get-data: %s' % getData)
    if postData:
        serverCall += '&postData=%s' % base64.b64encode(postData.encode('utf8')).decode('utf8')
        logger.info('##Assistant post-data: %s' % postData)
    if clearWebCache:
        serverCall += '&clearWebCache=%s' % clearWebCache
        logger.info('##Assistant clearWebCache: %s' % str(clearWebCache))
    if removeAllCookies:
        serverCall += '&removeAllCookies=%s' % removeAllCookies
        logger.info('##Assistant removeAllCookies: %s' % str(removeAllCookies))
    if hardResetWebView:
        serverCall += '&hardResetWebView=%s' % hardResetWebView
        logger.info('##Assistant hardResetWebView: %s' % str(hardResetWebView))

    if endpoint not in ['ping', 'getWebViewInfo', 'update', 'quit']:
        logger.info('##Assistant URL: ' + serverCall)
    response = httptools.downloadpage(serverCall, timeout=timeout+EXTRA_TIMEOUT, alfa_s=alfa_s, ignore_response_code=True, keep_alive=keep_alive)
    if not response.sucess and endpoint in ['ping', 'getWebViewInfo']:
        logger.info('##Assistant "%s" FALSE, timeout %s: %s' % (endpoint, timeout+EXTRA_TIMEOUT, serverCall), force=True)
    if not (response.sucess or response.data) and endpoint not in ['ping', 'getWebViewInfo', 'quit']:
        close_alfa_assistant()
        time.sleep(2)
        res = open_alfa_assistant(closeAfter, retry=True)
        if not res:
            time.sleep(10)
            res = get_generic_call('ping', timeout=2-EXTRA_TIMEOUT+10, alfa_s=True)
        if res:
            serverCall = serverCall.replace('&cache=False', '&cache=True')
            logger.info('##Assistant retrying URL: ' + serverCall)
            response = httptools.downloadpage(serverCall, timeout=timeout+EXTRA_TIMEOUT, alfa_s=alfa_s, ignore_response_code=True, keep_alive=keep_alive)
        else:
            platformtools.dialog_notification("ACTIVE Alfa Assistant en ", "%s" % ASSISTANT_SERVER)
    data = response.data
    
    #if closeAfter:
    #    close_alfa_assistant()

    if data:
        if endpoint in ['update']:
            return data
        try:
            data_ret = jsontools.load(data)
            if endpoint in ['ping', 'getWebViewInfo']:
                if endpoint in ['ping']:
                    data_ret = data_ret.get('assistantVersion', '')
                logger.info('##Assistant "%s" TRUE, timeout %s: %s' % (endpoint, timeout+EXTRA_TIMEOUT, str(data_ret)))
        except:
            data_ret = data
            logger.error('##Assistant "%s" ERROR, timeout %s: %s' % (endpoint, timeout+EXTRA_TIMEOUT, str(data_ret)))
        return data_ret
    else:
        data = ''
        return data
##############################################################################################################################################################################

#
# Lista el código fuente (decodificado) según filtro regex (parámetro "pattern") entre los datos que devuelve el navegador Alfa Assistant (parámetro "data")
#
def find_htmlsource_by_url_pattern(data, pattern):
    if not data:
        logger.info('##Assistant NOT received data from Alfa Assistant')
    else:
        logger.info('##Assistant Received data from Alfa Assistant')
        if data['htmlSources'] and len(data['htmlSources']) >= 1:
            for attrs in data['htmlSources']:
                if re.search(pattern, attrs['url']):
                    logger.info('##Assistant URL found by find_htmlsource_by_url_pattern: ' + attrs['url'])
                    return {
                        'url': attrs['url'],
                        'source': base64.b64decode(attrs['source']).decode('utf8')
                    }
                else:
                    logger.info('##Assistant The data found in Alfa Assistant has not the right info')
    return

#
# Prepara en una línea los argumentos necesarios para constituir una URL a partir de una lista que proviene de consultar Alfa Assistant
# Ejemplo:
#   from lib import alfa_assistant
#   data_assistant = alfa_assistant.get_urls_by_page_finished(global_url, 1, jsDirectCode2NoReturn=js_code, extraPostDelay=2, userAgent=ua, disableCache=True, closeAfter=True)
#   for visited in data_assistant["urlsVisited"]:
#       url = visited["url"] + alfa_assistant.getInlineRequestedHeaders(visited["requestHeaders"], [])
#
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
        logger.error(traceback.format_exc(1))

    return res    #Ejemplo: |param1=value1&param2=value2


##############################################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################
## F U N C I O N E S   D E   B A J O   N I V E L #############################################################################################################################
################# NO TOCAR ###################################################################################################################################################
##############################################################################################################################################################################
##############################################################################################################################################################################

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def open_alfa_assistant(closeAfter=None, getWebViewInfo=False, retry=False):
    global isAlfaAssistantOpen
    
    if not isAlfaAssistantOpen:
        res = False
        try:
            if ASSISTANT_MODE == 'este':
                logger.info('##Assistant Open at ' + ASSISTANT_SERVER)
                
                if not is_alfa_installed():
                    logger.error('##Assistant not installed or not available')
                    return False

                if closeAfter:
                    res = execute_in_alfa_assistant_with_cmd('openAndQuit')
                    isAlfaAssistantOpen = True
                else:
                    res = execute_in_alfa_assistant_with_cmd('open')
                    isAlfaAssistantOpen = True

                for x in range(7):
                    time.sleep(2)
                    res = get_generic_call('getWebViewInfo', timeout=1-EXTRA_TIMEOUT, alfa_s=True)
                    if res:
                        if isinstance(res, dict):
                            check_webview_version(res.get('wvbVersion', ''))
                            if not getWebViewInfo:
                                res = res.get('assistantVersion', '')
                            isAlfaAssistantOpen = res
                        else:
                            isAlfaAssistantOpen = res
                        return res
                
                isAlfaAssistantOpen = False
                return False

            else:
                res = get_generic_call('getWebViewInfo', timeout=3-EXTRA_TIMEOUT, alfa_s=True)
                if res:
                    if isinstance(res, dict):
                        check_webview_version(res.get('wvbVersion', ''))
                        if not getWebViewInfo:
                            res = res.get('assistantVersion', '')
                    return res
                else:
                    if not retry:
                        platformtools.dialog_notification("ACTIVE Alfa Assistant en %s" % ASSISTANT_SERVER, 
                                    "o Instale manualmente desde [COLOR yellow]https://bit.ly/2Zwpfzq[/COLOR]")
                    return False
        except:
            logger.error('##Assistant Error opening it')
            logger.error(traceback.format_exc(1))
        return res
    
    else:
        logger.info('##Assistant Already was Opened: %s' % str(isAlfaAssistantOpen))
        return isAlfaAssistantOpen

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def close_alfa_assistant():
    global isAlfaAssistantOpen
    isAlfaAssistantOpen = False
    try:
        if (ASSISTANT_SERVER == "http://127.0.0.1" or ASSISTANT_SERVER == "http://localhost") and is_alfa_installed():
            logger.info('##Assistant Close at ' + ASSISTANT_SERVER)
            return get_generic_call('quit', timeout=1-EXTRA_TIMEOUT, alfa_s=True)
        else:
            logger.info('##Assistant don\'t need to be closed if not local. IP: ' + ASSISTANT_SERVER)
    except:
        logger.error('##Assistant Error closing')
        logger.error(traceback.format_exc(1))

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def check_webview_version(wvbVersion):

    if not wvbVersion:
        logger.info('##Assistant wvbVersion NO DETECTADA', force=True)
        return
        
    if 'NEEDED_TO_CHECK_ONLINE_LIST_BASED_ON_ANDROID_VERSION' in wvbVersion:
        logger.info('##Assistant wvbVersion ANTERIOR a Android 5', force=True)
        return

    # Comparar la versión de WebView que tiene el Android donde reside la APP con la versión mínima adecuada
    ver_min = 85
    
    wvbVersion_list = wvbVersion.split('.')
    if len(wvbVersion_list) > 1:
        try:
            wvbVersion_major = int(wvbVersion_list[0])
        except:
            logger.error('##Assistant Error in wvbVersion: %s' % str(wvbVersion))
            return
            
        if wvbVersion_major < ver_min:
            logger.info('##Assistant wvbVersion OBSOLETA: %s' % str(wvbVersion), force=True)
            if not config.get_setting('wvbVersion_msg', False):
                config.set_setting('wvbVersion_msg', True)
                platformtools.dialog_notification("Alfa Assistant WebView: versión obsoleta", \
                            "%s - Actualice a una versión actual" % str(wvbVersion), time=10000)
    
    return
#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def is_alfa_installed(remote='', verbose=False):
    global isAlfaAssistantOpen
    version = True
    if not isAlfaAssistantOpen:
        version, app_name = install_alfa_assistant(update=False, remote=remote, verbose=verbose)
    return version

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def update_alfa_assistant(remote='', verbose=False):
    #return execute_in_alfa_assistant_with_cmd('update')
    return install_alfa_assistant(update=True, remote=remote, verbose=verbose)

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def check_permissions_alfa_assistant():
    return execute_in_alfa_assistant_with_cmd('checkPermissions')

#
## Comunica DIRECTAMENTE con el navegador Alfa Assistant ##################################################################################################################################
#
def execute_in_alfa_assistant_with_cmd(cmd, dataURI='about:blank'):
    if xbmc.getCondVisibility("system.platform.Android"):
        try:
            app = 'com.alfa.alfamobileassistant'
            intent = ''  # com.alfa.alfamobilehelper.MainActivity'
            dataType = cmd # 'openForDebug'
            cmd = 'StartAndroidActivity("%s", "%s", "%s", "%s")' % (app, intent, dataType, dataURI)
            logger.info('##Assistant executing CMD: ' + cmd)
            xbmc.executebuiltin(cmd)
            return True
        except:
            logger.error(traceback.format_exc(1))
            return False
    
    return False

#
## Instala o actualiza la app de Assitant ##################################################################################################################################
#
def install_alfa_assistant(update=False, remote='', verbose=False):
    if update:
        logger.info('update=%s' % str(update))
    # Si ya está instalada, devolvemos el control
    app_name = 'com.alfa.alfamobileassistant'
    if not verbose: verbose = config.get_setting('addon_update_message')        # Verbose en la actualización/instalación
    assistant_flag_install = config.get_setting('assistant_flag_install', default=True)
    addonid = 'alfa-mobile-assistant'
    download = addonid + '.apk'
    package = addonid + '.apk'
    version = addonid + '.version'
    forced_menu = False
    respuesta = False
    alfa_s = True
    addons_path = config.get_runtime_path()
    if filetools.exists(filetools.join(addons_path, 'channels', 'custom.py')):
        alfa_s = False

    if not remote:
        ANDROID_STORAGE = os.getenv('ANDROID_STORAGE')
        if not ANDROID_STORAGE: ANDROID_STORAGE = '/storage'
    else:
        # Remote es la url de un servidor FTP o SMB activo que apunta a la ruta "/storage" del dispositivo Android
        ANDROID_STORAGE = remote
        if ANDROID_STORAGE.endswith('/'):
            ANDROID_STORAGE = ANDROID_STORAGE[:-1]
    apk_files = '%s/%s/%s/%s/%s/%s' % (ANDROID_STORAGE, 'emulated', '0', 'Android', 'data', app_name)
    if ASSISTANT_MODE == 'este' and not filetools.exists(filetools.dirname(apk_files)):
        apk_files_alt = scrapertools.find_single_match(os.getenv('HOME'), '(.*?)\/\w*.\w*.\w*\/files')
        logger.info('HOME: ' + apk_files_alt)
        if apk_files_alt and filetools.exists(apk_files_alt):
            apk_files = '%s/%s' % (apk_files_alt, app_name)

    version_path = filetools.join(config.get_data_path(), version)
    version_act = filetools.read(version_path, silent=True)
    if not version_act: version_act = '0.0.0'
    
    # Averiguamos si es instalacción, update, o forzado desde el Menú de Ajustes
    if not update and ASSISTANT_MODE == 'este' and filetools.exists(apk_files):
        return version_act, app_name
    if ASSISTANT_MODE == 'este' and not update:
        check_permissions_alfa_assistant()                                      # activamos la app por si no se ha inicializado
        time.sleep(1)
        if filetools.exists(apk_files):
            return version_act, app_name
    # Mirarmos si la app está activa y obtenemos el nº de versión
    version_dict = get_generic_call('getWebViewInfo', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
    if isinstance(version_dict, dict):
        version_app = version_dict.get('assistantVersion', '')
        try:
            android_version = int(scrapertools.find_single_match(version_dict.get('userAgent', ''), r"Android\s*(\d+)"))
        except:
            android_version = 8
    else:
        version_app = version_dict
        android_version = 8
    if version_app and not update:
        return version_app, app_name
    
    if version_app:
        app_active = True
    else:
        app_active = False
        if ASSISTANT_MODE == "este":
            execute_in_alfa_assistant_with_cmd('openAndQuit')                   # activamos la app por si no se ha inicializado
            time.sleep(2)
            version_dict = get_generic_call('getWebViewInfo', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
            if isinstance(version_dict, dict):
                version_app = version_dict.get('assistantVersion', '')
                try:
                    android_version = int(scrapertools.find_single_match(version_dict.get('userAgent', ''), r"Android\s*(\d+)"))
                except:
                    android_version = 8
            else:
                version_app = version_dict
                android_version = 8
    version_actual = filetools.read(version_path, silent=True)
    if not version_actual and version_app:
        version_actual = version_app
        filetools.write(version_path, version_actual, mode='wb', silent=True)
    elif not version_actual:
        version_actual = '0.0.0'

    if ASSISTANT_MODE != 'este':
        if not version_app:
            if verbose or (update and not isinstance(update, bool)):
                platformtools.dialog_notification("Active Alfa Assistant", 
                            "o Instale manualmente desde [COLOR yellow]https://bit.ly/2Zwpfzq[/COLOR]")
            logger.info("Active Alfa Assistant, o Instale manualmente desde [COLOR yellow]https://bit.ly/2Zwpfzq[/COLOR]", force=True)
            config.set_setting('assistant_flag_install', False)
            return version_app, app_name
        else:
            config.set_setting('assistant_flag_install', True)
            if not update:
                return version_app, app_name
    elif not update and not assistant_flag_install and not filetools.exists(apk_files):
        logger.info('NO está instalada. El usuario no quiere instalaciñon automática: %s' % app_name)
        return False, app_name
    elif update and isinstance(update, bool) and not filetools.exists(apk_files):
        logger.info('NO está instalada. No se va a actualizar: %s' % app_name)
        return False, app_name
    elif update and not isinstance(update, bool) and not filetools.exists(apk_files):
        logger.info('NO está instalada. Viene del Menú y se va a instalar: %s' % app_name)
        update = False
        forced_menu = True
    elif not remote and not xbmc.getCondVisibility("system.platform.android"):
        logger.info('El sistema local no es Android: %s' % app_name)
        return False, app_name

    logger.info('assistant_mode=%s, update=%s, forced_menu=%s, assistant_flag_install=%s, version_actual=%s, android=%s, app_active=%s' \
            % (ASSISTANT_MODE, str(update), str(forced_menu), str(assistant_flag_install), version_actual, str(android_version), str(app_active)))
    
    # Si no está instalada, o se quiere actualizar, empezamos el proceso
    alfa_assistant_pwd = ''
    assistant_urls = ['https://github.com/alfa-addon/alfa-repo/raw/master/downloads/assistant/%s' % version, \
            'https://bitbucket.org/alfa_addon/alfa-repo/raw/master/downloads/assistant/%s' % version]
    
    apk_updated = filetools.join(addons_path, 'tools')
    apk_path = filetools.join(apk_updated, download)
    apk_apk = filetools.join(apk_updated, package)
    upk_install_path = filetools.join('special://xbmc/', 'files').replace('/cache/apk/assets', '')
    if not remote:
        apk_install = filetools.join(ANDROID_STORAGE, 'emulated', '0', 'Download')
        apk_install_SD = filetools.join(apk_install, package)
    else:
        apk_install = '%s/%s/%s/%s' % (ANDROID_STORAGE, 'emulated', '0', 'Download')
        apk_install_SD = '%s/%s' % (apk_install, package)

    if not update and not remote and not forced_menu:
        # Probamos a iniciar por si se ha instalado manualmente y no se ha iniciado la estrucutra de archivos
        check_permissions_alfa_assistant()
        try:
            command = ['pm', 'list', 'packages']
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            PM_LIST, error_cmd = p.communicate()
            if PY3 and isinstance(label_a, bytes):
                PM_LIST = PM_LIST.decode()
            if app_name in PM_LIST:
                logger.info('Ya instalada. Volvemos: %s' % app_name)
                return version_actual, app_name
        except:
            logger.error(traceback.format_exc(1))
    
    if not update and not forced_menu and not platformtools.dialog_yesno("Instalación Alfa Assistant", \
                    "¿Desea instalar la App [COLOR yellow][B]%s[/B][/COLOR]\n" % app_name +
                    " como ayuda para acceder a ciertos canales y servidores?"):
        config.set_setting('assistant_flag_install', False)
        return respuesta, app_name
    elif update and not isinstance(update, bool):
        platformtools.dialog_notification("Instalación Alfa Assistant", "Comienza la actualización")
    elif forced_menu:
        platformtools.dialog_notification("Instalación Alfa Assistant", "Comienza la instalación")

    # Comprobamos si el dispositivo está rooteado
    is_rooted = config.is_rooted(silent=True)                                   # ¡OJO! puede pedir permisos root en algunos dispositivos
    if is_rooted == 'rooted' and ASSISTANT_MODE == 'este':                      # El dispositivo esta rooteado?
        update_install = 'py'                                                   # Se actualiza desde esta función
    else:
        update_install = 'app'                                                  # Se actualiza desde la app
    cmd = 'update'                                                              # Comando de la app para auto actualizarse
    dataURI = 'Version:%s'                                                      # Versión a actualizar
    
    # Comprobamos si hay acceso a Github o BitBucket
    for assistant_rar in assistant_urls:
        response = httptools.downloadpage(assistant_rar, timeout=5, ignore_response_code=True, alfa_s=alfa_s, json_to_utf8=False)
        if response.sucess:
            break
    
    # Descargamos el archivo de version.  Si hay error avisamos, pero continuamos
    if not response.sucess:
        if update and isinstance(update, bool):
            logger.error("Error en la descarga de control de versión. No se puede actualizar: %s" % str(response.code))
            return respuesta, app_name
        platformtools.dialog_notification("Instalación Alfa Assistant", "Error en la descarga de control de versión. Seguimos")
        logger.error("Error en la descarga de control de versión. Seguimos...: %s" % str(response.code))

    #Si es una actualización programada, comprobamos las versiones de Github y de lo instalado
    if update and isinstance(update, bool):
        if version_actual != response.data:
            if version_app:
                version_actual = version_app
                filetools.write(version_path, version_actual, mode='wb', silent=True)
        if version_actual == response.data:
            if verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Ya está actualizado a version %s" % response.data)
            logger.info("Alfa Assistant ya actualizado a versión: %s" % response.data)
            return version_actual, app_name

    # Guardamos archivo de versión
    if remote:
        version_path = '%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s' % (ANDROID_STORAGE, 'emulated', '0', 'Android', 
                        'data', 'org.xbmc.kodi', 'files', '.kodi', 'addons', 'plugin.video.alfa', 
                        'tools', version)
        if not filetools.exists(filetools.dirname(version_path)):
            logger.error("Ruta a carpeta remota de versión no es estándar: %s" % version_path)
            version_path = ''
    version_old = version_actual
    version_actual = response.data
    if version_path:
        res = filetools.write(version_path, response.data, mode='wb', silent=True)
        if not res:
            if not update: platformtools.dialog_notification("Instalación Alfa Assistant", \
                            "Error en la escritura de control de versión. Seguimos...")
            logger.error("Error en la escritura de control de versión. Seguimos...: %s" % assistant_rar)

    # Descargamos y guardamos el .APK
    assistant_rar = assistant_rar.replace(version, download)                    # Sustituir en la url la versión por el apk
    res = False
    if not update: platformtools.dialog_notification("Instalación Alfa Assistant", "Descargando APK")
    logger.info('Descargando de_ %s' % assistant_rar)
    response = httptools.downloadpage(assistant_rar, timeout=5, ignore_response_code=True, alfa_s=alfa_s, json_to_utf8=False)
    if not response.sucess:
        if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error en la descarga del .apk")
        response.data = ''
        logger.error("Error en la descarga del .apk: %s" % str(response.code))
    else:
        # Guardamos archivo descargado de APK
        res = filetools.write(apk_path, response.data, mode='wb', silent=True)
        if not res:
            if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error en la escritura del APK")
            logger.error("Error en la escritura del APK: %s" % apk_path)
        
        else:
            if '.rar' in download:
                # Empezando la extracción del .rar del APK
                try:
                    import rarfile
                    archive = rarfile.RarFile(apk_path)
                    if alfa_assistant_pwd: archive.setpassword(alfa_assistant_pwd)
                    archive.extractall(apk_updated)
                except:
                    logger.error(traceback.format_exc(1))
            elif '.zip' in download:
                # Empezando la extracción del .rar del APK
                try:
                    import ziptools
                    archive = ziptools.ziptools()
                    #if alfa_assistant_pwd: archive.setpassword(alfa_assistant_pwd)      # No hay password en .zip
                    archive.extract(filetools.basename(apk_updated), filetools.dirname(apk_updated))
                except:
                    xbmc.executebuiltin('Extract("%s","%s")' % (filetools.basename(apk_updated), filetools.dirname(apk_updated)))
                    time.sleep(1)

            # Verificado si está el APK, y si está y es LOCAL lo instalamos
            if ASSISTANT_MODE == "este":
                res = filetools.copy(apk_apk, apk_install_SD, silent=True)
                if not res or not filetools.exists(apk_install_SD):
                    if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error de Extracción o Copia %s" % package)
                    logger.error("Error de Extracción o copia %s" % package)
                
                # Si está rooteado se instala/actualiza directamente
                elif update_install == 'py' and res and filetools.exists(apk_install_SD):

                    # Instalamos: nueva o actualización. 
                    if not update: platformtools.dialog_notification("Instalación Alfa Assistant", "Installando %s" % package)
                    logger.info("Installing %s" % package)
                    
                    # Instalación Remota
                    if remote:
                        filetools.remove(apk_apk, silent=True)
                        platformtools.dialog_notification("Alfa Assistant: Descarga Remota terminada", "Instale manualmente desde: %s" % apk_install_SD)
                        logger.info("Alfa Assistant: Descarga Remota terminada. Instale manualmente desde: %s" % apk_install_SD)
                        return version_actual, app_name

                    # Instalación Local
                    if not filetools.exists(upk_install_path):
                        filetools.mkdir(upk_install_path)
                    upk_install_path = filetools.join(upk_install_path, package)
                    res = filetools.copy(apk_install_SD, upk_install_path, ch_mod='777')    # Copiamos APK a la partición del Sistema, y cambiamos permisos
                    if not res:
                        if not update or verbose: platformtools.dialog_notification("Instalación Alfa Assistant", "Error de Copia %s" % package)
                        logger.error(str(filetools.listdir(apk_install)))
                        logger.error(filetools.file_info(filetools.dirname(upk_install_path)))
                        logger.error(str(filetools.listdir(filetools.dirname(upk_install_path), file_inf=True)))
                    else:

                        # Intenta la instalación vía ROOT y si no funciona como NO ROOT
                        
                        # Marcamos la opción de instalación, -r si es actualización, -g (todos los permisos granted) si es instalación
                        if filetools.exists(apk_files):
                            pm_opt = '-r'
                        else:
                            pm_opt = '-g'
                        
                        # Listamos todas las opciones de comandos, según las variantes de Android
                        command_list = [
                                        ['adb', 'install', '%s' % upk_install_path],
                                        ['su', '-c', 'pm install %s %s' % (pm_opt, upk_install_path)],
                                        ['su', '-c', 'pm', 'install', pm_opt, '%s' % upk_install_path],
                                        ['su', '-0', 'pm install %s %s' % (pm_opt, upk_install_path)],
                                        ['su', '-0', 'pm', 'install', pm_opt, '%s' % upk_install_path]
                                       ]
                        
                        for command in command_list:
                            try:
                                logger.info(command, force=True)
                                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                output_cmd, error_cmd = p.communicate()
                                if error_cmd:
                                    if error_cmd.startswith('su:'): continue
                                    if update:
                                        ver_upd = get_generic_call('ping', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
                                        if not ver_upd:
                                            execute_in_alfa_assistant_with_cmd('open')  # activamos la app por si no se ha inicializado
                                            time.sleep(1)
                                            ver_upd = get_generic_call('ping', timeout=2-EXTRA_TIMEOUT, alfa_s=True)
                                            execute_in_alfa_assistant_with_cmd('quit')
                                        if ver_upd == version_actual:
                                            logger.debug(str(error_cmd), force=True)
                                            error_cmd = ''
                                    else:
                                        check_permissions_alfa_assistant()
                                        time.sleep(1)
                                        if filetools.exists(apk_files):
                                            logger.debug(str(error_cmd), force=True)
                                            error_cmd = ''
                                    if error_cmd:
                                        logger.error(str(error_cmd))
                                    else:
                                        respuesta = version_actual
                                        break
                                else:
                                    respuesta = version_actual
                                    break
                            except Exception as e:
                                if not PY3:
                                    e = unicode(str(e), "utf8", errors="replace").encode("utf8")
                                logger.error('Command ERROR: %s, %s' % (str(command), str(e)))
                                continue
      
    # Ùltimo resorte: instalación manual desde GitHub o actualización desde la app
    if not respuesta and update:
        
        # Si hay que actualizar se verifica el vehículo de instalación
        logger.info("Instalación Alfa Assistant. Actualización desde la app de %s a %s" % (version_old, version_actual))
        version_mod = version_actual
        if not isinstance(update, bool):
            version_mod = '9.9.999'                                             # Intenta forzar la actualización si viene desde el Menú
        if ASSISTANT_MODE == "este":
            if android_version >= 10:
                app_active = False
                respuesta = execute_in_alfa_assistant_with_cmd(cmd, dataURI=dataURI % version_mod)
            else:
                if not app_active:
                    execute_in_alfa_assistant_with_cmd('openAndQuit')               # activamos la app por si no se ha inicializado
                    time.sleep(1)
                app_active = False
                respuesta = get_generic_call(cmd, version=version_mod, alfa_s=alfa_s)
        else:
            if app_active:
                respuesta = get_generic_call(cmd, version=version_mod, alfa_s=alfa_s)

        if not respuesta and ASSISTANT_MODE != "este":
            if verbose or not isinstance(update, bool):
                platformtools.dialog_notification("Instalación Alfa Assistant", "Intente la actualización manualmente %s" % version_actual)
            logger.info("Instalación Alfa Assistant. Intente la actualización manualmente %s" % version_actual)
            return False, app_name
        elif not respuesta:
            # Update local
            #respuesta = execute_in_alfa_assistant_with_cmd(cmd, dataURI=dataURI % version_mod)
            if not respuesta:
                if verbose or not isinstance(update, bool):
                    platformtools.dialog_notification("Instalación Alfa Assistant", "Actualización en error %s. REINTENTANDO" % version_actual)
                logger.info("Instalación Alfa Assistant. Actualización en error %s. REINTENTANDO" % version_actual)
        else:
            respuesta = version_actual
        
    if not respuesta:
        config.set_setting('assistant_flag_install', False)                     # No vuelve a intentar la instalación
        try:
            #xbmc.executebuiltin('StartAndroidActivity("","android.intent.action.VIEW","application/vnd.android.package-archive","file:%s")' % apk_install_SD)
            
            if ASSISTANT_MODE == "este":
                from lib import generictools
                assistant_rar = assistant_rar.replace('/raw/', '/tree/')            # Apuntar a la web de descargas
                browser, res = generictools.call_browser(assistant_rar, lookup=True)
                if browser:
                    filetools.remove(apk_install_SD, silent=True)
                    platformtools.dialog_ok("Alfa Assistant: Instale desde [COLOR yellow]%s[/COLOR]" % browser.capitalize(), 
                                    "O Instale manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_install_SD)
                    logger.info('Browser: %s, Ruta: %s' % (browser.capitalize(), apk_install_SD))
                    time.sleep(5)
                    browser, res = generictools.call_browser(assistant_rar, dataType='application/vnd.android.package-archive')
                    filetools.remove(apk_path, silent=True)
                    filetools.remove(upk_install_path, silent=True)
                else:
                    logger.error('Error de Instalación: NO Browser, Ruta: %s' % apk_install_SD)
                    raise
            else:
                logger.error('Error de Instalación: no se puede instalar en remoto: %s' % ASSISTANT_SERVER)
                raise
        except:
            if ASSISTANT_MODE == "este":
                platformtools.dialog_ok("Alfa Assistant: Error", "Instale manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_install_SD)
                logger.error("Alfa Assistant: Error. Instale manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_install_SD)
                filetools.remove(apk_path, silent=True)
                filetools.remove(upk_install_path, silent=True)
            else:
                platformtools.dialog_ok("Alfa Assistant: Error", "Copie a Android manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_apk)
                logger.error("Alfa Assistant: Error. Copie a Android manualmente desde: [COLOR yellow]%s[/COLOR]" % apk_apk)
            logger.error(traceback.format_exc(1))

    if respuesta:
        if update:
            if verbose or not isinstance(update, bool): platformtools.dialog_notification("Alfa Assistant", \
                                "Actualización con exito: %s" % respuesta)
            logger.info("Actualización terminada con éxito: %s" % respuesta)
        else:
            platformtools.dialog_notification("Alfa Assistant", "Instalación con exito: %s" % respuesta)
            logger.info("Instalación terminada con éxito: %s" % respuesta)
        filetools.remove(apk_path, silent=True)
        filetools.remove(apk_install_SD, silent=True)
        filetools.remove(upk_install_path, silent=True)
        if not update and not forced_menu:
            time.sleep(1)
            check_permissions_alfa_assistant()
            time.sleep(1)
        if app_active and ASSISTANT_MODE == "este":
            execute_in_alfa_assistant_with_cmd('open')                          # re-activamos la app para dejarla como estaba
        
    return respuesta, app_name
