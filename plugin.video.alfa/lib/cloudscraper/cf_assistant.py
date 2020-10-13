# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# cloudscaper+alfa_assistant
# ------------------------------------------------------------------------------

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from lib import alfa_assistant
from core import httptools, scrapertools
from platformcode import logger, config

def get_cl(resp, timeout=20, debug=False, extraPostDelay=15, retry=True):
    check_assistant = alfa_assistant.open_alfa_assistant(getWebViewInfo=True)
    if check_assistant and isinstance(check_assistant, dict):
        
        ua = get_ua(check_assistant)
        
        try:
            vers = int(scrapertools.find_single_match(ua, r"Android\s*(\d+)"))
        except:
            vers = 0

        if vers:
            dan = {'User-Agent': ua}
            resp.headers.update(dict(dan))
            ua = None
        else:
            ua = httptools.get_user_agent()

        logger.debug("UserAgent: %s || Android Vrs: %s" % (ua, vers))
        
        jscode = get_jscode(1, 'KEYCODE_ENTER', 1)

        data_assistant = alfa_assistant.get_source_by_page_finished(resp.url, timeout=timeout, getCookies=True, userAgent=ua,
                                                                    disableCache=True, debug=debug, jsCode=jscode,
                                                                    extraPostDelay=extraPostDelay, clearWebCache=True, 
                                                                    removeAllCookies=True
                                                                    )
        
        logger.debug("data assistant: %s" % data_assistant)
        
        domain = urlparse(resp.url).netloc
        domain_ = domain
        split_lst = domain.split(".")

        if len(split_lst) > 2:
            domain = domain.replace(split_lst[0], "")
        
        if not domain.startswith('.'):
            domain = "."+domain
        
        get_ua(data_assistant)

        if isinstance(data_assistant, dict) and data_assistant.get("cookies", None):
            
            for cookie in data_assistant["cookies"]:
                cookieslist = cookie.get("cookiesList", None)
                val = scrapertools.find_single_match(cookieslist, 'cf_clearance=([A-z0-9_-]+)')
                dom = cookie.get("urls", None)
                #logger.debug("dominios: %s" % dom[0])
                #logger.debug("Lista cookies: %s" % cookieslist)

                if 'cf_clearance' in cookieslist and val:
                    
                    dict_cookie = {'domain': domain,
                                   'name': 'cf_clearance',
                                   'value': val}
                    if domain_ in dom[0]:
                        httptools.set_cookies(dict_cookie)
                        rin = {'Server': 'Alfa'}

                        resp.headers.update(dict(rin))
                        #logger.debug("cf_clearence=%s" %s val)

                        return resp
                    else:
                        logger.error("No cf_clearance for %s" % domain_)

                else: 
                    logger.error("No cf_clearance")
        else:
            logger.error("No Cookies o Error en conexión con Alfa Assistant")

        if retry:
            config.set_setting('cf_assistant_ua', '')
            logger.debug("No se obtuvieron resultados, reintentando...")
            return get_cl(resp, timeout=timeout-5, extraPostDelay=extraPostDelay, retry=False,
                         )



    msg = 'Detected a Cloudflare version 2 Captcha challenge,\
        This feature is not available in the opensource (free) version.'
    
    resp.status_code = msg

    logger.error('Detected a Cloudflare version 2 Hcaptcha challenge')
    
    return False

def get_ua(data_assistant):
    
    if not data_assistant or not isinstance(data_assistant, dict):
        return 'Default'
    
    UA = data_assistant.get("userAgent", 'Default')
    
    if UA == httptools.get_user_agent():
        UA = 'Default'

    config.set_setting('cf_assistant_ua', UA)

    return UA

def get_jscode(count, key, n_iframe, timeout=3):
    
    count = str(count)
    focus = str(n_iframe)
    timeout = str(timeout * 1000)

    js = '''((() => {

    const KEYCODE_ENTER = 'KEYCODE_ENTER';
    const KEYCODE_TAB = 'KEYCODE_TAB';

    function sendKeyAfterNTabs(count, key) {
        try {
            for (var i = 0; i <= count; i++) {
                if (i > 0) {
                    alfaAssistantAndroidPI.sendKey(KEYCODE_TAB);
                }
                if (i == count) {
                    alfaAssistantAndroidPI.sendKey(key);
                    break;
                }
            }
        } catch (e) {
            console.error('##Error sending key ' + key, e);
        };
    };

   function setFocusToIframeNumber(nmb) {
    document.querySelectorAll('iframe')[nmb - 1].focus();
   }
    try {

        setFocusToIframeNumber('''+ focus +''');

        sendKeyAfterNTabs('''+ count +''', '''+ key +''');

        setTimeout(function() { 
            window.location.href = alfaAssistantAndroidPI.getMainURL();
            }, '''+ timeout +''');
    }
    catch(e){
            console.error('##Error focus ', e);
        };
}))();
'''
    return js
