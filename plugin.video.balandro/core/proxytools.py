# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    PY3 = False
else:
    PY3 = True


import os, time, re

from threading import Thread

from core import httptools, scrapertools
from platformcode import config, logger, platformtools

default_provider = 'proxyscrape.com'
all_providers = 'All-providers'
private_list = 'lista_proxies.txt'

opciones_provider = ['spys.me',
        'hidemy.name',
        'httptunnel.ge',
        'proxynova.com',
        'free-proxy-list',
        'spys.one',
        default_provider,
        'proxyservers.pro',
        'proxy-list.download',
        'us-proxy.org',
        all_providers,
        private_list]

opciones_tipo = ['Cualquier tipo', 'Elite', 'Anonymous', 'Transparent']
opciones_pais = ['Cualquier país', 'ES', 'US', 'FR', 'DE', 'CZ', 'IT', 'CH', 'NL', 'MX', 'RU', 'HK', 'SG'] #TODO completar

proxies_auto = config.get_setting('proxies_auto', default=True)
proxies_limit = config.get_setting('proxies_limit', default=True)

proxies_provider = config.get_setting('proxies_provider', default='10')
if proxies_provider == 10:
     proxies_todos = True
else:
     proxies_todos = False

proxies_tipos = config.get_setting('proxies_tipos', default=False)
proxies_paises = config.get_setting('proxies_paises', default=False)
proxies_maximo = config.get_setting('proxies_maximo', default=True)
proxies_list =  config.get_setting('proxies_list', default=False)
proxies_help = config.get_setting('proxies_help', default=True)

if not proxies_list:
    opciones_provider.remove(private_list)


# Parámetros proxytools_ específicos del canal
def get_settings_proxytools(canal):
    provider = config.get_setting('proxytools_provider', canal, default=default_provider)
    if proxies_auto:
        if not proxies_todos:
            provider_fijo = opciones_provider[proxies_provider]
            provider = provider_fijo

    tipo_proxy = config.get_setting('proxytools_tipo', canal, default='')
    pais_proxy = config.get_setting('proxytools_pais', canal, default='')

    if proxies_maximo: valor = 50
    else:
       valor = 20

    max_proxies = config.get_setting('proxytools_max', canal, default=valor)

    return provider, tipo_proxy, pais_proxy, max_proxies


