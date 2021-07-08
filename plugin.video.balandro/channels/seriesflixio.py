# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

host = 'https://seriesflix.io/'

perpage = 18


def do_downloadpage(url, post=None, headers=None, follow_redirects=False):
    data = httptools.downloadpage(url, post=post, headers=headers, follow_redirects=follow_redirects).data

    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-series-online/' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'generos', search_type = 'tvshow', grupo = 'productoras' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Categorías</h3>(.*?)>Estreno</h3>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">(.*?)</a>(.*?)</li>')

    for url, tit, tot in matches:
        if item.grupo == 'productoras':
            if 'series-de-' not in url: continue
        else:
            if 'series-de-' in url: continue

            if tit == 'Argentinas': continue
            elif tit == 'Colombianas': continue
            elif tit == 'Españolas': continue
            elif tit == 'Mexicanas': continue
            elif tit == 'Rusas': continue
            elif tit == 'Turcas': continue

        title = tit.replace('Series de', '').strip()
        if tot: title = title + ' %s' % tot.strip()

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    labels_paises = [
          ('argentinas'),
          ('colombianas'),
          ('espanolas'),
          ('mexicanas'),
          ('rusas'),
          ('turcas')
      ]

    for x in labels_paises:
        if x == 'turcas':
            url = host + 'genero/' + x + '/'
        else:
            url = host + 'genero/series-' + x + '/'

        title = x.capitalize()
        if title == 'Espanolas': title = 'Españolas'

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1 class="section-title">(.*?)class="navigation pagination">')

    matches = scrapertools.find_multiple_matches(bloque, '<article class="(.*?)</article>')
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' class="entry-title">(.*?)</h2>').strip()
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="([^"]+)')

        year = scrapertools.find_single_match(article, ' class="year">(\d{4})</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        if 'class="navigation pagination">' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?<a class="page-link" href="(.*?)">')
            if next_page:
               itemlist.append(item.clone (url = next_page, page = 0, title = '>> Página siguiente', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<div class="aa-drp choose-season">.*?<a href="(.*?)".*?class="btn lnk npd aa-arrow-right">Temporada<dt class="n_s" style="display: inline">(.*?)</dt>'
    matches = scrapertools.find_multiple_matches(data, patron)

    for url, numtempo in matches:
        numtempo = int(numtempo)

        title = 'Temporada ' + str(numtempo)

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.url = url
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        titulo = title
        if len(matches) >= 10:
            if len(str(numtempo)) == 1:
                titulo = title = 'Temporada 0' + str(numtempo)

        itemlist.append(item.clone( action = 'episodios', title = titulo, url = url, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key = lambda it: it.title)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for data_epi in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(data_epi, '<a href="([^"]+)"')
        episode = scrapertools.find_single_match(data_epi, '<span class="num-epi">.*?x(.*?)</span>')
        if not url or not episode: continue

        title = scrapertools.find_single_match(data_epi, '<h2 class="entry-title">(.*?)</h2>')
        title = title.replace(str(item.contentSeason) + 'x' + episode, '').strip()
        title = str(item.contentSeason) + 'x' + episode + ' ' + title

        fecha = scrapertools.find_single_match(data_epi, '<span>(.*?)</span>')
        if fecha: title = title + ' [COLOR gray](' + fecha + ')[/COLOR]'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

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

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, 'href="#options-(.*?)">(.*?)</li>')

    for ref, match in matches:
        servidor = scrapertools.find_single_match(match, 'span class="server">(.*?) -').strip().lower()
        servidor = corregir_servidor(servidor)

        lang = scrapertools.find_single_match(match, 'span class="server">.*?- .*? (.*?)</span>')
        lang = lang.replace('🟢', '').replace('⚪️', '').strip().lower()

        url = scrapertools.find_single_match(data, 'id="options-' + ref + '.*?data-src="(.*?)"')

        url = url.replace('&#038;', '&')

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                              language = IDIOMAS.get(lang, lang) ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    url = scrapertools.find_single_match(data, 'src="([^"]+)"')
    if url.startswith('/'): url = host + url[1:]

    if '/flixplayer.' in url:
        data = httptools.downloadpage(url).data
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, 'link":"([^"]+)"')

    elif host in url and '?h=' in url:
        fid = scrapertools.find_single_match(url, "h=([^&]+)")
        url2 = url.replace('index.php', '').split('?h=')[0] + 'r.php'
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
