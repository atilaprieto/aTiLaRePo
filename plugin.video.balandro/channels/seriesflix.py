# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb
import re

host = 'https://seriesflix.to/'

perpage = 24 # preferiblemente un múltiplo de los elementos que salen en la web (6x8=48) para que la subpaginación interna no se descompense


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas series', action = 'list_all', url = host + 'ver-series-online/' ))

    itemlist.append(item.clone( title = 'Por productoras', action = 'generos', search_type = 'tvshow', grupo = 'productoras' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<div class="Title">Géneros</div>\s*<ul>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">(.*?)</a>(.*?)</li>')

    for url, tit, tot in matches:
        if item.grupo == 'productoras':
            if 'series-de-' not in url: continue
        else:
            if 'series-de-' in url: continue

        title = tit.replace('Series de', '').strip()
        if tot: title = title + ' (%s)' % tot.strip()

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article class="(.*?)</article>')
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' class="Title">(.*?)</h2>').strip()
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="([^"]+)')
        year = scrapertools.find_single_match(article, '<span class="Date">(\d{4})</span>')
        if not year: year = '-'
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="Description">\s*<p>(.*?)</p>'))

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all' ))
            buscar_next = False

    if buscar_next:
        if '<nav class="wp-pagenavi">' in data:
            next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><i class="fa-arrow-right"></i></a>')
            if next_page:
               itemlist.append(item.clone (url = next_page, page=0, title = '>> Página siguiente', action = 'list_all'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'data-season="(\d+)".*?<a href="([^"]+)')

    for numtempo, url in matches:
        numtempo = int(numtempo)

        itemlist.append(item.clone( action = 'episodios', title = 'Temporada ' + str(numtempo), url = url, 
                                    contentType = 'season', contentSeason = numtempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist

# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
# ~ def tracking_all_episodes(item):
    # ~ return episodios(item)

def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<tr class="Viewed">(.*?)</tr>')

    for data_epi in matches:
        url = scrapertools.find_single_match(data_epi, '<a href="([^"]+)"')
        episode = scrapertools.find_single_match(data_epi, '<td><span class="Num">(\d+)</span>')
        if not url or not episode: continue

        thumb = scrapertools.find_single_match(data_epi, ' data-src="([^"]+)"')
        if thumb.startswith('/'): thumb = 'https:' + thumb

        title = scrapertools.find_single_match(data_epi, '<td class="MvTbTtl"><a [^>]+>(.*?)</a>')
        title = str(item.contentSeason) + 'x' + episode + ' ' + title

        fecha = scrapertools.find_single_match(data_epi, '<span>(.*?)</span>')
        if fecha: title = title + ' [COLOR gray](' + fecha + ')[/COLOR]'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, 
                                    contentType = 'episode', contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

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

    IDIOMAS = {'castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'VOSE'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, '<li data-typ(?:e|)="episode"(.*?)</li>')

    for match in matches:
        data_key = scrapertools.find_single_match(match, 'data-key="([^"]+)"')
        data_id = scrapertools.find_single_match(match, 'data-id="([^"]+)"')

        lang = scrapertools.find_single_match(match, '-language">(.*?)</p>').lower()
        lang = re.sub('[^a-z]+', '', lang)

        qlty = scrapertools.find_single_match(match, '-equalizer">(.*?)</p>')

        servidor = corregir_servidor(scrapertools.find_single_match(match, '-dns">(.*?)</p>'))

        url = host + '?trembed=%s&trid=%s&trtype=2' % (data_key, data_id)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, 
                              title = '', url = url,
                              language = IDIOMAS.get(lang, lang), quality = qlty
                       ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    url = scrapertools.find_single_match(data, 'src="([^"]+)"')

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
