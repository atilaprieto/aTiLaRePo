# -*- coding: utf-8 -*-
import cookielib
import gzip
import httplib
import inspect
import ssl
import aes
import urlparse
from HTMLParser import HTMLParser
from StringIO import StringIO
from threading import Lock
from decimal import Decimal


from libs.tools import *



cookies_lock = Lock()
cj = cookielib.MozillaCookieJar()
cookies_path = os.path.join(data_path, "cookies.dat")

# Headers por defecto, si no se especifica nada
default_headers = dict()
default_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0"
default_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
default_headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
default_headers["Accept-Charset"] = "UTF-8"
default_headers["Accept-Encoding"] = "gzip"

# No comprobar certificados
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def get_cloudflare_headers(url):
    """
    Añade los headers para cloudflare
    :param url: Url
    :type url: str
    """
    domain_cookies = cj._cookies.get("." + urlparse.urlparse(url)[1], {}).get("/", {})

    if "cf_clearance" not in domain_cookies:
        return url

    headers = dict()
    headers["User-Agent"] = default_headers["User-Agent"]
    headers["Cookie"] = "; ".join(["%s=%s" % (c.name, c.value) for c in domain_cookies.values()])

    return url + '|%s' % '&'.join(['%s=%s' % (k, v) for k, v in headers.items()])


def load_cookies():
    """
    Carga el fichero de cookies
    """
    cookies_lock.acquire()

    if os.path.isfile(cookies_path):
        try:
            cj.load(cookies_path, ignore_discard=True)
        except Exception:
            logger("El fichero de cookies existe pero es ilegible, se borra")
            os.remove(cookies_path)

    cookies_lock.release()


def save_cookies():
    """
    Guarda las cookies
    """
    cookies_lock.acquire()
    #if xbmcgui.Dialog().yesno('1x2', 'guardo?'):
    cj.save(cookies_path, ignore_discard=True)
    cookies_lock.release()


def get_cookies(domain):
    return dict((c.name, c.value) for c in cj._cookies.get("." + domain, {}).get("/", {}).values())

'''
def get_hash(url=None, data='', algorithm='md5', max_file_size= 104857600):
    import hashlib

    if url:
        url = url.split('|')[0]
        data = downloadpage(url).data
    if algorithm == "sha1":
        hash = hashlib.sha1()
    elif algorithm == "sha256":
        hash = hashlib.sha256()
    elif algorithm == "sha384":
        hash = hashlib.sha384()
    elif algorithm == "sha512":
        hash = hashlib.sha512()
    else:
        hash = hashlib.md5()
    
    total_read = 0
    ini_read = 0
    while True:
        total_read += 4096
        data = data[ini_read:total_read]

        if not data or total_read > max_file_size:
            break

        hash.update(data)
        ini_read = total_read

    return hash.hexdigest()
'''

