# -*- coding: utf-8 -*-

import re
import sys
import urllib
import urlparse

from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import tmdb
from platformcode import config, logger


host = "https://pedropolis.tv/"


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action="mainlist_pelis", title="Películas", url=host ))
    itemlist.append(item.clone( action="mainlist_series", title="Series", url=host + 'tvshows/' ))
    itemlist.append(item.clone( action="search", title="Buscar..." ))
    
    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    itemlist.append(item.clone( action="peliculas", title="Todas", url=host + 'pelicula/' ))
    if not descartar_xxx:
        itemlist.append(item.clone( action="peliculas", title="Más Vistas", url=host + 'tendencias/?get=movies' ))
        itemlist.append(item.clone( action="peliculas", title="Mejor Valoradas", url=host + 'calificaciones/?get=movies' ))
    itemlist.append(item.clone( action='peliculas', title='Estrenos', url=host + 'genero/estrenos/' ))
    itemlist.append(item.clone( action="generos", title="Por género", search_type="movie" ))
    itemlist.append(item.clone( action="anyos", title="Por año", search_type="movie" ))
    itemlist.append(item.clone( action="search", title="Buscar película...", search_type='movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action="series", title="Todas", url=host + 'serie/' ))
    itemlist.append(item.clone( action="series", title="Más Vistas", url=host + 'tendencias/?get=tv' ))
    itemlist.append(item.clone( action="series", title="Mejor Valoradas", url=host + 'calificaciones/?get=tv' ))
    itemlist.append(item.clone( action="search", title="Buscar serie...", search_type='tvshow' ))

    return itemlist



# ~ def generos_ant(item): # del menú principal (12 géneros)
    # ~ logger.info()
    # ~ itemlist = []
    # ~ if item.search_type != 'movie': return []

    # ~ data = httptools.downloadpage(host).data
    # ~ bloque = scrapertools.find_single_match(data, '<ul class="sub-menu">.*?</ul>')
    # ~ matches = scrapertools.find_multiple_matches(bloque, 'href="([^"]+)">([^"<]+)</a>')
    # ~ for scrapedurl, scrapedtitle in matches:
        # ~ if '/estrenos/' in scrapedurl: continue # ya se muestra en el menú principal
        # ~ itemlist.append(item.clone( action = "peliculas", title = scrapedtitle, url = scrapedurl ))

    # ~ descartar_xxx = config.get_setting('descartar_xxx', default=False)
    # ~ if not descartar_xxx:
        # ~ itemlist.append(item.clone( action = "peliculas", title = 'xxx / adultos', url = host + 'genero/eroticas/' ))

    # ~ return sorted(itemlist, key=lambda it: it.title)

def generos(item):
    logger.info()
    itemlist = []
    if item.search_type != 'movie': return []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = httptools.downloadpage(host+'genero/proximos-estrenos/').data

    bloque = scrapertools.find_single_match(data, '<ul class="genres(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)</a>\s*<i>([^<]+)')
    for url, title, num in matches:
        if num == '0': continue
        if '/estrenos/' in url or '/proximos-estrenos/' in url: continue # en el listado principal / no son géneros
        if descartar_xxx and scrapertools.es_genero_xxx(title): continue
        
        if '/eroticas/' in url: title = 'xxx / adultos'
        else: title = title[0].upper() + title[1:]

        itemlist.append(item.clone( action='peliculas', title='%s (%s)' % (title, num), url=url ))

    return sorted(itemlist, key=lambda it: it.title)

def anyos(item):
    logger.info()
    itemlist = []
    if item.search_type != 'movie': return []

    data = httptools.downloadpage(host+'genero/proximos-estrenos/').data
    bloque = scrapertools.find_single_match(data, '<ul class="releases(.*?)</ul>')
    
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">(\d{4})')
    for url, title in matches:
        itemlist.append(item.clone( action='peliculas', title=title, url=url ))

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)
    if '<div class="pagination"' in data: bloque = scrapertools.find_single_match(data, '<div class="content">(.*?)<div class="pagination"')
    elif '<div class="sidebar' in data: bloque = scrapertools.find_single_match(data, '<div class="content">(.*?)<div class="sidebar')
    else: bloque = data
    
    matches = re.compile('<article.*?</article>', re.DOTALL).findall(bloque)
    for article in matches:
        if ' class="item tvshows"' in article: continue
        thumb, title = scrapertools.find_single_match(article, ' src="([^"]+)" alt="([^"]+)')
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        if '/serie/' in url: continue
        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')
        quality = scrapertools.find_single_match(article, '<span class="quality">(.*?)</span>')
        langs = []
        for lg in scrapertools.find_multiple_matches(article, '/img/flags/([^.]+)\.png'):
            if lg not in langs: langs.append(lg)

        title_alt = title.split(' (')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb
        if not title_alt: title_alt = title.split(' /')[0].strip() if ' / ' in title else '' # para mejorar detección en tmdb
        
        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, contentTitleAlt = title_alt, 
                                    languages=', '.join(langs), qualities=quality, 
                                    infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, "<span class=\"current\">\d+</span><a href='([^']+)'")
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='peliculas' ))

    return itemlist


