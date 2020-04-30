# -*- coding: utf-8 -*-

import re, urllib, base64

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb

# ~ host = 'https://grantorrent.eu/'
host = 'https://grantorrentt.com/'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None):
    ant_hosts = ['http://grantorrent.net/', 'https://grantorrent1.com/', 'https://grantorrent.one/', 
                 'https://grantorrent.tv/', 'https://grantorrent.la/', 'https://grantorrent.io/', 
                 'https://grantorrent.cc/', 'https://grantorrent.li/', 'https://grantorrent.eu/']
    for ant in ant_hosts:
        url = url.replace(ant, host) # por si viene de enlaces guardados

    # ~ data = httptools.downloadpage(url, post=post).data
    data = httptools.downloadpage_proxy('grantorrent', url, post=post).data
    # ~ logger.debug(data)
    
    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                # ~ logger.debug('Cookies: %s %s' % (ck_name, ck_value))
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post).data
                data = httptools.downloadpage_proxy('grantorrent', url, post=post).data
                # ~ logger.debug(data)
        except:
            pass
        
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas películas', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    # ~ itemlist.append(item.clone( title = 'Por año', action = 'anyos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    
    opciones = {
        'accion':'Acción', 'animacion':'Animación', 'aventura':'Aventura', 'biografia':'Biografía', 'ciencia-ficcion':'Ciencia ficción',
        'comedia':'Comedia', 'crimen':'Crimen', 'deporte':'Deporte', 'documental':'Documental', 'drama':'Drama',
        'familia':'Familia', 'fantasia':'Fantasía', 'guerra':'Guerra', 'historia':'Historia', 'misterio':'Misterio', 'musica':'Música',
        'romance':'Romance', 'suspense':'Suspense', 'terror':'Terror'
    }
    for opc in sorted(opciones):
        itemlist.append(item.clone( title=opciones[opc], url=host + 'categoria/' + opc + '/', action='list_categ_search' ))

    return itemlist

def anyos(item):
    logger.info()
    itemlist = []
    
    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1969, -1):
        itemlist.append(item.clone( title=str(x), url=host + 'categoria/' + str(x) + '/', action='list_categ_search' ))

    return itemlist

def calidades(item):
    logger.info()
    itemlist = []
    
    itemlist.append(item.clone( title='Hd Rip', url=host + 'categoria/HDRip/', action='list_categ_search' ))
    itemlist.append(item.clone( title='Dvd Rip', url=host + 'categoria/dvdrip/', action='list_categ_search' ))
    itemlist.append(item.clone( title='Micro HD', url=host + 'categoria/MicroHD-1080p/', action='list_categ_search' ))
    itemlist.append(item.clone( title='BluRay', url=host + 'categoria/BluRay-1080p/', action='list_categ_search' ))
    itemlist.append(item.clone( title='3D', url=host + 'categoria/3D/', action='list_categ_search' ))
    itemlist.append(item.clone( title='4K', url=host + 'categoria/4k/', action='list_categ_search' ))

    return itemlist



def detectar_idioma(img):
    if 'icono_espaniol.png' in img: return 'Esp'
    else: return 'VO' # !?


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)
    
    patron = '<div class="imagen-post">\s*<a href="([^"]+)"[^>]*>(?:>|)<img src="([^"]+)"[^>]*>'
    # ~ patron += '\s*</a>\s*<div class="bloque-superior">([^<]+)'
    patron += '.*?</a>\s*<div class="bloque-superior">([^<]+)'
    patron += '<div class="imagen-idioma">\s*<img src="([^"]+)"[^>]*>'
    patron += '\s*</div>\s*</div>\s*<div class="bloque-inferior">([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, quality, lang, title in matches:
        title = title.strip()
        
        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    languages=detectar_idioma(lang), qualities=quality.strip(),
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link ))

    return itemlist


def list_categ_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)
    
    patron = '<div class="imagen-post">\s*<a href="([^"]+)".*?<img src="([^"]+)"'
    patron += '.*?</a>\s*<div class="bloque-inferior">([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title in matches:
        title = title.strip()
        
        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_categ_search' ))

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.lower().replace(' ', '').replace('-', '')
    orden = ['3d', 'screener', 'screener720p', 'hdscreener', 'brscreener', 'dvdrip', 'hdrip', 'bluray720p', 'microhd', 'microhd1080p', 'bluray1080p', 'fullbluray1080p', 'bdremux1080p', '4k', 'full4k', '4kuhdrip', '4kfulluhd', '4kuhdremux', '4kuhdremux1080p', '4khdr']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)
    
    # ~ patron = '<tr class="lol">\s*<td><img src="([^"]+)"[^>]*></td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td><a class="link" onclick="([^"]+)'
    patron = '<tr class="lol">\s*<td><img ([^>]*)>.*?</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td><a class="link" onclick="([^"]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if not matches:
        patron = '<tr class="lol">\s*<td><img ([^>]*)>.*?</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td><a class="link" href="([^"]+)'
        matches = re.compile(patron, re.DOTALL).findall(data)

    for lang, quality, peso, onclick in matches:
        # ~ logger.debug('%s => %s' % (quality, puntuar_calidad(quality)))

        if onclick.startswith('http'):
            url = onclick
        else:
            post = scrapertools.find_single_match(onclick, "u:\s*'([^']+)")
            if not post: continue
            try:
                url = base64.b64decode(post)
                # ~ url = url.replace('grantorrent.la/', 'grantorrent.one/')
            except:
                continue

        itemlist.append(Item( channel = item.channel, action = 'play',
                              title = '', url = url, server = 'torrent',
                              language = detectar_idioma(lang), quality = quality, quality_num = puntuar_calidad(quality), other = peso
                       ))

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_categ_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