# Diálogo principal para configurar los proxies de un canal concreto
def configurar_proxies_canal(canal, url):
    logger.info()

    if proxies_auto:
        proxies_actuales = config.get_setting('proxies', canal, default='').strip()

        if proxies_todos:
            provider_auto = all_providers
            proxies_nuevos = ''

            _buscar_proxies(canal, url, provider_auto)
            config.set_setting('proxytools_provider', provider_auto, canal)

            proxies_encontrados = config.get_setting('proxies', canal, default='').strip()

            if proxies_nuevos: proxies_nuevos = proxies_nuevos + ', '
            proxies_nuevos = proxies_nuevos + proxies_encontrados

            if proxies_nuevos:
                cuantos_proxies(canal, provider_auto, proxies_nuevos)
            else:
                sin_news_proxies(provider_auto, proxies_actuales)

        else:
            provider_fijo = opciones_provider[proxies_provider]

            if _buscar_proxies(canal, url, provider_fijo):
                config.set_setting('proxytools_provider', provider_fijo, canal)

                proxies_nuevos = config.get_setting('proxies', canal, default='').strip()

                cuantos_proxies(canal, provider_fijo, proxies_nuevos)
            else:
                sin_news_proxies(provider_fijo, proxies_actuales)

    # Aunque venga por automático y haya localizado nuevos proxies, hay que entrar por si se modifican o se quitan, o pq no van bien
    while True:
        proxies = config.get_setting('proxies', canal, default='').strip()

        provider, tipo_proxy, pais_proxy, max_proxies = get_settings_proxytools(canal)

        if provider == private_list:
            tipo_proxy = '-'
            pais_proxy = '-'
        else:
            tipo_proxy = opciones_tipo[0] if tipo_proxy == '' else tipo_proxy.capitalize()
            pais_proxy = opciones_pais[0] if pais_proxy == '' else pais_proxy

        acciones = []

        lbl = proxies if proxies else '(sin proxies)'
        if lbl == '(sin proxies)': texto = 'Informar proxies manualmente'
        else: texto = 'Modificar proxies manualmente'

        acciones.append(platformtools.listitem_to_select(texto, lbl, ''))
        acciones.append(platformtools.listitem_to_select('[COLOR moccasin]Buscar nuevos proxies[/COLOR]', 'Buscar con parámetros actuales (Guardará los mejores)'))
        acciones.append(platformtools.listitem_to_select('[COLOR cyan]Parámetros búsquedas[/COLOR] proveedor, tipo, país, ...', '%s, %s, %s, %d' % (provider, tipo_proxy, pais_proxy, max_proxies), ''))

        if proxies:
            acciones.append(platformtools.listitem_to_select('[COLOR red]Quitar proxies[/COLOR]', 'Suprimir proxies actuales para probar el canal sin ellos'))

        acciones.append(platformtools.listitem_to_select('[COLOR blue]Configuración[/COLOR]', '[COLOR mediumaquamarine]Si la modifica debe abandonar por cancelar[/COLOR]'))

        if proxies_help:
            acciones.append(platformtools.listitem_to_select('Ayuda', 'Informacion sobre la gestión de proxies'))

        ret = platformtools.dialog_select('Configuración proxies para %s' % canal.capitalize(), acciones, useDetails=True)

        if ret == -1: # cancel
            break

        elif ret == 0:
            new_proxies = platformtools.dialog_input(default=proxies, heading='Indicar el proxy a utilizar o varios separados por comas')
            if new_proxies:
                if not '.' in new_proxies or not ':' in new_proxies:
                    platformtools.dialog_notification(canal, 'Formato proxy inválido')
                    new_proxies = ''

            if new_proxies and new_proxies != proxies:
                config.set_setting('proxies', new_proxies, canal)
                break

        elif ret == 1:
            search_provider = True
            if proxies_auto:
                if proxies_todos: search_provider = False
            elif provider == all_providers: search_provider = False

            if not search_provider:
                if platformtools.dialog_yesno(config.__addon_name, '¿ Desea iniciar la búsqueda de proxies en todos los proveedores ?'):
                    search_provider = True

            if search_provider:
                if _buscar_proxies(canal, url, provider): break # si no se encuentran proxies válidos seguir para poder cambiar parámetros o entrar manualmente

        elif ret == 2:
            _settings_proxies_canal(canal, opciones_provider)

        else:
            if ret == 3:
                if proxies:
                    config.set_setting('proxies', '', canal)
                else:
                    configuracion_general()

            elif ret == 4:
                if proxies:
                    configuracion_general()
                else:
                    show_help_proxies()
            elif ret == 5:					
                show_help_proxies()

    return True


# Diálogos para guardar las diferentes opciones de búsqueda
def _settings_proxies_canal(canal, opciones_provider):
    provider, tipo_proxy, pais_proxy, max_proxies = get_settings_proxytools(canal)

    preselect = 0 if provider not in opciones_provider else opciones_provider.index(provider)
    ret = platformtools.dialog_select('Proveedores de proxies', opciones_provider, preselect=preselect)
    if ret == -1: return False

    provider = opciones_provider[ret]
    config.set_setting('proxytools_provider', provider, canal)

    if provider == private_list:
        config.set_setting('proxytools_max', 50, canal)
        return True

    if not proxies_tipos:
        ret = 0
    else:
        preselect = 0 if tipo_proxy.capitalize() not in opciones_tipo else opciones_tipo.index(tipo_proxy.capitalize())
        ret = platformtools.dialog_select('Tipo de anonimidad de los proxies', opciones_tipo, preselect=preselect)
        if ret == -1: return False

    tipo_proxy = '' if ret == 0 else opciones_tipo[ret].lower()

    config.set_setting('proxytools_tipo', tipo_proxy, canal)

    if not proxies_paises:
        ret = 0
    else:
        preselect = 0 if pais_proxy not in opciones_pais else opciones_pais.index(pais_proxy)
        ret = platformtools.dialog_select('País de los proxies', opciones_pais, preselect=preselect)
        if ret == -1: return False

    pais_proxy = '' if ret == 0 else opciones_pais[ret]

    config.set_setting('proxytools_pais', pais_proxy, canal)

    if proxies_maximo:
        config.set_setting('proxytools_max', 50, canal)
        return True

    try:
        max_proxies = int(platformtools.dialog_numeric(0, 'Valor máximo de proxies a analizar (tope 50)', '20'))
        if ret == -1: return False

        if max_proxies < 3 or max_proxies > 50:
            platformtools.dialog_notification(canal, 'Valor incorrecto, mínimo 3, máximo 50')
            max_proxies = 20
            if proxies_maximo:
                max_proxies = 50
    except:
        max_proxies = 20
        if proxies_maximo:
            max_proxies = 50

    config.set_setting('proxytools_max', max_proxies, canal)

    return True