def downloadpage(url, post=None, headers=None, timeout=None, follow_redirects=True, cookies=True, replace_headers=False,
                 add_referer=False, only_headers=False, bypass_cloudflare=True, bypass_testcookie=True, no_decode=False,
                 method=None):
    """
    Descarga una página web y devuelve los resultados
    :type url: str
    :type post: dict, str
    :type headers: dict, list
    :type timeout: int
    :type follow_redirects: bool
    :type cookies: bool, dict
    :type replace_headers: bool
    :type add_referer: bool
    :type only_headers: bool
    :type bypass_cloudflare: bool
    :return: Resultado
    """
    arguments = locals().copy()

    response = {}

    # Post tipo dict
    if type(post) == dict:
        post = urllib.urlencode(post)

    # Url quote
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")

    # Headers por defecto, si no se especifica nada
    request_headers = default_headers.copy()

    # Headers pasados como parametros
    if headers is not None:
        if not replace_headers:
            request_headers.update(dict(headers))
        else:
            request_headers = dict(headers)

    # Referer
    if add_referer:
        request_headers["Referer"] = "/".join(url.split("/")[:3])

    #logger("Headers:")
    #logger(request_headers, 'info')

    # Handlers
    handlers = list()
    handlers.append(HTTPHandler(debuglevel=False))

    # No redirects
    if not follow_redirects:
        handlers.append(NoRedirectHandler())
    else:
        handlers.append(HTTPRedirectHandler())

    # Dict con cookies para la sesión
    if type(cookies) == dict:
        for name, value in cookies.items():
            if not type(value) == dict:
                value = {'value': value}
            ck = cookielib.Cookie(
                version=0,
                name=name,
                value=value.get('value', ''),
                port=None,
                port_specified=False,
                domain=value.get('domain', urlparse.urlparse(url)[1]),
                domain_specified=False,
                domain_initial_dot=False,
                path=value.get('path', '/'),
                path_specified=True,
                secure=False,
                expires=value.get('expires', time.time() + 3600 * 24),
                discard=True,
                comment=None,
                comment_url=None,
                rest={'HttpOnly': None},
                rfc2109=False
            )
            cj.set_cookie(ck)

    if cookies:
        handlers.append(urllib2.HTTPCookieProcessor(cj))

    # Opener
    opener = urllib2.build_opener(*handlers)

    # Contador
    inicio = time.time()

    # Request
    req = Request(url, post, request_headers, method=method)

    try:
        #logger("Realizando Peticion")
        handle = opener.open(req, timeout=timeout)
        #logger('Peticion realizada')

    except urllib2.HTTPError, handle:
        #logger('Peticion realizada con error')
        response["sucess"] = False
        response["code"] = handle.code
        response["error"] = handle.__dict__.get("reason", str(handle))
        response["headers"] = handle.headers.dict
        response['cookies'] = get_cookies(urlparse.urlparse(url)[1])
        if not only_headers:
            #logger('Descargando datos...')
            response["data"] = handle.read()
        else:
            response["data"] = ""
        response["time"] = time.time() - inicio
        response["url"] = handle.geturl()

    except Exception, e:
        #logger('Peticion NO realizada')
        response["sucess"] = False
        response["code"] = e.__dict__.get("errno", e.__dict__.get("code", str(e)))
        response["error"] = e.__dict__.get("reason", str(e))
        response["headers"] = {}
        response['cookies'] = get_cookies(urlparse.urlparse(url)[1])
        response["data"] = ""
        response["time"] = time.time() - inicio
        response["url"] = url

    else:
        response["sucess"] = True
        response["code"] = handle.code
        response["error"] = None
        response["headers"] = handle.headers.dict
        response['cookies'] = get_cookies(urlparse.urlparse(url)[1])
        if not only_headers:
            #logger('Descargando datos...')
            response["data"] = handle.read()
        else:
            response["data"] = ""
        response["time"] = time.time() - inicio
        response["url"] = handle.geturl()

    #logger("Terminado en %.2f segundos" % (response["time"]))
    #logger("Response sucess     : %s" % (response["sucess"]))
    #logger("Response code       : %s" % (response["code"]))
    #logger("Response error      : %s" % (response["error"]))
    #logger("Response data length: %s" % (len(response["data"])))
    #logger("Response headers:")
    #logger(response['headers'])

    # Guardamos las cookies
    if cookies:
        save_cookies()

    # Gzip
    if response["headers"].get('content-encoding') == 'gzip':
        response["data"] = gzip.GzipFile(fileobj=StringIO(response["data"])).read()

    if not no_decode:
        try:
            response["data"] = HTMLParser().unescape(unicode(response["data"], 'utf8')).encode('utf8')
        except Exception:
            pass

    # Anti TestCookie
    if bypass_testcookie:

        if 'document.cookie="__test="+toHex(slowAES.decrypt(c,2,a,b))+"' in response['data']:
            a = re.findall('a=toNumbers\("([^"]+)"\)', response['data'])[0].decode("HEX")
            b = re.findall('b=toNumbers\("([^"]+)"\)', response['data'])[0].decode("HEX")
            c = re.findall('c=toNumbers\("([^"]+)"\)', response['data'])[0].decode("HEX")

            arguments['bypass_testcookie'] = False
            if not type(arguments['cookies']) == dict:
                arguments['cookies'] = {'__test': aes.AESModeOfOperationCBC(a, b).decrypt(c).encode("HEX")}
            else:
                arguments['cookies']['__test'] = aes.AESModeOfOperationCBC(a, b).decrypt(c).encode("HEX")
            response = downloadpage(**arguments).__dict__

    # Anti Cloudflare
    if bypass_cloudflare:
        response = retry_if_cloudflare(response, arguments)
        

    return HTTPResponse(response)


