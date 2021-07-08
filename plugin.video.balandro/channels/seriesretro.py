# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriesretro.com/'

perpage = 20


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/lista-series/' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host + 'lista-series/episodios-agregados-actualizados/' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letras = letra.lower()

        url = host + 'letter/' + letras + '/'

        itemlist.append(item.clone( action = 'list_alfa', title = letra, url = url ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    patron = 'class="menu-item menu-item-type-taxonomy menu-item-object-category.*?<a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = "list_all", title = title, url = url ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for data_show in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(data_show, '<h3 class="Title">(.*?)</h3>')

        thumb = scrapertools.find_single_match(data_show, 'data-src="([^"]+)"')
        if not thumb: thumb = scrapertools.find_single_match(data_show, '<img src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        url = scrapertools.find_single_match(data_show, '<a href="([^"]+)"')

        year = scrapertools.find_single_match(data_show, '<span class="Year">(.*?)</span>')
        if not year: year = '-'

        name = title.replace('&#038;', '&')

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = name, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        if '<div class="wp-pagenavi">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="wp-pagenavi">.*?<a class="next page-numbers" href="([^"]+)"')
            if next_page:
                itemlist.append(item.clone( action = 'list_all', page = 0, url = next_page, title = '>> Página siguiente', text_color='coral' ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')
    num_matches = len(matches)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)')
        title = scrapertools.find_single_match(match, '<strong>(.*?)</strong>').strip()
        if not url or not title: continue

        if '/aplicacion-oficial-de-seriesretro-com/' in url: continue

        thumb = scrapertools.find_single_match(match, ' data-src="([^"]+)')

        year = scrapertools.find_single_match(match, '<strong>.*?</td><td>Serie</td><td>(\d{4})</span>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article (.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        seas_epis = scrapertools.find_single_match(article, '<span class="ClB">(\d+)x(\d+)</span>')

        if not seas_epis: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        thumb = 'https:' + thumb

        title = scrapertools.find_single_match(article, '<h3 class="Title">(.*?)</h3>')

        fecha = scrapertools.find_single_match(article, '<span class="Year">(.*?)</span>')

        titulo = seas_epis[0] + 'x' + seas_epis[1] + ' ' + title
        if fecha: titulo = titulo + ' (' + fecha + ')'

        itemlist.append(item.clone( action = 'findvideos', title = titulo, url = url, thumbnail = thumb,
                                    contentType = 'episode', contentSerieName = title, contentSeason = seas_epis[0], contentEpisodeNumber = seas_epis[1] ))

    tmdb.set_infoLabels(itemlist)

    if '<div class="wp-pagenavi">' in data:
        if '<a class="next page-numbers"' in data:
            next_url = scrapertools.find_single_match(data, '<a class="next page-numbers".*?href="(.*?)">')

            if next_url:
                itemlist.append(item.clone (url = next_url, title = '>> Página siguiente', action = 'list_epis', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile(' data-tab="(.*?)">Temporada', re.DOTALL).findall(data)

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data

    season = str(item.contentSeason)

    bloque = scrapertools.find_single_match(data, ' data-tab="' + season + '".*?<tbody>(.*?)</tbody>' )

    matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>')

    for data_epi in matches[item.page * perpage:]:
        episode = scrapertools.find_single_match(data_epi, '<span class="Num">(.*?)</span>')

        thumb = scrapertools.find_single_match(data_epi, '<img src="([^"]+)"')
        thumb = 'https:' + thumb

        title = scrapertools.find_single_match(data_epi, ' alt="Imagen.*?<a href=.*?>(.*?)</a>')
        if not title: title = scrapertools.find_single_match(data_epi, ' alt=.*?Imagen.*?<a href=.*?>(.*?)</a>')

        url = scrapertools.find_single_match(data_epi, '<a href="([^"]+)"')

        if not url or not title: continue

        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, 
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'data-tplayernv="Opt(.*?)"><span>(.*?)</span>')

    for opt, servidor in matches:
        servidor = servidor.replace('<strong>', '').replace('</strong>', '')
        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src="([^"]+)"')
        if url.startswith('//') == True:
            url = scrapertools.find_single_match(data, ' id="Opt' + str(opt) + '.*?src=&quot;(.*?)&quot;')

        if not servidor or not url: continue

        if 'opción' in servidor:
            link_other = servidor
            servidor = 'directo'
        elif servidor == 'anavids':
            link_other = servidor
            servidor = 'directo'
        else: link_other = ''

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '',  language = 'Lat', other = link_other ))

    # Descargas
    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')

    for match in matches:
        servidor = scrapertools.find_single_match(match, 'alt="Descargar(.*?)">')
        servidor = servidor.replace('.', '').strip()

        if not servidor: continue

        servidor = servertools.corregir_servidor(servidor)

        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '',  language = 'Lat', other = 'd' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    if url.startswith(host):
        if item.other == 'd':
            url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')
        else:
            data = httptools.downloadpage(url).data
            if item.other == 'anavids':
                url = scrapertools.find_single_match(data, '<IFRAME SRC="(.*?)"')

                data = httptools.downloadpage(url).data
                url = scrapertools.find_single_match(str(data), 'sources.*?"(.*?)"')
            else:
                url = scrapertools.find_single_match(data, 'src="([^"]+)"')

    if url:
        if url.startswith('//') == True: url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        if servidor:
            url = servertools.normalize_url(servidor, url)
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