def _buscar_proxies(canal, url, provider):
    proxies_actuales = config.get_setting('proxies', canal, default='').strip()

    if url == '': url = 'http://httpbin.org/ip'

    provider_canal, tipo_proxy, pais_proxy, max_proxies = get_settings_proxytools(canal)

    # Obtener lista de proxies
    all_providers_proxies = []

    search_provider = False
    if proxies_auto:
        if proxies_todos: search_provider = True
    elif provider == all_providers: search_provider = True

    if search_provider:
        platformtools.dialog_notification('Buscar proxies', '[COLOR blue]Obteniendo proxies espere ...[/COLOR]')

    if search_provider or provider == 'spys.one':
        proxies = _spys_one(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'hidemy.name':
        proxies = _hidemy_name(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'httptunnel.ge':
        proxies = _httptunnel_ge(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'proxynova.com':
        proxies = _proxynova_com(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'free-proxy-list':
        proxies = _free_proxy_list(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'spys.me':
        proxies = _spys_me(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == default_provider:
        proxies = _proxyscrape_com(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'proxyservers.pro':
        proxies = _proxyservers_pro(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'proxy-list.download':
        proxies = _proxy_list_download(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)

    if search_provider or provider == 'us-proxy.org':
        proxies = _us_proxy_org(url, tipo_proxy, pais_proxy, max_proxies)
        if proxies:
            all_providers_proxies = acumulaciones(provider, proxies, all_providers_proxies, max_proxies)


    # fichero personal de proxies en userdata (separados por comas o saltos de línea)
    if provider == private_list:
        proxies = obtener_private_list()
    else:
        if not provider:
            if not search_provider:
                platformtools.dialog_notification('Buscar proxies', '[COLOR red]Parámetros desconocidos[/COLOR]')
                return False

    if not all_providers_proxies:
        if not proxies:
            platformtools.dialog_notification('Buscar proxies ' + provider.capitalize(), '[COLOR coral]Sin proxies según parámetros[/COLOR]')
            return False

    # Limitar proxies y validar formato
    if not PY3:
        proxies = filter(lambda x: re.match('\d+\.\d+\.\d+\.\d+\:\d+', x), proxies)
    else:
        proxies = re.compile('\d+\.\d+\.\d+\.\d+\:\d+', re.DOTALL).findall(str(proxies))

    if max_proxies: proxies = proxies[:max_proxies]
    # ~ logger.debug(proxies)

    # Testear proxies
    if search_provider:
        proxies = all_providers_proxies

        if len(proxies) > 50:
            platformtools.dialog_notification('Buscar proxies', '[COLOR blue]Cargando proxies espere ...[/COLOR]')

        tot_proxies = len(proxies)
        if tot_proxies >= 500: tot_proxies = 500
        if max_proxies: proxies = proxies[:tot_proxies]

    nom_provider = provider
    if search_provider: nom_provider = all_providers

    proxies_info = testear_lista_proxies(nom_provider, url, proxies)

    # Guardar mejores proxies en la configuración del canal
    selected = []

    for proxy, info in proxies_info:
        if not info['ok']: break
        selected.append(proxy)

        proxies_validos = config.get_setting('proxies_validos', default=True)
        if proxies_validos:
           if not search_provider:
              if len(selected) >= 3: break # los 3 más rápidos
           else:
              if proxies_limit:
                 if len(selected) >= 10: break # si todos los 10 más rápidos
              else: 
                 if len(selected) >= 3: break # los 3 más rápidos
        else:
           if proxies_limit:
               if len(selected) >= 10: break # si todos los 10 más rápidos
           else: 
               if len(selected) >= 3: break # los 3 más rápidos

    if len(selected) > 0:
        config.set_setting('proxies', ', '.join(selected), canal)
        logger.info('Proxies actualizados %s : %s' % (canal, ', '.join(selected)))
        platformtools.dialog_notification('Buscar proxies', '[COLOR blue]%s[/COLOR][COLOR gold] proxies actualizados[/COLOR]' % canal.capitalize())
    else:
        if not proxies_actuales:
            avisar = True
            if proxies_auto:
                if proxies_todos: avisar = False
            elif provider == all_providers: avisar = False

            if avisar:
                 platformtools.dialog_notification('Buscar proxies', '[COLOR red]Sin localizar proxies válidos[/COLOR]')
        else:
            if provider == private_list:
                platformtools.dialog_notification('Buscar proxies', 'Sin proxies válidos [COLOR red]en su lista[/COLOR]')

    # Apuntar resultados en proxies.log
    if config.get_setting('developer_mode', default=False):
        proxies_log = os.path.join(config.get_data_path(), 'proxies.log')

        txt_log = os.linesep + '%s Buscar proxies en %s para %s' % (time.strftime("%Y-%m-%d %H:%M"), nom_provider, url) + os.linesep
        if provider != '': txt_log += provider + os.linesep

        num_ok = 0
        for proxy, info in proxies_info:
            txt_log += '%s ~ %s ~ %.2f segundos ~ %s ~ %d bytes' % (proxy, info['ok'], info['time'], info['code'], info['len']) + os.linesep
            if info['ok']: num_ok += 1

        txt_log += 'Búsqueda finalizada. Proxies válidos: %d' % (num_ok) + os.linesep

        with open(proxies_log, 'a') as f: f.write(txt_log); f.close()

    if not provider == private_list:
        if len(selected) == 0:
            sin_news_proxies(nom_provider, proxies_actuales)
        elif len(selected) >= 10:
            valor = str(len(selected))
            top_news_proxies(nom_provider, proxies_actuales, valor)

    return True if len(selected) > 0 else False


def cuantos_proxies(canal, provider, proxies_actuales):
    cuantos = config.get_setting('proxies', canal, default='').strip()
    cuantos = cuantos.split(',')

    if cuantos:
        valor = str(len(cuantos))
        top_news_proxies(provider, proxies_actuales, valor)

def sin_news_proxies(provider, proxies_actuales):
    avisar = True
    if proxies_auto:
        if proxies_todos: avisar = False
    else:
        if provider == all_providers: avisar = True

    if avisar:
        texto_mensaje = ''
        if proxies_actuales: texto_mensaje = '[COLOR yellow]Se conservan los proxies almacenados actualmente.[/COLOR]'
        platformtools.dialog_ok('Búsqueda proxies en [COLOR blue]' + provider.capitalize() + '[/COLOR]', 'No se ha obtenido ningún proxy válido con este proveedor.', texto_mensaje, '[COLOR coral]Puede intentar obtener nuevos proxies, cambiando de proveedor, en los parámetros para buscar proxies.[/COLOR]')

def top_news_proxies(provider, proxies_actuales, valor):
    avisar = True
    if proxies_auto:
        if proxies_todos: avisar = False
    else:
        if provider == all_providers: avisar = True

    if avisar:
        texto_mensaje = ''
        if proxies_actuales: texto_mensaje = '[COLOR yellow][B]El tiempo de espera acceso al canal podría ser muy elevado.[/B][/COLOR]'
        platformtools.dialog_ok('Búsqueda proxies en [COLOR blue]' + provider.capitalize() + '[/COLOR]', 'Se han obtenido ' + valor + ' proxies válidos con este proveedor.', texto_mensaje, '[COLOR coral]Puede intentar obtener menos proxies, cambiando de proveedor, en los parámetros para buscar proxies.[/COLOR]')


def _spys_one(url, tipo_proxy, pais_proxy, max_proxies):
    url_provider = 'https://spys.one/en/free-proxy-list/'
    url_post = 'xpp=0'
    if tipo_proxy == 'anonymous': url_post += 'xf1=3'
    elif tipo_proxy == 'transparent': url_post += 'xf1=2'
    elif tipo_proxy == 'elite': url_post += 'xf1=4'
    else: url_post += '&xf1=0'

    url_post += '&xf2=0&xf4=0&xf5=0'

    resp = httptools.downloadpage(url_provider, post=url_post, raise_weberror=False)

    valores = {}
    numeros = scrapertools.find_multiple_matches(resp.data, '([a-z0-9]{6})=(\d{1})\^')
    for a, b in numeros:
        valores[a] = b

    proxies = []
    enlaces = scrapertools.find_multiple_matches(resp.data, '<font class=spy14>(\d+\.\d+\.\d+\.\d+).*?font>"(.*?)</script>')
    for prox, resto in enlaces:
        puerto = ''
        numeros = scrapertools.find_multiple_matches(resto, '\+\(([a-z0-9]{6})\^')
        for a in numeros: puerto += str(valores[a])
        proxies.append(prox + ':' + puerto)

    return proxies

def _hidemy_name(url, tipo_proxy, pais_proxy, max_proxies):
    url_provider = 'https://hidemy.name/es/proxy-list/?'
    url_provider += 'type=' + ('s' if url.startswith('https') else 'h')
    if pais_proxy != '': url_provider += '&country=' + pais_proxy
    if tipo_proxy == 'anonymous': url_provider += '&anon=3'
    elif tipo_proxy == 'transparent': url_provider += '&anon=2'
    elif tipo_proxy == 'elite': url_provider += '&anon=4'
    else:  url_provider += '&anon=1'

    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    proxies = []
    enlaces = scrapertools.find_multiple_matches(resp.data, '<tr><td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td>')
    for prox, puerto in enlaces:
        proxies.append(prox + ':' + puerto)

    return proxies

def _httptunnel_ge(url, tipo_proxy, pais_proxy, max_proxies):
    url_provider = 'https://www.httptunnel.ge/ProxyListForFree.aspx'
    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    proxies = []

    enlaces = scrapertools.find_multiple_matches(resp.data, ' target="_new">(\d+\.\d+\.\d+\.\d+)\:(\d+)</a>.*?<td align="center"[^>]*>(T|A|E|U)</td>.*? src="images/flags/([^.]+)\.gif"')
    for prox, puerto, tipo, pais in enlaces:
        if tipo_proxy != '': 
            if tipo == 'T' and tipo_proxy != 'transparent': continue
            elif tipo == 'A' and tipo_proxy != 'anonymous': continue
            elif tipo == 'E' and tipo_proxy != 'elite': continue
        if pais_proxy != '': 
            if pais != pais_proxy: continue

        proxies.append(prox+':'+puerto)

    return proxies

def _proxynova_com(url, tipo_proxy, pais_proxy, max_proxies):
    url_provider = 'https://www.proxynova.com/proxy-server-list/'
    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    proxies = []

    enlaces = scrapertools.find_multiple_matches(resp.data, "<script>document.write.*?'(.*?)'.*?<td align=.*?>(.*?)</td>")
    for prox, port in enlaces:
        port = port.strip()
        proxies.append(prox + ':' + port)

    return proxies

def _free_proxy_list(url, tipo_proxy, pais_proxy, max_proxies):
    url_provider = 'https://free-proxy-list.net'
    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    proxies = []

    block = scrapertools.find_single_match(resp.data, 'Updated at(.*?)</textarea>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')
    for prox in enlaces:
        if prox == '': continue
        elif  '-' in prox: continue
        proxies.append(prox)

    return proxies

def _spys_me(url, tipo_proxy, pais_proxy, max_proxies):
    url_provider = 'https://spys.me/proxy.txt'
    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    need_ssl = url.startswith('https')

    proxies = []
    enlaces = scrapertools.find_multiple_matches(resp.data, '(\d+\.\d+\.\d+\.\d+)\:(\d+) ([A-Z]{2})-((?:H|A|N){1}(?:!|))(.*?)\n')
    for prox, puerto, pais, tipo, resto in enlaces:
        if need_ssl and '-S' not in resto: continue
        if tipo_proxy != '': 
            if tipo == 'N' and tipo_proxy != 'transparent': continue
            elif tipo == 'A' and tipo_proxy != 'anonymous': continue
            elif tipo == 'H' and tipo_proxy != 'elite': continue
        if pais_proxy != '': 
            if pais != pais_proxy: continue

        proxies.append(prox + ':' + puerto)

    return proxies

def _proxyscrape_com(url, tipo_proxy, pais_proxy, max_proxies):
    # API: https://proxyscrape.com/api-documentation
    url_provider = 'https://api.proxyscrape.com/?request=displayproxies'
    url_provider += '&proxytype=' + ('https' if url.startswith('https') else 'http')  # http, socks4, socks5
    # ~ url_provider += '&ssl=' + ('yes' if url.startswith('https') else 'no')
    url_provider += '&ssl=all' # para evitar ssl=no ya que hay poquísimos proxies !?
    if tipo_proxy != '': url_provider += '&anonymity=' + tipo_proxy
    if pais_proxy != '': url_provider += '&country=' + pais_proxy

    resp = httptools.downloadpage(url_provider, raise_weberror=False)
    proxies = resp.data.split()

    return proxies

def _proxyservers_pro(url, tipo_proxy, pais_proxy, max_proxies):
    url_provider = 'https://es.proxyservers.pro/proxy/list?__path2query_param__='
    url_provider += '/protocol/' + ('https' if url.startswith('https') else 'http')
    if tipo_proxy != '': url_provider += '/anonymity/' + tipo_proxy
    if pais_proxy != '': url_provider += '/country/' + pais_proxy
    url_provider += '/order/updated/order_dir/desc/page/1'

    resp = httptools.downloadpage(url_provider, raise_weberror=False)
    # ~ logger.debug(resp.data)

    chash = scrapertools.find_single_match(resp.data, "var chash\s*=\s*'([^']+)")
    def decode_puerto(t, e):
        a = []; r = []
        for n in range(0, len(t), 2): a.append(int('0x'+t[n:n+2], 16))
        for n in range(len(e)): r.append(ord(e[n]))
        for n, val in enumerate(a): a[n] = val ^ r[n % len(r)]
        for n, val in enumerate(a): a[n] = chr(val)
        return ''.join(a)

    proxies = []
    enlaces = scrapertools.find_multiple_matches(resp.data, '(\d+\.\d+\.\d+\.\d+)</a>\s*</td>\s*<td><span class="port" data-port="([^"]+)')
    for prox, puerto in enlaces:
        proxies.append(prox + ':' + decode_puerto(puerto, chash))

    return proxies

def _proxy_list_download(url, tipo_proxy, pais_proxy, max_proxies):
    # API: https://www.proxy-list.download/api/v1
    url_provider = 'https://www.proxy-list.download/api/v1/get'
    url_provider += '?type=' + ('https' if url.startswith('https') else 'http') # http, https, socks4, socks5
    if tipo_proxy != '': url_provider += '&anon=' + tipo_proxy
    if pais_proxy != '': url_provider += '&country=' + pais_proxy

    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    if len(resp.data) > 0: proxies = resp.data.split()
    else:
       url_provider = 'https://www.proxy-list.download/'
       url_provider += ('HTTPS' if url.startswith('https') else 'HTTP')
       resp = httptools.downloadpage(url_provider, raise_weberror=False)

       proxies = []

       block = scrapertools.find_single_match(resp.data, '<tbody id="tabli"(.*?)</tbody>')

       enlaces = scrapertools.find_multiple_matches(block, '<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>')

       for prox, puerto in enlaces:
           proxies.append(prox + ':' + puerto)
       
    return proxies

def _us_proxy_org(url, tipo_proxy, pais_proxy, max_proxies):
    url_provider = 'https://www.us-proxy.org/#list'
    resp = httptools.downloadpage(url_provider, raise_weberror=False)

    proxies = []

    block = scrapertools.find_single_match(resp.data, 'Updated at(.*?)</textarea>')

    enlaces = scrapertools.find_multiple_matches(block, '(.*?)\n')
    for prox in enlaces:
        if prox == '': continue
        elif  '-' in prox: continue
        proxies.append(prox)

    return proxies


def acumulaciones(provider, proxies, all_providers_proxies, max_proxies):
    acumular = False
    if proxies_auto:
        if proxies_todos: acumular = True
    elif provider == all_providers: acumular = True

    if acumular:
        tot_proxies = len(proxies)
        if tot_proxies >= 50: tot_proxies = 50
        if max_proxies: proxies = proxies[:tot_proxies]
        all_providers_proxies = all_providers_proxies + proxies

    return all_providers_proxies


# Testear una lista de proxies para una url determinada
def do_test_proxy(url, proxy, info):
    resp = httptools.downloadpage(url, use_proxy = {'http': proxy, 'https': proxy}, timeout=15, raise_weberror=False)

    info['ok'] = (type(resp.code) == int and resp.code >= 200 and resp.code < 400)
    if 'ERROR 404 - File not found' in resp.data \
       or 'HTTP/1.1 400 Bad Request' in resp.data \
       or '<title>Site Blocked</title>' in resp.data \
       or len(resp.data) < 100:
        info['ok'] = False

    info['time'] = resp.time
    info['len'] = len(resp.data)
    info['code'] = resp.code


def testear_lista_proxies(provider, url, proxies=[]):
    threads = []
    proxies_info = {} # resultados de los tests

    num_proxies = float(len(proxies)) # float para calcular porcentaje

    progreso = platformtools.dialog_progress('Testeando proxies en ' + provider.capitalize(), '%d proxies a comprobar. Cancelar si tarda demasiado.' % num_proxies)

    for proxy in proxies:
        if proxy in proxies_info: continue # por si hay repetidos
        proxies_info[proxy] = {'ok': False, 'time': 0, 'len': 0, 'code': ''}

        try:
           t = Thread(target=do_test_proxy, args=[url, proxy, proxies_info[proxy]])
           t.setDaemon(True)
           t.start()
           threads.append(t)
        except:
           logger.info("proxytools-check: Error Thread.start")
           break

        if progreso.iscanceled(): break

    pendent = [a for a in threads if a.isAlive()]
    while len(pendent) > 0:
        hechos = num_proxies - len(pendent)
        perc = int(hechos / num_proxies * 100)
        validos = sum([1 for proxy in proxies if proxies_info[proxy]['ok']])

        progreso.update(perc, 'Comprobando %d de %d proxies. Válidos %d. Cancelar si tarda demasiado o si ya hay más de uno válido.' % (hechos, num_proxies, validos))

        if progreso.iscanceled(): break

        time.sleep(0.5)
        pendent = [a for a in threads if a.isAlive()]

    progreso.close()

    # Ordenar según proxy válido y tiempo de respuesta
    return sorted(proxies_info.items(), key=lambda x: (-x[1]['ok'], x[1]['time']))


def show_help_proxies():
    logger.info()

    from modules import helper

    item = []

    helper.show_help_proxies(item)


def configuracion_general():
    config.__settings__.openSettings()


def obtener_private_list():
    from core import filetools

    proxies = []

    proxies_file = os.path.join(config.get_data_path(), private_list)
    existe = filetools.exists(proxies_file)

    if not existe:
        import xbmcgui

        ubicacion_path = xbmcgui.Dialog().browseSingle(3, 'Seleccionar carpeta ubicación ' + private_list, 'files', '', False, False, '')
        if not ubicacion_path: return proxies

        proxies_file = filetools.join(ubicacion_path, private_list)
        existe = filetools.exists(proxies_file)

        if not existe:
            platformtools.dialog_notification('Buscar proxies', '[COLOR red]No se encuentra el fichero[/COLOR]')
            time.sleep(1.0)
            return proxies

    data = filetools.read(proxies_file)
    data = re.sub(r'(?m)^#.*\n?', '', data) # Quitar líneas que empiezen por #
    proxies = data.replace(' ', '').replace(';', ',').replace(',', '\n').split()

    return proxies