def retry_if_cloudflare(response, args):
    cf = Cloudflare(response)

    if cf.is_cloudflare:
        logger("cloudflare detectado, esperando %s segundos..." % cf.wait_time)
        auth_url = cf.get_url()
        #logger("Autorizando... url: %s" % auth_url)
        auth_args = args.copy()
        auth_args['url'] = auth_url
        auth_args['follow_redirects'] = False
        auth_args['headers'] = {'Referer': args['url']}

        resp = downloadpage(**auth_args)
        if resp.sucess:
            logger("cloudflare: Autorización correcta, descargando página")
            args['bypass_cloudflare'] = False
            return downloadpage(**args).__dict__
        elif resp.code == 403 and resp.headers.get('cf-chl-bypass'):
            if [a[3] for a in inspect.stack()].count('retry_if_cloudflare') > 2:
                logger("cloudflare: No se ha podido autorizar. Demasiados intentos")
                return response
            #logger("Reintentando...")
            return downloadpage(**args).__dict__
        else:
            logger("cloudflare: No se ha podido autorizar")
    return response


class HTTPHandler(urllib2.HTTPHandler):
    def http_open(self, req):
        return self.do_open(HTTPConnection, req)


class HTTPConnection(httplib.HTTPConnection):
    def _send_request(self, method, url, body, headers):
        # Honor explicitly requested Host: and Accept-Encoding: headers.
        header_names = dict.fromkeys([k.lower() for k in headers])
        skips = {}
        if 'host' in header_names:
            skips['skip_host'] = 1
        if 'accept-encoding' in header_names:
            skips['skip_accept_encoding'] = 1

        self.putrequest(method, url, **skips)

        if 'content-length' not in header_names:
            self._set_content_length(body, method)

        order = ["Host", 'User-Agent', 'Accept', 'Accept-Language', 'Accept-Encoding']

        for hdr, value in sorted(headers.items(), lambda x, y: cmp(order.index(x[0]) if x[0] in order else len(order),
                                                                   order.index(y[0]) if y[0] in order else len(order))):
            self.putheader(hdr, value)

        self.endheaders(body)


class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl

    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if 'Authorization' in req.headers:
            req.headers.pop('Authorization')
        return urllib2.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)


class HTTPResponse:
    def __init__(self, response):
        self.sucess = None
        self.code = None
        self.error = None
        self.headers = None
        self.cookies = None
        self.data = None
        self.time = None
        self.url = None
        self.__dict__ = response


class Request(urllib2.Request):
    def __init__(self, *args, **kwargs):
        self.method = None
        if 'method' in kwargs:
            self.method = kwargs.pop('method')
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        if self.method:
            return self.method.upper()

        if self.has_data():
            return "POST"
        else:
            return "GET"



