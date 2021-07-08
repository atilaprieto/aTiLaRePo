# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urlparse
else:
    import urllib.parse as urlparse

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

host = 'https://www.cinecalidad.im/'

# ~ dominios = ['https://www.cinecalidad.is/', 'https://www.cinecalidad.li/', 'https://www.cinecalidad.eu/', 'https://www.cinecalidad.im/']


def host_by_lang(lang=''):
    if lang == '': # si no se especifica idioma, obtenerlo de las preferencias de idioma del usuario
        pref_esp = config.get_setting('preferencia_idioma_esp', default='1')
        pref_lat = config.get_setting('preferencia_idioma_lat', default='2')
        lang = 'Esp' if pref_esp != 0 and (pref_lat == 0 or pref_esp <= pref_lat) else 'Lat'

    # ~ dominio = config.get_setting('dominio', 'cinecalidad', default=dominios[0])
    # ~ if dominio not in dominios: dominio = dominios[0]
    # ~ if lang == 'Lat': return dominio
    # ~ if lang == 'Esp': return dominio + 'espana/'
    # ~ return dominio

    if lang == 'Lat': return host
    if lang == 'Esp': return host + 'espana/'
    return host


# ~ def item_configurar_dominio(item):
    # ~ plot = 'Este canal tiene varios posibles dominios. Si uno no te funciona puedes probar con los otros antes de intentarlo con proxies.'
    # ~ return item.clone( title = 'Configurar dominio a usar ...', action = 'configurar_dominio', folder=False, plot=plot, text_color='yellowgreen' )


# ~ def configurar_dominio(item):
    # ~ dominio = config.get_setting('dominio', 'cinecalidad', default=dominios[0])
    # ~ num_dominio = dominios.index(dominio) if dominio in dominios else 0
    # ~ ret = platformtools.dialog_select('Dominio a usar CineCalidad', dominios, preselect=num_dominio)
    # ~ if ret == -1: return False
    # ~ config.set_setting('dominio', dominios[ret], 'cinecalidad')
    # ~ return True


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host_by_lang('Lat') + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )


# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host_by_lang(''))


def do_downloadpage(url, post=None, headers=None):
    # ~  por si viene de enlaces guardados
    # ~ dominio = config.get_setting('dominio', 'cinecalidad', default=dominios[0])
    # ~ if dominio not in dominios: dominio = dominios[0]
    # ~ for dom in dominios:
        # ~ url = url.replace('https://www1.', 'https://www.')
        # ~ url = url.replace(dom, dominio)

    url = url.replace('https://www1.', 'https://www.')
    url = url.replace('/www.cinecalidad.is/', host)
    url = url.replace('/www.cinecalidad.li/', host)
    url = url.replace('/www.cinecalidad.eu/', host)

    data = httptools.downloadpage(url, post=post, headers=headers).data
    # ~ data = httptools.downloadpage_proxy('cinecalidad', url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'mainlist_pelis_lang', idioma = 'Esp' ))
    itemlist.append(item.clone( title = 'Latino', action = 'mainlist_pelis_lang', idioma = 'Lat' ))

    # ~ itemlist.append(item_configurar_dominio(item))
    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_pelis_lang(item):
    logger.info()
    itemlist = []

    host = host_by_lang(item.idioma)
    itemlist.append(item.clone( title='Catálogo', action='peliculas', url=host ))

    itemlist.append(item.clone( title='Destacadas', action='peliculas', url=host+'genero-peliculas/destacada/' ))

    itemlist.append(item.clone( title='En 4K', action='peliculas', url=host+'peliculas/4k-ultra-hd/' ))

    itemlist.append(item.clone( title='Por género', action='generos' ))
    itemlist.append(item.clone( title='Por año', action='anios' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_dominio(item))
    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        ('accion','Acción'), 
        ('animacion','Animación'), 
        ('aventura','Aventura'), 
        ('biografia','Biografía'), 
        ('ciencia-ficcion','Ciencia ficción'), 
        ('comedia','Comedia'), 
        ('crimen','Crimen'), 
        ('drama','Drama'), 
        ('fantasia','Fantasía'), 
        ('guerra','Guerra'), 
        ('historia','Historia'), 
        ('infantil','Infantil'), 
        ('misterio','Misterio'), 
        ('musica','Música'), 
        ('romance','Romance'), 
        ('suspenso','Suspenso'), 
        ('terror','Terror'), 
    ]

    url_base = host_by_lang(item.idioma)

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url=url_base + 'genero-peliculas/' + opc + '/', action='peliculas' ))

    return itemlist

def anios(item):
    logger.info()
    itemlist = []

    item.url = host_by_lang(item.idioma)+'peliculas-por-ano/'

    data = do_downloadpage(item.url)
    # ~ patron = '<a href="([^"]+)">([^<]+)</a><br'
    patron = '<a href=([^>]+)>([^<]+)</a><br'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        itemlist.append(item.clone( title=scrapedtitle, action='peliculas', url=url ))

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    patron = '<div class="home_post_cont[^"]*">\s*<a href=([^>]+)>'
    patron += '<img width=\d* height=\d* src=([^ ]+) class="[^"]*" alt="[^"]*" (?:loading=lazy |)title="([^"]+)"'
    patron += '.*?&lt;p&gt;(.*?)&lt;/p&gt;&lt;'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title, plot in matches:
        if url.startswith('/'): url = host_by_lang('Lat') + url[1:]
        title = re.sub('&lt;!--.*?--&gt;', '', title)
        m = re.match(r"^(.*?)\((\d+)\)$", title)
        if m:
            title = m.group(1).strip()
            year = m.group(2)
        else:
            year = '-'

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    languages=item.idioma,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, "<link rel=next href=([^>]+)")
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='peliculas', text_color='coral' ))

    return itemlist


