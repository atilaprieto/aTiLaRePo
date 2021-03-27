# -*- coding: utf-8 -*-

import re, string

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://www.subtorrents.nl/'

perpage = 30


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage_proxy('subtorrents', url, post=post, headers=headers).data
    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))

    itemlist.append(item.clone ( title = 'Series', action = 'mainlist_series' ))

    # ~ habra q controlar dato sufijo  en list_all  y list_series
    # ~ y añadir los item clones en cada uno de ellos para q vayan a Findvideos o Temporadas
    #itemlist.append(item.clone( title = 'Buscar ...', action = 'search', url = host, search_type = 'all' ))

    itemlist.append(item_configurar_proxies(item))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-subtituladas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Catálogo castellano ó latino', action = 'list_all', url = host + 'peliculas-subtituladas/?filtro=audio-latino',
                                search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas-subtituladas/?filtro=estrenos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos castellano ó latino', action = 'list_all', url = host + 'peliculas-subtituladas/?filtro=estrenos&filtro2=audio-latino',
                                search_type = 'movie', ))

    itemlist.append(item.clone( title = 'En DVD', action = 'list_all', url = host + 'calidad/dvd-full/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En 3D', action = 'list_all', url = host + 'peliculas-3d/', search_type = 'movie' ))

    itemlist.append(item.clone( title='Por letra (A - Z)', action='alfabetico', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    itemlist.append(item_configurar_proxies(item))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_series', url = host + 'series-2/', search_type = 'tvshow', page = 0 ))

    itemlist.append(item.clone( title='Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    itemlist.append(item_configurar_proxies(item))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<img src="([^"]+)" height=.*\s*<a href="([^"]+)" title="([^"]+)">[^<]+<\/a>\s*<\/td>\s*<td>[^<]+<\/td>\s*<td>([^<]+)<\/td>(?:\s*<td>(.*?)<|)').findall(data)

    for lang, url, title, genre, qlty in matches:
        if not url or not title: continue

        if "series" in genre.lower():
            contentType = "tvshow"
        else:
            contentType = "movie"

        title = title.split("(")[0]
        if "3D" in title: title = title.split("3D")[0]
        if lang.endswith("1.png"):
            lang = "Esp"
        elif lang.endswith("1.png"):
            lang = "Esp"
        elif lang.endswith("2.png"):
            lang = "VO"
        elif lang.endswith("4.png"):
            lang = "Fr"   
        elif lang.endswith("8.png"):
            lang = "It"
        elif lang.endswith("512.png"):
            lang = "Lat"
        else:
            lang = "Vose"

        if contentType == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url=url, title=title, contentType='tvshow', contentSerieName=title ))

        else:
            itemlist.append(item.clone( action='findvideos', url=url, title=title, qualities=qlty, languages=lang,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    next_url = scrapertools.find_single_match(data, "<span class='current'>\d+<\/span><a href='([^']+)'")
    if len(next_url) > 0:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def list_series(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    if '?s=' in item.url:
        blok = scrapertools.find_single_match(data, '<table class="tablaseries2">(.*?)</table>')
        matches = re.compile('<a href="(.*?)".*? title="(.*?)"').findall(blok)
    else:
        matches = re.compile('<option value="[^"]+(\/series\/[^"]+)">([^<]+)').findall(data)

    num_matches = len(matches)

    for url, title in matches[item.page * perpage:]:
        if not url or not title: continue

        title = title.split("(")[0]

        if not host in url:
            url = host + url

        itemlist.append(item.clone( action='temporadas', url=url, title=title, contentType='tvshow', contentSerieName=title ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if '?s=' in item.url:
        if "<div class='pagination'" in data:
            next_page = scrapertools.find_single_match(data, "<div class='pagination'.*?class='current'.*?<a href='(.*?)'")
            if next_page:
                itemlist.append(item.clone( title = '>> Página siguiente', url = next_page, action='list_series', page = 0, text_color = 'coral' ))
    else:
       if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
           hasta = (item.page * perpage) + perpage
           if hasta < num_matches:
               itemlist.append(item.clone( title = '>> Página siguiente', url = item.url, action='list_series', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
       url_letra = host + 'peliculas-subtituladas/?s=letra-'
    else:
       url_letra = host + 'series-2/?s=letra-'

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#':
        title = letra
        if letra == '#': letra = '0'

        url = url_letra + letra.lower()

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = "list_all", title = title, url = url))
        else:
            itemlist.append(item.clone( action = "list_series", title = title, url = url, page = 0))

    return itemlist


def temporadas (item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, r'">Temporada (\d+)<')

    for tempo in sorted(matches):
        title = "Temporada " + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url=item.url, contentType = 'season', contentSeason = int(tempo), page = 0 ))

    return itemlist    


def episodios (item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('a href="([^"]+)" class="link-torrent-serie" title="([^"]+)').findall(data)

    for url, title in matches:
        s_e = scrapertools.get_season_and_episode(title)
        season = int(s_e.split("x")[0])
        episode = s_e.split("x")[1]

        if not item.contentSeason: continue
        elif not str(item.contentSeason) == str(season): continue

        itemlist.append(item.clone( action='findvideos', url=url, title=title, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

    return sorted(itemlist, key=lambda x: x.contentEpisodeNumber)


def findvideos(item):
    logger.info()
    itemlist = []

    if item.contentType == "movie":
        data = do_downloadpage(item.url)

        url_torrent = re.compile('<a href="([^"]+)" title=".*?" class="fichabtndes linktorrent"').findall(data)[0]
    else:
        url_torrent = item.url

    itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url_torrent, server = 'torrent'))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.endswith('.torrent'):
        # Opció 2, el gestor de torrents amb url local
        import os
        from platformcode import config
            
        data = do_downloadpage(item.url)
        file_local = os.path.join(config.get_data_path(), "temp.torrent")
        with open(file_local, 'w') as f: f.write(data); f.close()
            
        itemlist.append(item.clone( url = file_local, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       if item.search_type == 'movie':
           item.url = host + 'peliculas-subtituladas/'
       else:
           item.url = host + 'series-2/'

       item.url = item.url + '?s=' + texto.replace(" ", "+")

       if item.search_type == 'movie':
           return list_all(item)
       else:
           return list_series(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []