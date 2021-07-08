# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, servertools


host = "https://www.documentales-online.com"


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<ul class="sub-menu">(.*?)</ul>')

    patron = ' href="([^"]+)">([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, title in matches:
        if url.startswith('/'): url = host + url

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for article in matches:
        url, title = scrapertools.find_single_match(article, '<h2 class="entry-title"><a href="([^"]+)".*?>(.*?)</a>')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        if '/series-temas/' in url: continue

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, plot=plot,
                                    contentType='movie', contentTitle=title, contentExtra='documentary' ))

    next_page_link = scrapertools.find_single_match(data, '<span aria-current="page" class="page-numbers current">.*?href="(.*?)"')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', action='list_all', url = next_page_link, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(http[^"]+)')

    for url in matches:
        if 'amazon-adsystem.com' in url: continue

        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = servidor.capitalize(), url = url, language = 'Esp' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