def dec(item, dec_value):
    link = []
    val = item.split(' ')
    link = list(map(int, val))

    for i in range(len(link)):
        link[i] = link[i] - int(dec_value)
        real = ''.join(map(chr, link))
    return (real)

def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    dec_value = scrapertools.find_single_match(data, 'String\.fromCharCode\(parseInt\(str\[i\]\)-(\d+)\)')

    # Enlaces Online
    server_url = {
        'UpToBox': 'https://uptobox.com/iframe/%s',
        'YourUpload': 'http://www.yourupload.com/embed/%s',
        'UsersCloud': 'https://userscloud.com/%s',
        'OkRu': 'http://ok.ru/videoembed/%s',
        'Mega': 'https://mega.nz/file/%s',
        'Fembed': 'https://www.fembed.com/v/%s',
        'Gounlimited': 'https://gounlimited.to/embed-%s.html',
        'Clipwatching': 'https://clipwatching.com/embed-%s.html',
        'Vidoza': 'https://vidoza.net/embed-%s.html',
        'Jetload': 'https://jetload.net/e/%s',
        'Openplay': 'https://player.openplay.vip/player.php?id=%s'
    }

    matches = re.compile(' target=_blank class="link onlinelink" service=Online([^ ]+) data="([^"]+)', re.DOTALL).findall(data)
    if not matches:
        matches = re.compile(' target="_blank" class="link onlinelink" service="Online([^"]+)" data="([^"]+)', re.DOTALL).findall(data)

    for srv, encoded in matches:
        if srv in server_url:
            url = server_url[srv] % dec(encoded, dec_value)
            servidor = srv.lower()
            if servidor == 'netu': servidor = 'netutv'

            itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = item.languages ))

    # Idioma para enlaces BitTorrent, 4K
    idio = scrapertools.find_single_match(data, '<div class=pane_title>DESCARGAR</div><div class=pane_descripcion>([^<]+)').lower()
    if 'audio castellano' in idio: lang = 'Esp'
    elif 'audio latino' in idio: lang = 'Lat'
    else: lang = 'Vose'

    # Enlaces Mega 4K
    matches = re.compile(' href="([^"]+)" target=_blank class="link link4k" rel=nofollow service=Mega4K', re.DOTALL).findall(data)
    if not matches:
        matches = re.compile(' href="([^"]+)" target="_blank" class="link link4k" rel="nofollow" service="Mega4K', re.DOTALL).findall(data)

    for url in matches:
        if url.startswith('/'): url = host_by_lang('Lat') + url[1:]
        itemlist.append(Item(channel = item.channel, action = 'play', server = 'mega', title = '', url = url, language = lang, quality = '4K' ))

    # Enlaces BitTorrent
    matches = re.compile(' href="([^"]+)" target=_blank class=link rel=nofollow service=BitTorrent', re.DOTALL).findall(data)
    if not matches:
        matches = re.compile(' href="([^"]+)" target="_blank" class="link" rel="nofollow" service="BitTorrent', re.DOTALL).findall(data)

    for url in matches:
        if url.startswith('/'): url = host_by_lang('Lat') + url[1:]
        itemlist.append(Item(channel = item.channel, action = 'play', server = 'torrent', title = '', url = url, language = lang ))

    # Enlaces BitTorrent 4K
    matches = re.compile(' href="([^"]+)" target=_blank class="link link4k" rel=nofollow service=BitTorrent4K', re.DOTALL).findall(data)
    if not matches:
        matches = re.compile(' href="([^"]+)" target="_blank" class="link link4k" rel="nofollow" service="BitTorrent4K', re.DOTALL).findall(data)

    for url in matches:
        if url.startswith('/'): url = host_by_lang('Lat') + url[1:]
        itemlist.append(Item(channel = item.channel, action = 'play', server = 'torrent', title = '', url = url, language = lang, quality = '4K' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '/ouo.io/' in item.url:
        url = scrapertools.find_single_match(item.url, '\?s=(.*)$')
        if not url:
            if url.startswith('https://ouo.io/'):
                url = url.replace('https://ouo.io/', 'https://ouo.io/go/')
                data = httptools.downloadpage(url).data
                _token = scrapertools.find_single_match(data, 'name="_token" type="hidden" value="(.*?)"')
                post = {'action': "https://ouo.io/shorten", '_token': _token }
                url = httptools.downloadpage(url, post = post, follow_redirects=False, only_headers=True).headers.get('location', '')
        if url:
            item.url = url

    if '/protect/v.php' in item.url or '/vip/v.php' in item.url or '/protect/v2.php' in item.url or '/vip/v2.php' in item.url:
        data = do_downloadpage(item.url)
        # ~ logger.debug(data)

        cod_vip = scrapertools.find_single_match(data, 'name="codigovip" value="([^"]+)"')
        if cod_vip:
            data = do_downloadpage(item.url, post={'codigovip': cod_vip})
            # ~ logger.debug(data)

        if item.server != 'torrent':
            url = scrapertools.find_single_match(data, '<div id="contenido".*?href="([^"]+)"')
            if url: url = url.replace('/file/', '/embed#!')
        else:
            url = scrapertools.find_single_match(data, 'value="(magnet.*?)"')

    if url:
        if url.endswith('.torrent'):
            if config.get_setting('proxies', item.channel, default=''):
                import os
            
                data = do_downloadpage(url)
                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))
            else:
                itemlist.append(item.clone( url = url, server = 'torrent' ))

            return itemlist

        itemlist.append(item.clone(url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host_by_lang(item.idioma) + '?s=' + texto.replace(" ", "+")
        item.idioma = 'Esp' if '/espana/' in item.url else 'Lat' # Desde búsqueda global no hay idioma fijado
        return peliculas(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
