# -*- coding: utf-8 -*-

import re, os

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://pctfenix.com/'

perpage = 30


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host)

def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo castellano', action = 'list_all', url = host + 'descargar-peliculas/', search_type = 'movie', page=0))
    itemlist.append(item.clone( title = 'Catálogo latino', action = 'list_all', url = host + 'descargar-peliculas/latino', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'descargar-peliculas/estrenos-de-cine/', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'Lo último', action = 'list_last', url = host + 'descargar-lo-ultimo/', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'mas-valorados/', search_type = 'movie', page=0 ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'mas-visitados/', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'descargar-peliculas/hd/', search_type = 'movie', page=0 ))
    itemlist.append(item.clone( title = 'En x264 MKV', action ='list_all', url = host + 'descargar-peliculas/x264-mkv/', search_type = 'movie', page=0 ))
    itemlist.append(item.clone( title = 'En 3D', action ='list_all', search_type = 'movie', url = host + 'descargar-peliculas/3d/', page=0 ))

    itemlist.append(item.clone( title = 'Por calidad en castellano', action = 'calidades', url = host + '/torrents-de-peliculas.html', calidad_type = 'cast' ))
    itemlist.append(item.clone( title = 'Por calidad en latino', action = 'calidades', url = host + '/secciones.php?sec=ultimos_torrents', calidad_type = 'latino' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Lo último', action = 'list_last', url = host + 'descargar-lo-ultimo/', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Series TV', action = 'list_all', url = host + 'descargar-series/', search_type = 'tvshow', page=0 ))
    itemlist.append(item.clone( title = 'Series HD', action = 'list_all', url = host + 'descargar-series/hd/', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'mas-valorados/', search_type = 'tvshow', page=0 ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'mas-visitados/', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    if item.calidad_type == "cast":
        url = host + "descargar-peliculas"
    elif item.calidad_type == "latino":
        url = host + "descargar-peliculas/latino/"

    data = httptools.downloadpage(url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    data = scrapertools.find_single_match(data, r'<div class="title-hd">(.*?)<\/div>')
    matches = scrapertools.find_multiple_matches(data, '<a href="([^"]+)" title="([^"]+)"')

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url if url.startswith("http") else host[:-1] + url, page=0))

    return sorted(itemlist, key=lambda x: x.title)


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.page == 0:
        data = httptools.downloadpage(item.url).data
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

        matches = re.compile('<img src="([^"]+)" alt="([^"]+)".*?a href="([^"]+)".*?<strong>([^<]+)').findall(data)
        num_matches = len(matches)

        for thumb, title, url, qlty in matches:
            if not url or not title: continue

            titulo = title.split('(')[0].strip()

            if "Temp" in titulo and item.search_type == "tvshow": 
                tmdb_title = re.sub('(?i)(Temp.*)', '', titulo)
            else:
                tmdb_title = title

            qlty = qlty.replace('(', '').replace(')', '').strip()

            if not thumb.startswith('http'): thumb = "https:" + thumb

            if item.search_type == 'tvshow':
                if not "/temporada-" in url and not "/capitulo-" in url: continue

                itemlist.append(item.clone( action='temporadas', url=url, title=titulo, thumbnail=thumb,
                                            contentType='tvshow', contentSerieName=tmdb_title, infoLabels={'year': '-'} ))
            else:
                 if "/temporada-" in url or "/capitulo-" in url: continue

                 itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, qualities=qlty,
                                            contentType='movie', contentTitle=titulo, infoLabels={'year': '-'} ))

            if len(itemlist) >= perpage: break          

    else:
        data = httptools.downloadpage(host + "controllers/load-more.php", post="i=%s&c=%s&u=%s" % (item.page, perpage, '/' + item.url.replace(host, ''))).data
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
        matches = re.compile('<img src="([^"]+)" alt="([^"]+)".*?a href="([^"]+)"').findall(data)
        num_matches = len(matches)

        for thumb, title, url in matches:
            if not url or not title: continue

            titulo = title.split('(')[0].strip()
            if "Temp" in titulo and item.search_type == "tvshow": 
                tmdb_title = re.sub('(?i)(Temp.*)', '', titulo)
            else:
                tmdb_title = title

            if not thumb.startswith('http'): thumb = "https:" + thumb

            if item.search_type == 'tvshow':
                if not "/temporada-" in url and not "/capitulo-" in url: continue

                itemlist.append(item.clone( action='temporadas', url=url, title=titulo, thumbnail=thumb,
                                            contentType='tvshow', contentSerieName=tmdb_title, infoLabels={'year': '-'} ))
            else:
                if "/temporada-" in url or "/capitulo-" in url: continue

                itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb,
                                            contentType='movie', contentTitle=titulo, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if num_matches >= perpage:
        itemlist.append(item.clone( title='>> Página siguiente', url=item.url, page=item.page + 1, action='list_all', text_color='coral' ))

    return itemlist