class Cloudflare:
    def __init__(self, response):
        self.timeout = 5
        self.domain = urlparse.urlparse(response["url"])[1]
        self.protocol = urlparse.urlparse(response["url"])[0]
        self.response = response
        self.js_data = {}
        self.header_data = {}

        if not "var s,t,o,p,b,r,e,a,k,i,n,g,f" in response["data"] or "chk_jschl" in response["url"]:
            return

        try:
            self.js_data["auth_url"] = \
            re.compile('<form id="challenge-form" action="([^"]+)" method="get">').findall(response["data"])[0]
            self.js_data["params"] = {}
            self.js_data["params"]["jschl_vc"] = \
            re.compile('<input type="hidden" name="jschl_vc" value="([^"]+)"').findall(response["data"])[0]
            self.js_data["params"]["pass"] = \
            re.compile('<input type="hidden" name="pass" value="([^"]+)"').findall(response["data"])[0]
            self.js_data["params"]["s"] = \
            re.compile('<input type="hidden" name="s" value="([^"]+)"').findall(response["data"])[0]

            var, self.js_data["value"] = \
            re.compile('var s,t,o,p,b,r,e,a,k,i,n,g,f[^:]+"([^"]+)":([^\n]+)};', re.DOTALL).findall(response["data"])[0]
            # ~ logger(var)
            # ~ logger(self.js_data["value"])

            # Modificar function(p){... per algun valor
            self.js_data["old_way"] = True
            if 'function(p){var p =' in response["data"]:
                var_k = re.compile("k = '([^']+)';").findall(response["data"])[0]
                k_value = re.compile(' id="%s">(.*?)</div>' % var_k).findall(response["data"])[0]
                response["data"] = re.sub('function\(p\)\{var p =.*?\}\(\)', k_value, response["data"])
                self.js_data["old_way"] = False

            if '(function(p){return' in response["data"]:
                var_num = re.compile("\(function\(p\)\{return.*?\}\((.*?)\)\)\);").findall(response["data"])[0]
                var_num = int(self.decode(var_num + '/+(+1)'))
                valor = ord(self.domain[var_num])
                response["data"] = re.sub('\(function\(p\)\{return.*?\}\(.*?\)\)\);', '(' + str(valor) + '));',
                                          response["data"])
                self.js_data["old_way"] = False

            # ~ logger(response["data"])

            self.js_data["op"] = re.compile(var + "([\+|\-|\*|\/])=([^;]+)", re.MULTILINE).findall(response["data"])
            self.js_data["wait"] = int(re.compile("\}, ([\d]+)\);", re.MULTILINE).findall(response["data"])[0]) / 1000
        except:
            logger("Metodo #1 (javascript): NO disponible")
            self.js_data = {}

        if "refresh" in response["headers"]:
            try:
                self.header_data["wait"] = int(response["headers"]["refresh"].split(";")[0])
                self.header_data["auth_url"] = response["headers"]["refresh"].split("=")[1].split("?")[0]
                self.header_data["params"] = {}
                self.header_data["params"]["pass"] = response["headers"]["refresh"].split("=")[2]
            except:
                logger("Metodo #2 (headers): NO disponible")
                self.header_data = {}

    @property
    def wait_time(self):
        if self.js_data.get("wait", 0):
            return self.js_data["wait"]
        else:
            return self.header_data.get("wait", 0)

    @property
    def is_cloudflare(self):
        # return self.response['code'] == 503 and bool(self.header_data or self.js_data)
        return self.header_data.get("wait", 0) > 0 or self.js_data.get("wait", 0) > 0


    def get_url(self):
        # Metodo #1 (javascript)
        if self.js_data.get("wait", 0):
            jschl_answer = self.decode(self.js_data["value"])
            # ~ logger(jschl_answer)

            for op, v in self.js_data["op"]:
                # ~ logger('op: %s v: %s decoded: %f' % (op, v, self.decode(v)))
                if op == '+':
                    jschl_answer = jschl_answer + self.decode(v)
                elif op == '-':
                    jschl_answer = jschl_answer - self.decode(v)
                elif op == '*':
                    jschl_answer = jschl_answer * self.decode(v)
                elif op == '/':
                    jschl_answer = jschl_answer / self.decode(v)
                # ~ logger(jschl_answer)

            if self.js_data["old_way"]:
                self.js_data["params"]["jschl_answer"] = round(jschl_answer, 10) + len(self.domain)
            else:
                self.js_data["params"]["jschl_answer"] = round(jschl_answer, 10)
            # ~ logger(jschl_answer)

            response = "%s://%s%s?%s" % (
            self.protocol, self.domain, self.js_data["auth_url"], urllib.urlencode(self.js_data["params"]))
            # ~ logger(response)

            time.sleep(self.js_data["wait"])

            return response

        # Metodo #2 (headers)
        if self.header_data.get("wait", 0):
            response = "%s://%s%s?%s" % (
                self.protocol, self.domain, self.header_data["auth_url"], urllib.urlencode(self.header_data["params"]))

            time.sleep(self.header_data["wait"])

            return response

    def decode(self, data):
        data = re.sub("\!\+\[\]", "1", data)
        data = re.sub("\!\!\[\]", "1", data)
        data = re.sub("\[\]", "0", data)

        pos = data.find("/")
        numerador = data[:pos]
        denominador = data[pos + 1:]

        aux = re.compile('\(([0-9\+]+)\)').findall(numerador)
        num1 = ""
        for n in aux:
            num1 += str(eval(n))

        aux = re.compile('\(([0-9\+]+)\)').findall(denominador)
        num2 = ""
        for n in aux:
            # ~ num2 += str(eval(n))
            # ~ logger(n)
            if '+' in n:
                num2 += str(eval(n))
            else:
                num2 = str(int(num2) + int(n))

        # ~ logger(num1); logger(num2)
        return Decimal(Decimal(num1) / Decimal(num2)).quantize(Decimal('.0000000000000001'))
