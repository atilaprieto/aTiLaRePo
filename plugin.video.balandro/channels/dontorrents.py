# -*- coding: utf-8 -*-

import re, os, string

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://dontorrents.one/'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    url = url.replace('/dontorrents.org/', '/dontorrents.one/')
    url = url.replace('/dontorrents.net/', '/dontorrents.one/')
    url = url.replace('/dontorrent.one/', '/dontorrents.one/')

    # ~ data = httptools.downloadpage(url, post=post).data
    data = httptools.downloadpage_proxy('dontorrents', url, post=post, headers=headers).data
    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))
    itemlist.append(item.clone( title = 'Documentales', action = 'mainlist_documentary' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/page/1', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'Lo último', action = 'list_last', url = host + 'ultimos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En 4K', action = 'list_all', url = host + 'peliculas/4K/page/1', search_type = 'movie', page=0 ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'peliculas/hd/page/', search_type = 'all', page=0 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie', tipo = 'genero', page=0 ))

    itemlist.append(item.clone( title = 'Por año', action = 'call_post', url = host + 'peliculas/buscar', search_type = 'movie', tipo = 'anyo', page=0 ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'listado_alfabetico', url = host + 'peliculas/buscar', search_type = 'movie', tipo = 'letra', page=0 ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/letra-.', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Lo último', action = 'list_last', url = host + 'ultimos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'series/hd/letra-.', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'listado_alfabetico', url = host + 'tv-series', search_type = 'tvshow', page=0 ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_documentary(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'documentales/letra-.', page=0, search_type = 'documentary'))

    itemlist.append(item.clone( title = 'Lo último', action = 'list_last', url = host + 'ultimos', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'listado_alfabetico', url = host + 'documentales', search_type = 'documentary', page=0 ))

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary' ))

    return itemlist


def call_post(item):
    logger.info()

    if not item.page: item.page = 0

    if item.tipo == 'anyo':
        val = platformtools.dialog_numeric(0, "Introduzca el año de búsqueda", default="")
        item.post = "campo=%s&valor=%s&valor2=&valor3=&valor4=&pagina=" % ('anyo', val)
    elif item.tipo == 'genero':
        item.post = "campo=%s&valor=&valor2=%s&valor3=&valor4=&pagina=" % ('genero', item.genre)
    elif item.tipo == 'letra':
        if item.search_type == 'movie':
            item.post = "campo=%s&valor=&valor2=&valor3=%s&valor4=&pagina=" % ('letra', item.letra)
        else:
            if item.search_type == "tvshow": tipo = "series"
            else: tipo = "documentales"
            item.url = host + "%s/letra-%s" %(tipo, item.letra.lower())
            return list_all(item)
 
    return list_post(item)


def generos(item):
    logger.info()
    itemlist = []

    genres = ['Acción',
       'Animación',
       'Aventuras',
       'Bélica',
       'Biográfica',
       'Ciencia Ficción',
       'Cine Negro',
       'Comedia',
       'Crimen',
       'Documental',
       'Drama',
       'Fantasía',
       'Musical',
       'Romántica',
       'Suspense',
       'Terror',
       'Western'
       ]

    for genre in genres:
        itemlist.append(item.clone( action = "call_post", title = genre, url = host + 'peliculas/buscar', tipo='genero', genre=genre, page=0 ))

    return itemlist


def listado_alfabetico(item):
    logger.info()
    itemlist = []

    for letra in string.ascii_uppercase:
        itemlist.append(item.clone(action="call_post", title=letra, letra=letra, tipo='letra'))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    if item.search_type == "movie": search_type = "PELÍCULAS"
    elif item.search_type == "tvshow": search_type = "SERIES"
    elif item.search_type == "documentary": search_type = "DOCUMENTALES"

    data = do_downloadpage(item.url)

    match = re.compile("""(?s)<div class="h5 text-dark">%s:<\/div>(.*?)<br><br>""" % (search_type)).findall(data)[0]
    matches = re.compile(r"""<span class="text-muted">\d+-\d+-\d+<\/span> <a href='([^']+)' class="text-primary">([^<]+)""").findall(match)

    for url, title in matches:
        if "(" in title: title = title.split("(")[0]

        if item.search_type== 'tvshow':
            itemlist.append(item.clone( action='episodios', url=host + url, title=title, 
                                        contentType=item.search_type, contentSerieName=title, infoLabels={'year':"-"} ))
        else:
            itemlist.append(item.clone( action='findvideos', url=host + url, title=title,
                                        contentType=item.search_type, contentTitle=title, infoLabels={'year': "-"} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    sufijo = ''

    if item.search_type == "movie":
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
        patron = r'<a href="([^"]+)">\s*<img.*?src="([^"]+)'
        matches = re.compile(patron).findall(data)

        for url, thumb in matches:
            title = os.path.basename(os.path.normpath(url)).replace("-", " ")
            if "4K" in title: title = title.split("4K")[0]
            if "ESP" in title: title = title.split("ESP")[0]

            thumb if "http" in thumb else "https:" + thumb

            itemlist.append(item.clone( action='findvideos', url=host[:-1] + url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': "-"} ))

    elif item.search_type== 'tvshow':
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
        patron = r"<a href='([^']+)'>([^<]+)"
        matches = re.compile(patron).findall(data)

        for url, title in matches:
            if "-" in title: SerieName = title.split("-")[0]
            else: SerieName = title
            itemlist.append(item.clone( action='episodios', url=host[:-1] + url, title=title, fmt_sufijo=sufijo, 
                                        contentType = 'tvshow', contentSerieName = SerieName, infoLabels={'year':"-"} ))

    else:
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
        patron = r"<a href='([^']+)'>([^<]+)"
        matches = re.compile(patron).findall(data)

        for url, title in matches:
            itemlist.append(item.clone( action = 'findvideos', url = host[:-1] + url, title = title, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, contentExtra = 'documentary' ))

    tmdb.set_infoLabels(itemlist)

    next_url = scrapertools.find_single_match(data, '<a class="page-link" href="([^"]+)">Siguiente')
    if next_url:
        next_url if next_url.startswith("http") else host[:-1] + next_url

        itemlist.append(item.clone( title='>> Página siguiente', url=next_url, action='list_all', page=item.page + 1, contentType=item.contentType, text_color='coral' ))

    return itemlist


def list_post(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url, post=item.post + str(item.page + 1))
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '''<a class="position-relative" href="([^"]+)" data-toggle="popover" '''
    patron += '''data-content="<div><p class='lead text-dark mb-0'>([^<]+)'''
    patron += '''<\/p><hr class='my-2'><p>([^<]+).*?src='([^']+)'''
    matches = re.compile(patron).findall(data)

    for url, title, info, thumb in matches:
        itemlist.append(item.clone( action='findvideos', url=host[:-1] + url, title=title, thumbnail=thumb if "http" in thumb else "https:" + thumb,
                                            contentType='movie', contentTitle=title, infoLabels={'year': "-", 'plot': info} ))

    tmdb.set_infoLabels(itemlist)

    next_url = scrapertools.find_single_match(data, '<a class="page-link" href="([^"]+)">Siguiente')
    if next_url:
        itemlist.append(item.clone( title='>> Página siguiente', action='list_post', page=item.page + 1, contentType=item.contentType, text_color='coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = """<td style='vertical-align: middle;'>([^<]+)<\/td>\s*<td>"""
    patron += """<a class="text-white bg-primary rounded-pill d-block shadow-sm text-decoration-none my-1 py-1" """
    patron += """style="font-size: 18px; font-weight: 500;" href='([^']+)'"""

    matches = re.compile(patron).findall(data)

    if not matches:
        matches = scrapertools.find_multiple_matches(data, "<td style='vertical-align.*?>(.*?)</td>.*?<a.*?href='(.*?)'.*?download>Descargar</a>.*?</tr>")

    for title, url in matches:
        s_e = scrapertools.get_season_and_episode(title)

        try:
           season = int(s_e.split("x")[0])
           episode = s_e.split("x")[1]
        except:
           season = 0
           episode = 0

        if url.startswith("//"): url = "https:" + url

        itemlist.append(item.clone( action='findvideos', url=url, title="%s %s" %(title, item.contentSerieName), 
                                    language = 'Esp', contentType = 'episode', contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.contentType == "episode":
        url = item.url
        quality = ""

    elif not item.contentType == "tvshow":
        data = do_downloadpage(item.url)

        quality = scrapertools.find_single_match(data, '<b class="bold">Formato:</b> ([^<]+)<').strip()
        url = scrapertools.find_single_match(data, "href='([^']+)'.*?download>Descargar</a>")

        if url:
            url = url if url.startswith("http") else "https:" + url
    else:
        url = item.url
        quality = ""

    if url:
        if not url == 'https:':
           itemlist.append(Item( channel = item.channel, action = 'play', title = '', quality=quality, url = url, server = 'torrent'))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    headers = {'Referer': host}

    data = do_downloadpage(item.url, headers=headers)

    patron = "<a href='(.*?)'.*?"
    patron += 'class="text-decoration-none">(.*?)</a>'

    matches = re.compile(patron).findall(data)

    for url, title in matches:
        if not url or not title: continue

        if "pelicula" in url:
            contentType = "movie"
        elif "documental" in url:
            contentType = "documentary"
        else:            
            contentType = "tvshow"

        if item.search_type not in ['all', contentType]: continue

        if contentType == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == "movie": continue
            itemlist.append(item.clone( action='episodios', url=host[:-1] + url, title=title, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year':"-"} ))
        else:
            if not item.search_type == 'all':
                if item.search_type == "tvshow": continue

            itemlist.append(item.clone( action='findvideos', url=host[:-1] + url, title=title,
                                        contentType='movie', contentTitle=title, infoLabels={'year': "-"} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist

def search(item, texto):
    logger.info()
    try:
       item.url = host + 'buscar/' + texto
       return list_search(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
