# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://www.pelispedia.biz/'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone ( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone ( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    return itemlist

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Últimas películas', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Tendencias', action = 'list_all', url = host + 'tendencias/?get=movies', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Últimas series', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))
    itemlist.append(item.clone ( title = 'Tendencias', action = 'list_all', url = host + 'tendencias/?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    bloque = scrapertools.find_single_match(data, '<nav class="genres">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)</a>\s*<i>([^<]+)</i>')
    for url, title, num in matches:
        itemlist.append(item.clone( action='list_all', title=title + ' ('+num+')', url=url ))

    return itemlist

def anios(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(host).data
    
    bloque = scrapertools.find_single_match(data, '<nav class="releases">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)</a>')
    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

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

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            qlty = scrapertools.find_single_match(article, '<span class="quality">([^<]+)')
            
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><span class="icon-chevron-right">')
    if next_page:
       itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    
    matches = re.compile("<span class='title'>Temporada (\d+)", re.DOTALL).findall(data)
    for numtempo in matches:
        itemlist.append(item.clone( action='episodios', title='Temporada %s' % numtempo,
                                    contentType='season', contentSeason=numtempo ))
        
    tmdb.set_infoLabels(itemlist)

    return itemlist

# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)

def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    if item.contentSeason: # reducir datos a la temporada pedida
        data = scrapertools.find_single_match(data, "<span class='se-t[^']*'>%s</span>(.*?)</ul>" % item.contentSeason)

    matches = re.compile('<li(.*?)</li>', re.DOTALL).findall(data)
    for data_epi in matches:
        try:
            url, title = scrapertools.find_single_match(data_epi, "<a href='([^']+)'>([^<]*)</a>")
            season, episode = scrapertools.find_single_match(data_epi, "<div class='numerando'>(\d+) - (\d+)")
        except:
            continue
        if not url or not season or not episode: continue
        if item.contentSeason and item.contentSeason != int(season): continue

        thumb = scrapertools.find_single_match(data_epi, " src='([^']+)")
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist



# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'tsscreener', 'brscreener', 'sd480p', 'dvdrip', 'hdrip', 'hd720p', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def normalize_server(server):
    server = servertools.corregir_servidor(server)
    return server

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'es':'Esp', 'mx':'Lat', 'en':'VOSE',  'spanish':'Esp','español':'Esp', 'latino':'Lat', 'subtitulado':'VOSE'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    # Enlaces en embeds
    bloque = scrapertools.find_single_match(data, "<ul id='playeroptionsul'(.*?)</ul>")
    matches = scrapertools.find_multiple_matches(bloque, '<li(.*?)</li>')
    for datos in matches:
        if "data-nume='trailer'" in datos: continue
        url = scrapertools.find_single_match(datos, " data-playerid='([^']+)")
        if not url: continue

        servidor = servertools.get_server_from_url(url)
        if not servidor or (servidor == 'directo' and 'stream-mx.com/' not in url): continue
        url = servertools.normalize_url(servidor, url)

        lang = scrapertools.find_single_match(datos, 'img/flags/([^.]+)')

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                              title = '', url = url, 
                              language = IDIOMAS.get(lang, lang) #, other = 'e'
                       ))

    # Enlaces en descargas
    bloque = scrapertools.find_single_match(data, "<div id='download'(.*?)</table>")
    matches = re.compile('<tr(.*?)</tr>', re.DOTALL).findall(bloque)
    for lin in matches:
        # ~ logger.debug(lin)
        if '<th' in lin: continue

        url = scrapertools.find_single_match(lin, " href='([^']+)")
        if url.startswith('//'): url = 'https:' + url
        server = scrapertools.find_single_match(lin, "domain=([^.']+)")
        if not url or not server: continue
        
        tds = scrapertools.find_multiple_matches(lin, '<td>(.*?)</td>')
        if len(tds) != 7: continue
        
        qlty = scrapertools.find_single_match(tds[1], "<strong class='quality'>([^<]+)")
        lang = tds[2].lower()
        other = tds[5]
        author = scrapertools.find_single_match(tds[6], "/author/([^/]+)")
        if author: other += ', ' + author

        itemlist.append(Item( channel = item.channel, action = 'play', server = normalize_server(server),
                              title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty), other = other
                       ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith(host):
        data = httptools.downloadpage(item.url).data
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, '<a id="link"[^>]*href="([^"]+)')
        if url:
            servidor = servertools.get_server_from_url(url)
            if servidor and servidor != 'directo':
                url = servertools.normalize_url(servidor, url)
                itemlist.append(item.clone( url=url, server=servidor ))
        
    elif 'stream-mx.com/' in item.url:
        data = httptools.downloadpage(item.url).data
        # ~ logger.debug(data)
        bloque = scrapertools.find_single_match(data, '"sources":\s*\[(.*?)\]')
        for enlace in scrapertools.find_multiple_matches(bloque, "\{(.*?)\}"):
            v_url = scrapertools.find_single_match(enlace, '"file":\s*"([^"]+)')
            if not v_url: continue
            v_type = scrapertools.find_single_match(enlace, '"type":\s*"([^"]+)')
            if v_type == 'hls':
                itemlist.append(item.clone(url = v_url, server = 'm3u8hls'))
            else:
                v_lbl = scrapertools.find_single_match(enlace, '"label":\s*"([^"]+)')
                itemlist.append([v_lbl, v_url])

    else:
        itemlist.append(item.clone())

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
        title_alt = title.split('(')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))
        
        if tipo == 'movie':
            langs = [] # descartado pq acostumbra a haber más idiomas de los que salen
            # ~ if 'img/flags/es.png' in article: langs.append('Esp')
            # ~ if 'img/flags/mx.png' in article: langs.append('Lat')
            # ~ if 'img/flags/en.png' in article: langs.append('VOSE')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, languages = ', '.join(langs), 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))

            
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