def series(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, '<div class="content">(.*?)<div class="pagination"')

    matches = re.compile('<article.*?</article>', re.DOTALL).findall(bloque)
    for article in matches:
        thumb, title = scrapertools.find_single_match(article, ' src="([^"]+)" alt="([^"]+)')
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        if '/pelicula/' in url: continue
        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')
        title = title.replace('&#8217;', "'")

        title_alt = title.split(' (')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb
        if not title_alt: title_alt = title.split(' /')[0].strip() if ' / ' in title else '' # para mejorar detección en tmdb

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                    contentType='tvshow', contentSerieName=title, contentTitleAlt = title_alt, 
                                    infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, "<span class=\"current\">\d+</span><a href='([^']+)'")
    if next_page_link:
        itemlist.append(item.clone(title=">> Página siguiente", url=next_page_link, action='series'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<span class="title">([^<]+)<i>'  # season
    matches = scrapertools.find_multiple_matches(data, patron)
    if len(matches) > 1:
        for scrapedseason in matches:
            scrapedseason = " ".join(scrapedseason.split())
            temporada = scrapertools.find_single_match(scrapedseason, '(\d+)')
            itemlist.append(item.clone( action="episodios", title=scrapedseason, contentType='season', contentSeason=temporada ))

        tmdb.set_infoLabels(itemlist)

        itemlist.sort(key=lambda it: it.title)

    if len(itemlist) > 0:
        return itemlist
    else:
        return episodios(item)
    # ~ return itemlist


# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div class="imagen"><a href="([^"]+)">.*?'  # url
    patron += '<div class="numerando">(.*?)</div>.*?'     # numerando cap
    patron += '<a href="[^"]+">([^<]+)</a>'               # title de episodios
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle, scrapedname in matches:
        scrapedtitle = scrapedtitle.replace('--', '0')
        patron = '(\d+) - (\d+)'
        match = re.compile(patron, re.DOTALL).findall(scrapedtitle)
        season, episode = match[0]
        if 'season' in item.infoLabels and int(item.infoLabels['season']) != int(season):
            continue
        title = "%sx%s: %s" % (season, episode.zfill(2), scrapertools.unescape(scrapedname))

        itemlist.append(item.clone(title=title, url=scrapedurl, action="findvideos",
                                   contentType="episode", contentSeason=season, contentEpisodeNumber=episode))

    tmdb.set_infoLabels(itemlist)

    itemlist.sort(key=lambda it: int(it.infoLabels['episode']), reverse=False)

    return itemlist



def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)
    patron = '<div id="option-(\d+)".*?<iframe.*?src="([^"]+)".*?</iframe>'  # lang, url
    matches = re.compile(patron, re.DOTALL).findall(data)
    for option, url in matches:
        # ~ logger.debug(url)
        lang = scrapertools.find_single_match(data, '<li><a class="options" href="#option-%s">.*?</b>(.*?)<span' % option)
        lang = lang.lower().strip()
        idioma = {'latino': 'Lat',
                  'drive': 'Lat',
                  'castellano': 'Esp',
                  'español': 'Esp',
                  'subtitulado': 'VOS',
                  'ingles': 'Eng'}
        if lang in idioma:
            lang = idioma[lang]

        if "bit.ly" in url: # obtenemos redirecionamiento de shorturl en caso de coincidencia
            url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get("location", "")

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, title = item.title,
                              language = lang, quality = item.qualities ))

    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist



def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = urlparse.urljoin(host, "?s={0}".format(texto))
    if item.search_type == '': item.search_type = 'all'
    try:
        return sub_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

def sub_search(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data

    matches = re.compile('<article>(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        tipo = 'tvshow' if 'span class="tvshows"' in article else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"').strip()
        year = scrapertools.find_single_match(article, '<span class="year">(\d+)')
        plot = scrapertools.find_single_match(article, '<div class="contenido"><p>(.*?)</p>').strip()

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))


    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, '<span class="current">\d+</span><a href=\'([^\']+)')
    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='sub_search' ))

    return itemlist
