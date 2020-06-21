# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'http://www.online.tucineclasico.es/'


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Últimas películas', action = 'list_all', url = host + 'peliculas/' ))

    itemlist.append(item.clone ( title = 'Tendencias', action = 'list_all', url = host + 'tendencias/?get=movies' ))
    itemlist.append(item.clone ( title = 'Mejor valoradas', action = 'list_all', url = host + '22-2/?get=movies' ))
    itemlist.append(item.clone ( title = 'Películas VOSE', action = 'list_all', url = host + 'genero/version-original-subtitulada/' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos_ant(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    bloque = scrapertools.find_single_match(data, '<nav class="genres">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)</a>\s*<i>([^<]+)</i>')
    for url, title, num in matches:
        if num == '0': continue
        if 'genero/version-original-subtitulada' in url: continue
        itemlist.append(item.clone( action='list_all', title=title + ' ('+num+')', url=url ))

    return itemlist

def generos(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    bloque = scrapertools.find_single_match(data, '<ul id="menu-generos" class="menu">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)')
    for url, title in matches:
        if 'genero/version-original-subtitulada' in url: continue
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist

def anios(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    bloque = scrapertools.find_single_match(data, '<nav class="releases">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)</a>')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    for ano in range(1948, 1921, -1):
        itemlist.append(item.clone( action = 'list_all', title = str(ano), url = host + 'lanzamiento/' + str(ano) + '/' ))

    return itemlist



def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    if '<h1>' in data: data = data.split('<h1>')[1] # descartar lista de destacadas
    if '<div class="dt_mainmeta">' in data: data = data.split('<div class="dt_mainmeta">')[0] # descartar lista de más vistas
    # ~ logger.debug(data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h4>(.*?)</h4>')
        if not title: title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, ' (\d{4})</span>')
        if not year: year = '-'
        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><span class="icon-chevron-right">')
    if next_page:
       itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all'))

    return itemlist



def get_url(dpost, dnume, dtype, referer):
    logger.info()
    itemlist = []

    post = {'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype}
    data = httptools.downloadpage(host + 'wp-admin/admin-ajax.php', post=post, headers={'Referer':referer}).data
    # ~ logger.debug(data)

    url = scrapertools.find_single_match(data, "(?i) src='([^']+)")
    if not url: url = scrapertools.find_single_match(data, '(?i) src="([^"]+)')

    return url

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'es':'Esp', 'mx':'Lat', 'en':'VOSE'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Fuentes de vídeo
    bloque = scrapertools.find_single_match(data, "<ul id='playeroptionsul'(.*?)</ul>")

    matches = scrapertools.find_multiple_matches(bloque, "<li id='player-option-(\d+)'(.*?)</li>")
    for optnum, enlace in matches:
        # ~ logger.debug(enlace)
        url = scrapertools.find_single_match(data, "<div id='source-player-%s' class='source-box'><div class='pframe'><iframe src=\"([^\"]+)" % optnum)
        if not url:
            dtype = scrapertools.find_single_match(enlace, "data-type='([^']+)")
            dpost = scrapertools.find_single_match(enlace, "data-post='([^']+)")
            dnume = scrapertools.find_single_match(enlace, "data-nume='([^']+)")
            if not dtype or not dpost or not dnume or dnume == 'trailer': continue
            url = get_url(dpost, dnume, dtype, item.url)

        if not url: continue
        servidor = servertools.get_server_from_url(url)
        if not servidor or servidor == 'directo': continue
        url = servertools.normalize_url(servidor, url)

        lang = scrapertools.find_single_match(enlace, "/img/flags/([^.']+)").lower()

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                              title = '', url = url,
                              language = IDIOMAS.get(lang, lang)
                       ))

    return itemlist



def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<div class="result-item">(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))
        
        langs = []
        if 'img/flags/es.png' in article: langs.append('Esp')
        if 'img/flags/mx.png' in article: langs.append('Lat')
        if 'img/flags/en.png' in article: langs.append('VOSE')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(langs), 
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
            
    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, ' href="([^"]+)"[^>]*><span class="icon-chevron-right">')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_search' ))

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
