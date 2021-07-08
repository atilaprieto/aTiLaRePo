# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://senininternetin.com/'

IDIOMAS = {'Español': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose'}


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    url = url.replace('/www.tupelihd.com/', '/senininternetin.com/')

    raise_weberror = False if '/peliculas/estrenos-' in url else True

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


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

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'todas-las-peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Estrenos', action = 'estrenos', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Más vistas', action = 'list_all', url = host + 'peliculas-mas-vistas/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Más votadas', action = 'list_all', url = host + 'mas-votadas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por país', action = 'paises', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def estrenos(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Estrenos 2021', action = 'list_all', url = host + 'peliculas/estrenos-2021/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Estrenos 2020', action = 'list_all', url = host + 'peliculas/estrenos-2020/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Estrenos 2019', action = 'list_all', url = host + 'peliculas/estrenos-2019/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Estrenos 2018', action = 'list_all', url = host + 'peliculas/estrenos-2018/', search_type = 'movie' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'En 4K UHD Micro', action = 'list_all', url = host + 'peliculas/4k-uhdmicro/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'En 4K UHD Rip', action = 'list_all', url = host + 'peliculas/4k-uhdrip/', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'En Bluray MicroHD', action = 'list_all', url = host + 'peliculas/bluray-microhd/', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'Generos</span></a>\s*<ul class="sub-menu">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"><i[^>]*></i><span>([^<]+)')
    for url, title in matches:
        if '/estrenos/' in url: continue

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    labels_paises = [
          ('Alemania', 'germany'),
          ('Argentina', 'argentina'),
          ('Australia', 'australia'),
          ('Canadá', 'canada'),
          ('China', 'china'),
          ('España', 'spain'),
          ('Estados Unidos', 'united-states-of-america'),
          ('Francia', 'france'),
          ('Hong Kong', 'hong-kong'),
          ('India', 'india'),
          ('Italia', 'italy'),
          ('Japón', 'japan'),
          ('Mejico', 'mexico'),
          ('Reino Unido', 'united-kingdom'),
          ('Rusia', 'russia')
          ]

    for x in labels_paises:
        url = host  + 'country/' + x[1] + '/'

        itemlist.append(item.clone( title = x[0], url = url, action = 'list_all' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letras = letra.lower()
        if letras == '#': letras = '0-9'

        url = host + 'letters/' + letras + '/'

        itemlist.append(item.clone( action = 'list_alfa', title = letra, url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<section>(.*?)</section>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')

        title = scrapertools.find_single_match(article, '<div class="Title">(.*?)</div>')
        if not title: title = scrapertools.find_single_match(article, '<h2 class="Title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = '-'

        tipo = 'tvshow' if '>Serie TV</span>' in article else 'movie'
        if item.search_type not in ['all', tipo]: continue

        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            qlty_lang = scrapertools.find_single_match(article, '<span class="calidad">(.*?)</span')
            if '|' in qlty_lang:
                qlty = qlty_lang.split('|')[0].strip()
                lang = qlty_lang.split('|')[1].strip()
            else:
                qlty = qlty_lang
                lang = ''

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        qualities=qlty, languages=IDIOMAS.get(lang, lang),
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if '>Siguiente &raquo;</a' in data:
        next_page = scrapertools.find_single_match(data, "class='page-numbers current'>.*?<a class='page-numbers'.*?" + 'href="([^"]+)')

        if next_page:
           itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all', text_color='coral' ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)')
        title = scrapertools.find_single_match(match, '<strong>(.*?)</strong>').strip()
        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)')
        year = scrapertools.find_single_match(match, '<strong>.*?<td>(.*?)</td>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if "<div class='wp-pagenavi'" in data:
        next_page = scrapertools.find_single_match(data, "class='current'>.*?" + 'href="(.*?)"')

        if next_page:
           itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_alfa', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-tab="(.*?)"', re.DOTALL).findall(data)

    for  numtempo in matches:
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

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'data-tab="' + str(item.contentSeason) + '".*?<table>(.*?)</table>')

    matches = re.compile('<td><span class="Num">(.*?)</span>.*?<img src="(.*?)".*?<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for epis, thumb, url, title in matches[item.page * perpage:]:
        if thumb.startswith('//'): thumb = 'https:' + thumb

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + title

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSeason=item.contentSeason, contentEpisodeNumber=epis ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()

    orden = [
	'cam',
	'hdcam',
	'webscreener',
	'tsscreener',
	'hdtcscreener',
	'brscreener',
	'hdtv',
	'hdtv720p',
	'microhd',
	'dvdrip',
	'bluraymicrohd',
	'blurayrip',
	'hdrip',
	'hd720',
	'hd1080',
	'4kuhdmicro'
	]

    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def normalize_server(server):
    server = servertools.corregir_servidor(server)
    if server:
        server = server.replace('.com', '').replace('.net', '').replace('.to', '')

    if server == 'uploaded': return 'uploadedto'
    return server

def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, '<section class="section player(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, ' href="#options-(.*?)".*?class="server">(.*?)</span>')

    # Enlaces en opciones
    for opt, server_idioma in matches:
        s_i = scrapertools.find_single_match(server_idioma, '(.*?)-(.*?)$')
        if not s_i: continue

        servidor = s_i[0].strip().lower()
        if not servidor: continue
        elif servidor == 'youtube': continue

        lang = s_i[1].strip()

        url = scrapertools.find_single_match(bloque, '<div id="options-' + opt + '.*?<iframe src="(.*?)"')
        if not url: url = scrapertools.find_single_match(bloque, '<div id="options-' + opt + '.*?<iframe data-src="(.*?)"')
        if not url: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = normalize_server(servidor), title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), other = 'e' ))

    # Enlaces en descargas
    if '>Enlaces<' in data:
        bloque = scrapertools.find_single_match(data, '<table>(.*?)</table>')

        matches = re.compile('<td><span class="Num">(.*?)</tr>', re.DOTALL).findall(bloque)

        for match in matches:
            url = scrapertools.find_single_match(match, ' href="([^"]+)"')
            if url.startswith('//'): url = 'https:' + url
            if not url: continue

            servidor = scrapertools.find_single_match(match, 'alt=".*?">(.*?)</span>').strip()
            if not servidor: continue

            lang = scrapertools.find_single_match(match, 'alt="Idioma">(.*?)</span>').strip()
            qlty = scrapertools.find_single_match(match, 'alt="Idioma">.*?<td><span>(.*?)</span>').strip()

            other = ''
            if servidor.lower() != 'torrent':
                if servidor.lower() == 'senininternetin':
                    other = 't'
                    servidor = ''

            itemlist.append(Item( channel = item.channel, action = 'play', server = normalize_server(servidor), title = '', url = url,
                                  language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) , other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&').replace(' class=', '')

    url = ''

    if item.other:
        if not item.url.startswith == host:
            return itemlist

    if item.server == 'torrent':
        import os
        from platformcode import config

        data = do_downloadpage(item.url)
        file_local = os.path.join(config.get_data_path(), "temp.torrent")
        with open(file_local, 'wb') as f: f.write(data); f.close()
            
        itemlist.append(item.clone( url = file_local, server = 'torrent' ))
        return itemlist

    elif item.other == 't':
        url = httptools.downloadpage(item.url, only_headers = True, follow_redirects = False).headers.get('location')

        if url:
            # Provar si el gestor de torrents accepta una url que conté un format .torrent
            if url.endswith('.torrent'):
               itemlist.append(item.clone( url = url, server = 'torrent' ))
               return itemlist

            import os
            from platformcode import config

            data = do_downloadpage(url)
            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()
            
            itemlist.append(item.clone( url = file_local, server = 'torrent' ))
            return itemlist

    else:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')

    if url:
       if item.server == 'torrent':
            itemlist.append(item.clone(url = url, server = item.server))
       else:
            servidor = servertools.get_server_from_url(url)
            if servidor and servidor != 'directo':
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