def list_last(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<img src="([^"]+)" alt="([^"]+)".*?a href="([^"]+)".*?<strong>([^<]+)').findall(data)
    num_matches = len(matches)

    for thumb, title, url, qlty in matches[item.page * perpage:]:
        if not url or not title: continue

        titulo = title.split('(')[0].strip()

        if "Temp" in titulo and item.search_type == "tvshow": 
            tmdb_title = re.sub('(?i)(Temp.*)', '', titulo)
        else:
            tmdb_title = title

        qlty = qlty.replace('(', '').replace(')', '').strip()

        if not thumb.startswith('http'): thumb = "https:" + thumb

        if item.search_type == 'tvshow':
            if not "/temporada-" in url and not "/capitulo-" in url: continue

            itemlist.append(item.clone( action='temporadas', url=url, title=titulo, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=tmdb_title, infoLabels={'year': '-'} ))
        else:
            if "/temporada-" in url or "/capitulo-" in url: continue

            itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, qualities=qlty,
                                            contentType='movie', contentTitle=titulo, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break          

    tmdb.set_infoLabels(itemlist)

    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_last', text_color='coral' ))

    return itemlist


def temporadas (item):
    logger.info()
    itemlist = []

    if not item.url.startswith("http"): item.url = host[:-1] + item.url
    data = httptools.downloadpage(item.url).data
    matches = scrapertools.find_multiple_matches(data, r"onClick='modCap\((\d+)\)'>\s*([^<]+)")

    for id, title in matches:
        itemlist.append(item.clone( action='findvideos', title=title, contentType='episode', episodeId=id ))
    return itemlist    


def findvideos(item):
    logger.info()
    itemlist = []

    if not item.url.startswith("http"): item.url = host[:-1] + item.url
    if item.contentType == "movie":
        data = httptools.downloadpage(item.url).data
    else:
        data = httptools.downloadpage("https://pctfenix.com/controllers/show.chapters.php", post="id=%s" %(item.episodeId)).data

    url_torrent = scrapertools.find_single_match(data, '<div class="ctn-download-torrent"><a href="javascript:[^"]+" id="[^"]+" data-ut\s*=\s*"([^"]+)"')

    if '[castellano]' in data: 
        lang = 'Esp'
    else:
        lang = 'Lat'

    if url_torrent:
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', language = lang, url = url_torrent if url_torrent.startswith("http") else "https:" + url_torrent, server = 'torrent'))

    if '<div class="box-content-links">' in data:
        block = scrapertools.find_single_match(data, '<div class="box-content-links">(.*?)</div')
        matches = scrapertools.find_multiple_matches(block, '<a href="([^"]+)".*?">(.*?)</a>')

        for url, servidor in matches:
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', language = lang, url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'controllers/search-mini.php'
       item.post = 's=%s' % texto.replace(" ", "+")
       return list_search(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []

def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, post = item.post).data
    patron = '<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title in matches:
        if not url or not title: continue

        if "/temporada-" in url or "/capitulo-" in url:
            contentType = "tvshow"
        else:
            contentType = "movie"

        titulo = title.split('(')[0].strip()

        if contentType == "tvshow":
            if "Temp" in titulo: 
                tmdb_title = re.sub('(?i)(Temp.*)', '', titulo)
            else:
                tmdb_title = title
        else:
            tmdb_title = title

        if not thumb.startswith('http'): thumb = "https:" + thumb

        tipo = 'tvshow' if contentType == "tvshow" else 'movie'
        if item.search_type not in ['all', tipo]: continue

        sufijo = '' if item.search_type != 'all' else tipo

        if contentType == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == "movie": continue

            itemlist.append(item.clone( action='temporadas', url=url, title=titulo, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=tmdb_title, infoLabels={'year': '-'} ))
        else:
            if not item.search_type == 'all':
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=titulo, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist