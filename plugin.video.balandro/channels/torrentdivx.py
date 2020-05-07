# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

# ~ HOST = 'https://www.torrentdivx.com/'
HOST = 'https://www.esdivx.nl/'

perpage = 20 # preferiblemente un múltiplo de los elementos que salen en la web (5x8=40) para que la subpaginación interna no se descompense

def do_downloadpage(url, post=None, headers=None):
    url = url.replace('https://www.torrentdivx.com/', 'https://www.esdivx.nl/') # por si viene de enlaces guardados
    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data



def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    return itemlist

def mainlist_pelis(item):
    logger.info()
    itemlist = []
    
    itemlist.append(item.clone( title='Últimas actualizadas', action='list_all', url=HOST+'movies/', search_type = 'movie' ))
    itemlist.append(item.clone( title='Estrenos', action='list_all', url=HOST + 'tag/estreno/', search_type = 'movie' ))

    itemlist.append(item.clone( title='Castellano', action='list_all', url=HOST + 'tag/castellano/', search_type = 'movie' ))
    itemlist.append(item.clone( title='Latino', action='list_all', url=HOST + 'tag/latino/', search_type = 'movie' ))
    itemlist.append(item.clone( title='Subtitulado', action='list_all', url=HOST + 'tag/subtitulado/', search_type = 'movie' ))

    itemlist.append(item.clone( title='Calidad HdRip', action='list_all', url=HOST + 'tag/hdrip/', search_type = 'movie' ))
    itemlist.append(item.clone( title='Calidad 720p', action='list_all', url=HOST + 'tag/720p/', search_type = 'movie' ))
    itemlist.append(item.clone( title='Calidad 1080p', action='list_all', url=HOST + 'tag/1080p/', search_type = 'movie' ))
    itemlist.append(item.clone( title='Calidad 4k', action='list_all', url=HOST + 'tag/4k/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Últimas series', action='list_all', url=HOST+'tvshows/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    
    data = do_downloadpage(HOST)
    
    bloque = scrapertools.find_single_match(data, 'Generos</a>\s*<ul class="sub-menu">(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"[^>]*>([^<]+)')
    for url, title in matches:
        title = title[0].upper() + title[1:] # algun género no tiene la mayúscula inicial
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    itemlist.append(item.clone ( action = 'list_all', title = 'Bélica', url = HOST + 'genre/belica/' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    
    tit = '<h1>Series de TV</h1>' if item.search_type == 'tvshow' else '<h1>Películas</h1>'
    if tit in data: data = data.split(tit)[1]
    if '<div class="sidebar scrolling">' in data: data = data.split('<div class="sidebar scrolling">')[0]
    
    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    if item.search_type == 'movie': matches = filter(lambda x: not '/tvshows/' in x, matches) # descartar series
    elif item.search_type == 'tvshow': matches = filter(lambda x: not '/movies/' in x, matches) # descartar pelis
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if year:
            title = title.replace('(%s)' % year, '').strip()
        else:
            year = '-'
        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')

        tipo = 'tvshow' if '/tvshows/' in url else 'movie'
        if tipo == 'movie':
            qlty = scrapertools.find_single_match(article, '<span class="quality">([^<]+)')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

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


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    
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

    data = do_downloadpage(item.url)
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



def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'ts', 'webdl', 'webrip', 'bdscr', 'hdtv', 'hc720p', 'bdrip', 'hdrip', '720p', '1080p', '4k']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'Castellano':'Esp', 'Latino':'Lat', 'V.O. Subtitulado':'VOSE', 'Version Original':'VO', 'Version Original +Sub':'VOS', 'Latino - Varios':'Varios'}

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, '<div class="box_links">(.*?)</table>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<tr(.*?)</tr>')
    for enlace in matches:
        if '<th' in enlace or 'torrent' not in enlace: continue
        url = scrapertools.find_single_match(enlace, " href='([^']+)")
        if not url: continue
        tds = scrapertools.find_multiple_matches(enlace, '<td>(.*?)</td>')
        qlty = scrapertools.find_single_match(tds[1], "<strong class='quality'>([^<]+)")
        lang = tds[2]
        othr = tds[3] if tds[3] != '----' else ''

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'torrent', 
                              title = '', url = url,
                              language = IDIOMAS.get(lang,lang), quality = qlty, quality_num = puntuar_calidad(qlty), other = othr
                       ))

    if len(itemlist) == 0: # páginas antiguas con otro formato
        matches = scrapertools.find_multiple_matches(data, ' href="(magnet[^"]+)')
        for url in matches:
            itemlist.append(Item( channel = item.channel, action = 'play', server = 'torrent', title = '', url = url ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith(HOST) and '/links/' in item.url:
        #TODO!? linkwz=true variable !?
        data = do_downloadpage(item.url, post='linkwz=true')
        # ~ logger.debug(data)

        url = scrapertools.find_single_match(data, '<a id="link" rel="nofollow" href="([^"]+)')
        if url:
            itemlist.append(item.clone(url = url))

    else:
        itemlist.append(item.clone())

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="result-item">(.*?)</article>', re.DOTALL).findall(data)
    if item.search_type == 'movie': matches = filter(lambda x: not '/tvshows/' in x, matches) # descartar series
    elif item.search_type == 'tvshow': matches = filter(lambda x: not '/movies/' in x, matches) # descartar pelis
    matches = filter(lambda x: not re.search('\(S\d+E\d+', x), matches) # descartar episodios de series como película
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(title, '\((\d{4})\)')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))
        
        if year:
            title = title.replace('(%s)' % year, '').strip()
        else:
            year = '-'
        title_clean = re.sub('\([^\)]+\)', '', title).strip()
        #Ejs: La Chica Danesa (2015) (DVDrip Latino) / La Chica Danesa (2015) (BDscr Castellano)

        tipo = 'tvshow' if '/tvshows/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title_clean, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title_clean, infoLabels={'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_search' ))
            buscar_next = False

    if buscar_next:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><span class="icon-chevron-right')
        if next_page:
           itemlist.append(item.clone (url = next_page, page = 0, title = '>> Página siguiente', action = 'list_search'))

    return itemlist

def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = HOST + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
