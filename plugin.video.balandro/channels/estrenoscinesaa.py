# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.estrenoscinesaa.com/'


def do_downloadpage(url):
    data = httptools.downloadpage(url).data
    return data


def mainlist(item):
    # ~ De momento descartadas series pq solamente hay 13
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'genre/netflix/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + 'genre/marvel/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'D.C.', action = 'list_all', url = host + 'genre/d-c/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Star wars', action = 'list_all', url = host + 'genre/starwars/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<ul class="genres(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">(.*?)</a>\s*<i>(.*?)</i>')

    for url, title, count in matches:
        if '/genre/d-c/' in url: continue
        if '/genre/marvel/' in url: continue
        if '/genre/netflix/' in url: continue
        if '/genre/starwars/' in url: continue
        if '/sci-fi-fantasy/' in url: continue # Solo son series

        if count: title = title + ' (' + count + ')'

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    hasta_data = '<div class="pagination">' if '<div class="pagination">' in data else '<nav class="genres">'
    bloque = scrapertools.find_single_match(data, '</h1>(.*?)' + hasta_data)
    if not bloque: bloque = scrapertools.find_single_match(data, '</h1>(.*)')

    matches = scrapertools.find_multiple_matches(bloque, '<article id="post-(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)')
        title = scrapertools.find_single_match(match, ' alt="([^"]+)').strip()
        thumb = scrapertools.find_single_match(match, ' src="([^"]+)')

        year = scrapertools.find_single_match(match, '<span>(\d{4})</span>')
        if not year: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(match, '<div class="texto">(.*?)</div>'))

        if '/tvshows/' in url:
           if item.search_type == 'movie': continue

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if '<div class="pagination">' in data:
        next_page = scrapertools.find_single_match(data, '<span class="current".*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all', text_color='coral' ))

    return itemlist


# Si hay excepciones concretas de este canal, añadir aquí, si son genéricas añadir en servertools.corregir_servidor
def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    return servidor

def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    # Fuentes de vídeo
    matches = scrapertools.find_multiple_matches(data, "(?i)<div class='pframe'><iframe.*?src=(?:'|\")([^'\"]+)")
    for url in matches:
        if 'youtube.com' in url: continue # trailers
        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Esp' ))

    # Descarga
    bloque = scrapertools.find_single_match(data, "<div id='download'(.*?)</table></div></div></div>")

    matches = scrapertools.find_multiple_matches(bloque, "<tr id='link-[^']+'>(.*?)</tr>")
    for enlace in matches:
        url = scrapertools.find_single_match(enlace, " href='([^']+)")
        servidor = corregir_servidor(scrapertools.find_single_match(enlace, "domain=(?:www.|dl.|)([^'.]+)"))
        # ~ logger.info('url: %s Servidor: %s' % (url,servidor))
        if not url or not servidor: continue
        quality = 'HD'; lang = 'Esp' # siempre tienen las mismas !?

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                              language = lang, quality = quality , other = 'd' ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if host in item.url:
        data = do_downloadpage(item.url)
        url = scrapertools.find_single_match(data, '<a id="link".*?href="([^"]+)')
        if url:
            servidor = servertools.get_server_from_url(url)
            if servidor and servidor != 'directo':
                url = servertools.normalize_url(servidor, url)
                itemlist.append(item.clone( url=url, server=servidor ))

    else:
        itemlist.append(item.clone())

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article>(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)')
        title = scrapertools.find_single_match(match, ' alt="([^"]+)').strip()
        thumb = scrapertools.find_single_match(match, ' src="([^"]+)')

        year = scrapertools.find_single_match(match, '<span class="year">(\d{4})</span>')
        if not year: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(match, '<div class="contenido"><p>(.*?)<p></div>'))

        if '/tvshows/' in url:
           if item.search_type == 'movie': continue

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if '<div class="pagination">' in data:
        next_page = scrapertools.find_single_match(data, '<span class="current".*?<a href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_search', text_color='coral' ))

    return itemlist
