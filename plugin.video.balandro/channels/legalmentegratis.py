# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'http://legalmentegratis.com/'


web_otros = [
   ('alfred-hitchcock'),
   ('anitra-ford'),
   ('bela-lugosi'),
   ('buster-keaton'),
   ('cary-grant'),
   ('david-lynch'),
   ('ed-wood'),
   ('eisenstein'),
   ('frank-capra'),
   ('frank-sinatra'),
   ('fritz-lang'),
   ('gary-cooper'),
   ('george-romero'),
   ('griffith'),
   ('henry-mancini'),
   ('murnau'),
   ('orson-welles'),
   ('roger-corman'),
   ('tarantino'),
   ('tarkovski'),
   ('vincent-price')
   ]


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por dirección, interprete', action = 'otros', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<ul class="sub-menu">(.*?)</ul>')

    patron = 'class="menu-item menu-item-type-taxonomy menu-item-object-category.*?href="(.*?)">(.*?)</a>'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, title in matches:
        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url = host + 'eco/'

    data = httptools.downloadpage(url).data

    bloque = scrapertools.find_single_match(data, '<span>Etiquetas</span>(.*?)</aside>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?aria-label.*?">(.*?)</a>')

    for url, title in matches:
        despreciar = url.replace(host, '').replace('tag/', '').replace('/', '')
        if despreciar in web_otros: continue

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return sorted(itemlist, key = lambda it: it.title)


def otros(item):
    logger.info()
    itemlist = []

    for x in web_otros:
        title = str(x)
        title = title.replace('-', ' ').capitalize()

        url = host + 'tag/' + str(x) + '/'

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article id="post-(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        if not url: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        try:
           title, year, plot = scrapertools.find_single_match(match, "<p>(.*?) (\(?\d{4}\)?)([^<]+)</p>")
        except:
           title = scrapertools.find_single_match(match, "<p>(.*?) ")
           year = scrapertools.find_single_match(match, "<p>.*? (.*?)")
           plot = scrapertools.find_single_match(match, "<p>(.*?)</p>")

        titulo = scrapertools.find_single_match(match, '<span class="visuallyhidden">(.*?)</span>')
        if not titulo: titulo = title

        year = re.sub(r'\(|\)','', year)

        if not year: year = '-'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<div class="nav-previous"><a href="(.*?)"')

    if next_page:
        itemlist.append(item.clone(action = 'list_all', title = '>> Página siguiente', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    idioma = scrapertools.find_single_match(data, '<p><strong>(.*?)</strong>').lower()
    if 'subtitul' in idioma: lang = 'Vose'
    elif 'n original' in idioma: lang = 'VO'
    else: lang = 'Esp'

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(.*?)"')

    for url in matches:
        if url.startswith('//'): url = 'https:' + url
        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, title = '', language = lang)) 

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+") + '&submit=Search'
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
