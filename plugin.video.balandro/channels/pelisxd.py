# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://www.pelisxd.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por país', action = 'paises', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Categorías de Películas<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Películas por País<(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?aria-label.*?>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    url_letra = host + 'letter/'

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#':
        if letra == '#': url = url_letra + '0-9/'
        else: url = url_letra + letra + '/'

        itemlist.append(item.clone( title = letra, action = 'list_all', url = url ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)<h3')

    matches = re.compile('<article(.*?)</article', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, '<a href="(.*?)"')
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>')
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        year = scrapertools.find_single_match(article, '<span class="year">(.*?)</span>')
        if not year:
            year = '-'

        langs = []
        if '/es.png' in article: langs.append('Esp')
        if '/la.png' in article: langs.append('Lat')
        if '/us.png' in article: langs.append('Vose')

        quality = scrapertools.find_single_match(article, '<span class="Qlty">(.*?)</span>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=','.join(langs), qualities=quality,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="(.*?)"')

        if next_page:
            itemlist.append(item.clone( title='>> Página siguiente', url = next_page, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('href="#options-(.*?)">.*?<span class="server">(.*?)</span>', re.DOTALL).findall(data)

    for option, servidor in matches:
        servidor = servidor.lower()
        if not servidor: 
            continue

        if '-' in servidor:
            servidor = servidor.strip()
            lang = scrapertools.find_single_match(servidor, '.*?-(.*?)$').strip()
            servidor = scrapertools.find_single_match(servidor, '(.*?)-')
        else:
            lang = item.languages

        servidor = servidor.strip()

        if servidor == 'femax20': servidor = 'fembed'
        elif servidor == 'embed': servidor = 'mystream'
        elif servidor == 'player': servidor = 'directo'

        bloque = scrapertools.find_single_match(data, '<div id="options-' + str(option) + '"(.*?)</div>')

        url = scrapertools.find_single_match(str(bloque), '<iframe src="(.*?)"')
        if not url: url = scrapertools.find_single_match(str(bloque), '<iframe data-src="(.*?)"')

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, 
                                  language = IDIOMAS.get(lang, lang) ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')

    data = do_downloadpage(item.url)

    url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')
    if not url: url = scrapertools.find_single_match(data, '<IFRAME SRC="(.*?)"')

    if '/player.pelisxd.com/' in url:
        data = do_downloadpage(url)
        url = scrapertools.find_single_match(data, 'link":"([^"]+)"')

    if url:
        if '/fembed.com/' in url:
            url = url.replace('/fembed.com/', '/www.fembed.com/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)
        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
