# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

HOST = 'https://mega1link.com/'

perpage = 20 # preferiblemente un múltiplo de los elementos que salen en la web (5x8=40) para que la subpaginación interna no se descompense


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []
    
    itemlist.append(item.clone( title='Últimas actualizadas', action='list_all', url=HOST + 'peliculas/' ))

    itemlist.append(item.clone( title='Castellano', action='list_all', url=HOST + 'tag/espanol-castellano/' ))
    itemlist.append(item.clone( title='Latino', action='list_all', url=HOST + 'tag/espanol-latino/' ))
    itemlist.append(item.clone( title='Subtitulado', action='list_all', url=HOST + 'tag/subtitulada/' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por calidades', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(HOST).data

    bloque = scrapertools.find_single_match(data, 'Genero</a>\s*<ul class="sub-menu">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)')
    for url, title in matches:
        if '/genero/' not in url: continue
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    itemlist.append(item.clone ( action = 'list_all', title = 'Bélica', url=HOST + 'belica/' ))
    itemlist.append(item.clone ( action = 'list_all', title = 'Western', url=HOST + 'western/' ))

    return sorted(itemlist, key=lambda it: it.title)

def calidades(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(HOST).data

    bloque = scrapertools.find_single_match(data, 'Calidad</a>\s*<ul class="sub-menu">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    if '<h1>Películas</h1>' in data: data = data.split('<h1>Películas</h1>')[1]

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        article = scrapertools.decodeHtmlentities(article)
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if year:
            title = re.sub(' %s$' % year, '', title)
            title = re.sub(' \(%s\)$' % year, '', title)
        else:
            year = '-'
        title_alt = title.split(' / ')[0].strip() if ' / ' in title else '' # para mejorar detección en tmdb
        if not title_alt and ' – ' in title: title_alt = title.split(' – ')[0].strip()

        qlty = scrapertools.find_single_match(article, '<span class="quality">([^<]+)')
        qlty = re.sub(' -$', '', qlty)
        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all' ))
            buscar_next = False

    if buscar_next:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><span class="icon-chevron-right')
        if next_page:
           itemlist.append(item.clone (url = next_page, page = 0, title = '>> Página siguiente', action = 'list_all'))

    return itemlist



# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['tscam', 'brscreener', 'dvdrip', 'hd720p', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'Español Castellano': 'Esp', 'Español Latino': 'Lat', 'Subtitulada': 'VOSE'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Enlaces en descargas
    bloque = scrapertools.find_single_match(data, "<div id='download'(.*?)</table>")
    matches = re.compile('<tr(.*?)</tr>', re.DOTALL).findall(bloque)
    for lin in matches:
        # ~ logger.debug(lin)
        if '<th' in lin: continue

        url = scrapertools.find_single_match(lin, " href='([^']+)")
        if url.startswith('//'): url = 'https:' + url
        server = servertools.corregir_servidor(scrapertools.find_single_match(lin, "domain=([^.']+)"))
        if not url or not server: continue
        
        qlty = scrapertools.find_single_match(lin, "<strong class='quality'>([^<]+)").replace('mp4', '').strip()
        lang = scrapertools.find_single_match(lin, "<td>([^<]+)")

        itemlist.append(Item( channel = item.channel, action = 'play', server = server,
                              title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty)
                       ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith(HOST):
        data = httptools.downloadpage(item.url).data
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, '<a id="link"[^>]*href="([^"]+)')
        if url:
            servidor = servertools.get_server_from_url(url)
            if servidor and servidor != 'directo':
                url = servertools.normalize_url(servidor, url)
                itemlist.append(item.clone( url=url, server=servidor ))
        
    else:
        itemlist.append(item.clone())

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<div class="result-item">(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        article = scrapertools.decodeHtmlentities(article)
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(title, '\((\d{4})\)')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))
        
        if year:
            title = re.sub(' %s$' % year, '', title)
            title = re.sub(' \(%s\)$' % year, '', title)
        else:
            year = '-'
        title_alt = title.split(' / ')[0].strip() if ' / ' in title else '' # para mejorar detección en tmdb
        if not title_alt and ' – ' in title: title_alt = title.split(' – ')[0].strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))
            
    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, ' href="([^"]+)"[^>]*><span class="icon-chevron-right">')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_search' ))

    return itemlist

def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = HOST + '/?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
