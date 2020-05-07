# -*- coding: utf-8 -*-

import re, urlparse

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


DOMINIOS = ['https://www.cinecalidad.eu/', 'https://www.cinecalidad.is/', 'https://www.cinecalidad.to/', 'https://www1.cinecalidad.top/']

def host_by_lang(lang=''):
    if lang == '': # si no se especifica idioma, obtenerlo de las preferencias de idioma del usuario
        pref_esp = config.get_setting('preferencia_idioma_esp', default='1')
        pref_lat = config.get_setting('preferencia_idioma_lat', default='2')
        lang = 'Esp' if pref_esp != 0 and (pref_lat == 0 or pref_esp <= pref_lat) else 'Lat'
        
    dominio = config.get_setting('dominio', 'cinecalidad', default=DOMINIOS[0])
    if lang == 'Lat': return dominio
    if lang == 'Esp': return dominio + 'espana/'
    return dominio


def item_configurar_dominio(item):
    plot = 'Este canal tiene varios posibles dominios. Si uno no te funciona puedes probar con los otros antes de intentarlo con proxies.'
    return item.clone( title = 'Configurar dominio a usar ...', action = 'configurar_dominio', folder=False, plot=plot, text_color='red' )

def configurar_dominio(item):
    dominio = config.get_setting('dominio', 'cinecalidad', default=DOMINIOS[0])
    num_dominio = DOMINIOS.index(dominio) if dominio in DOMINIOS else 0
    ret = platformtools.dialog_select('Dominio a usar', DOMINIOS, preselect=num_dominio)
    if ret == -1: return False
    config.set_setting('dominio', DOMINIOS[ret], 'cinecalidad')
    return True

def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host_by_lang('Lat') + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host_by_lang(''))

def do_downloadpage(url, post=None, headers=None):
    dominio = config.get_setting('dominio', 'cinecalidad', default=DOMINIOS[0]) # por si viene de enlaces guardados
    for dom in DOMINIOS:
        url = url.replace(dom, dominio)

    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('cinecalidad', url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []
    
    itemlist.append(item.clone( title='Castellano', action='mainlist_pelis_lang', idioma='Esp' ))
    itemlist.append(item.clone( title='Latino', action='mainlist_pelis_lang', idioma='Lat' ))

    itemlist.append(item_configurar_dominio(item))
    itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_pelis_lang(item):
    logger.info()
    itemlist = []
    
    host = host_by_lang(item.idioma)
    itemlist.append(item.clone( title='Lista de películas', action='peliculas', url=host ))
    itemlist.append(item.clone( title='Destacadas', action='peliculas', url=host+'genero-peliculas/destacada/' ))
    itemlist.append(item.clone( title='Por Género', action='generos' ))
    itemlist.append(item.clone( title='Por Año', action='anyos' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    itemlist.append(item_configurar_dominio(item))
    itemlist.append(item_configurar_proxies(item))
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

def anyos(item):
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

    # ~ patron = '<div class="home_post_cont[^"]*">\s*<a href="([^"]+)">'
    # ~ patron += '<img width="[^"]*" height="[^"]*" src="([^"]+)" class="[^"]*" alt="[^"]*" title="([^"]+)"'
    # ~ patron += '.*?&lt;p&gt;(.*?)&lt;/p&gt;&lt;'
    patron = '<div class="home_post_cont[^"]*">\s*<a href=([^>]+)>'
    patron += '<img width=\d* height=\d* src=([^ ]+) class="[^"]*" alt="[^"]*" title="([^"]+)"'
    patron += '.*?&lt;p&gt;(.*?)&lt;/p&gt;&lt;'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    for url, thumb, title, plot in matches:
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

    # ~ next_page_link = scrapertools.find_single_match(data, "<link rel='next' href='([^']+)' />")
    next_page_link = scrapertools.find_single_match(data, "<link rel=next href=([^>]+)")
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='peliculas' ))

    return itemlist


def dec(item, dec_value):
    link = []
    val = item.split(' ')
    link = map(int, val)
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
        'Mega': 'https://mega.nz/embed#!%s',
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
            
            itemlist.append(Item(channel = item.channel, action = 'play', server = servidor,
                                 title = '', url = url,
                                 language = item.languages
                           ))

    # Enlaces Torrent
    idio = scrapertools.find_single_match(data, '<div class=pane_title>DESCARGAR</div><div class=pane_descripcion>([^<]+)').lower()
    if 'audio castellano' in idio: lang = 'Esp'
    elif 'audio latino' in idio: lang = 'Lat'
    else: lang = 'VOSE'
    matches = re.compile(' href="([^"]+)" target=_blank class=link rel=nofollow service=BitTorrent', re.DOTALL).findall(data)
    if not matches:
        matches = re.compile(' href="([^"]+)" target="_blank" class="link" rel="nofollow" service="BitTorrent', re.DOTALL).findall(data)
    for url in matches:
        itemlist.append(Item(channel = item.channel, action = 'play', server = 'torrent',
                             title = '', url = host_by_lang('Lat')+url[1:],
                             language = lang
                       ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url
    if '/protect/v.php' in item.url:
        data = do_downloadpage(item.url)
        # ~ logger.debug(data)
        url_torrent = scrapertools.find_single_match(data, 'value="(magnet.*?)"')
        if url_torrent != '': url = url_torrent

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
