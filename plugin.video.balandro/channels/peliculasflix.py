# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

host = 'https://peliculasflix.co/'

perpage = 24


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-peliculas-online/' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'generos', search_type = 'movie', grupo = 'productoras' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    productoras = [
        '/amazon-prime-video/',
        '/apple-tv-plus/',
        '/bbc-one/',
        '/blim-tv/',
        '/peliculas-de-claro-video/',
        '/dc-comics/',
        '/peliculas-de-disney-plus/',
        '/hbo-go/',
        '/movistar-play/',
        '/peliculas-de-netflix/'
        ]

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<div class="Title">Géneros</div>\s*<ul>(.*?)<ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">(.*?)</a>(.*?)</li>')

    for url, tit, tot in matches:
        gen = scrapertools.find_single_match(url, '/genero(/[^/]+/)')
        if item.grupo == 'productoras': 
            if gen not in productoras: continue
        else:
            if gen in productoras: continue

        if descartar_xxx and tit == 'Erótica': continue

        if tot: tit = tit + ' (%s)' % tot.strip()

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article class="(.*?)</article>')

    if descartar_xxx:
        matches = filter(lambda x: '/genero/erotica/' not in x, matches)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' class="Title">(.*?)</h2>').strip()
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="([^"]+)')
        year = scrapertools.find_single_match(article, '<span class="Date">(\d{4})</span>')
        if not year: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="Description">\s*<p>(.*?)</p>'))

        quality = scrapertools.find_single_match(article, '<span class="Qlty">(.*?)</span>')
        langs = []
        if '/espana.png' in article: langs.append('Esp')
        if '/mexico.png' in article: langs.append('Lat')
        if '/usa.png' in article: langs.append('Vose')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages=', '.join(langs), qualities=quality,
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        if '<nav class="wp-pagenavi">' in data:
            next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><i class="fa-arrow-right"></i></a>')
            if next_page:
               itemlist.append(item.clone (url = next_page, page=0, title = '>> Página siguiente', action = 'list_all', text_color='coral' ))

    return itemlist


# Si hay excepciones concretas de este canal, añadir aquí, si son genéricas añadir en servertools.corregir_servidor
def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'embed': return 'mystream'
    if servidor == 'flixplayer': return 'directo'
    return servidor

def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, '<li data-typ(?:e|)="movie"(.*?)</li>')

    for match in matches:
        data_key = scrapertools.find_single_match(match, 'data-key="([^"]+)"')
        data_id = scrapertools.find_single_match(match, 'data-id="([^"]+)"')

        lang = scrapertools.find_single_match(match, '-language">(.*?)</p>').lower()
        lang = re.sub('[^a-z]+', '', lang)

        qlty = scrapertools.find_single_match(match, '-equalizer">(.*?)</p>')

        servidor = corregir_servidor(scrapertools.find_single_match(match, '-dns">(.*?)</p>'))

        if servidor == 'damedamehoy': servidor = 'directo'

        url = host + '?trembed=%s&trid=%s&trtype=1' % (data_key, data_id)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                              language = IDIOMAS.get(lang, lang), quality = qlty ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    url = scrapertools.find_single_match(data, 'src="([^"]+)"')

    if '/damedamehoy.xyz/' in url:
        url = url.replace('https://damedamehoy.xyz/embed.html#', 'https://damedamehoy.xyz/details.php?v=')
        data = httptools.downloadpage(url).data

        url = scrapertools.find_single_match(data, '"file":"(.*?)"')

        url = url.replace('\\/', '/')

        if url:
           itemlist.append(item.clone( url=url, server='directo'))
           return itemlist

    if '/flixplayer.' in url:
       data = httptools.downloadpage(url).data
       # ~ logger.debug(data)
       url = scrapertools.find_single_match(data, 'link":"([^"]+)"')

    elif host in url and '?h=' in url:
        fid = scrapertools.find_single_match(url, "h=([^&]+)")
        url2 = url.split('?h=')[0] + 'r.php'
        resp = httptools.downloadpage(url2, post='h='+fid, headers={'Referer': url}, follow_redirects=False)
        if 'location' in resp.headers: url = resp.headers['location']
        else: url = None

    if url:
        servidor = servertools.get_server_from_url(url)
        # ~ if servidor and servidor != 'directo': # descartado pq puede ser 'directo' si viene de flixplayer
        url = servertools.normalize_url(servidor, url)
        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
