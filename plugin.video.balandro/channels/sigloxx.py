# -*- coding: utf-8 -*-

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://videos.2000peliculassigloxx.com/'

host2 = 'https://2000peliculassigloxx.com/'


perpage_list_all = 10
perpage_list_film = 25


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    # ~ itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por actor', action = 'biografias', url = host2 + 'actores/' ))
    itemlist.append(item.clone ( title = 'Por actriz', action = 'biografias', url = host2 + 'actrices/' ))
    itemlist.append(item.clone ( title = 'Por dirección, guionistas, productores', action = 'biografias', url = host2 + 'directores/' ))
    itemlist.append(item.clone ( title = 'Por compositores, escritores, novelistas', action = 'biografias', url = host2 + 'otras-biografias/' ))

    # ~ itemlist.append(item.clone ( title = 'Por letra (A - Z)', action='alfabetico' ))

    # ~ itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    url = host2
    data = httptools.downloadpage(url).data

    bloque = scrapertools.find_single_match(data, '<nav id="site-navigation"(.*?)</nav><!-- #site-navigation -->')

    matches = scrapertools.find_multiple_matches(bloque, '<li id=".*?<a href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        if not url or not title: continue

        if not '/anos-' in url: continue

        itemlist.append(item.clone( action = 'list_filmografias', title = title, url = url ))

    return itemlist


def biografias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if '/otras-biografias' in item.url:
        matches = scrapertools.find_multiple_matches(data, '<li><a href="([^"]+)".*?rel="noopener noreferrer">(.*?)</a>')

        for url, title in matches:
            if not url or not title: continue

            itemlist.append(item.clone( action= 'list_filmografias', title = title, url = url ))
    else:
       matches = scrapertools.find_multiple_matches(data, '<figure.*?<a href="([^"]+)".*?src="([^"]+)".*?alt="(.*?)".*?</figure>')

       for url, thumb, title in matches:
           if not url or not title: continue

           itemlist.append(item.clone( action = 'list_filmografias', title = title, url = url, thumbnail = thumb ))

    return sorted(itemlist, key = lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(host, use_cache = True).data

    matches = scrapertools.find_multiple_matches(data, '<li class="page_item page-item-.*?<a href="([^"]+)">(.*?)</a>')

    num_matches = len(matches)
    desde = item.page * perpage_list_all
    hasta = desde + perpage_list_all

    if matches: platformtools.dialog_notification('SigloXX', '[COLOR blue]Cargando películas[/COLOR]')

    for url, title in matches[desde:hasta]:
        if not url or not title: continue

        thumb_data = httptools.downloadpage(url).data

        thumb = scrapertools.find_single_match(thumb_data, '<div class="entry-content">.*?background:.*?url(.*?) ')
        thumb = thumb.replace('(', '').replace(')', '')

        name = title.strip()

        try:
            year = title.split('(')[1]
            year = year.split(',')[0]

            if year:
                title = title.replace(year + ', ', '')

                name = title
                name = name.split('(')[0]
                name = name.strip()
        except:
            year = ''

        if not year: year = '-'

        itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = name, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if num_matches > hasta:
        next_page = item.page + 1
        itemlist.append(item.clone( title='>> Página siguiente', page = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def list_filmografias(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<tr class="row-.*?<img src="([^"]+)".*?alt="(.*?)".*?<a href="([^"]+)".*?</tr>')

    num_matches = len(matches)
    desde = item.page * perpage_list_film
    hasta = desde + perpage_list_film

    for thumb, title, url in matches[desde:hasta]:
        if not url or not title: continue

        url = url.replace('https://www.adf.ly/6680622/banner/', '')

        name = title.strip()

        try:
            year = title.split('(')[1]
            year = year.split(',')[0]

            if year:
                title = title.replace(year + ', ', '')

                name = title
                name = name.split('(')[0]
                name = name.strip()
        except:
            year = ''

        if not year: year = '-'

        itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = name, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if num_matches > hasta:
        next_page = item.page + 1
        itemlist.append(item.clone( title='>> Página siguiente', page = next_page, action = 'list_filmografias', text_color='coral' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'abcdefghijklmnopqrstuvwxyz#':
        itemlist.append(item.clone ( title = letra.upper(), url = host, action = 'list_alfa', filtro_search = letra ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    sort_alfa = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(host, use_cache = True).data

    matches = scrapertools.find_multiple_matches(data, '<li class="page_item page-item-.*?<a href="([^"]+)">(.*?)</a>')

    i = 0

    if matches: platformtools.dialog_notification('SigloXX', '[COLOR blue]Cargando películas[/COLOR]')

    for url, title in matches:
        if not url or not title: continue

        buscado = item.filtro_search.lower().strip()
        titulo = title.lower().strip()

        letra_titulo = titulo[0]
        if not letra_titulo == buscado:
            if not buscado == '#': continue
            if letra_titulo in '0123456789¡¿': pass
            else: continue

        i +=1

        desde = item.page * perpage_list_all
        hasta = desde + perpage_list_all

        if i >= desde and i <= hasta:
            thumb_data = httptools.downloadpage(url).data

            thumb = scrapertools.find_single_match(thumb_data, '<div class="entry-content">.*?background:.*?url(.*?) ')
            thumb = thumb.replace('(', '').replace(')', '')
        else: thumb = ''

        sort_alfa.append([url, title, thumb])

    if not i == 0:
        num_matches = i -1
        desde = item.page * perpage_list_all
        hasta = desde + perpage_list_all

        if num_matches < desde:
            hasta = desde
            desde = 0

        for url, title, thumb in sort_alfa[desde:hasta]:
            itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        tmdb.set_infoLabels(itemlist)

        if i > perpage_list_all:
            if num_matches > hasta:
                next_page = item.page + 1
                itemlist.append(item.clone( title = '>> Página siguiente', page = next_page, action = 'list_alfa', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, '<source src="(.*?)"')
    if not url:
       url = scrapertools.find_single_match(data, '<source type="video/mp4".*?src="(.*?)"')

    url = url.replace('https://www.adf.ly/6680622/banner/', '').replace('&amp;', '&')

    if url.startswith('https://ipfs.infura.io/'):
        headers = {'referer': host}
        url = httptools.downloadpage(url, headers = headers, only_headers = True, follow_redirects = False).headers.get('location')
        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', language = 'Esp', url = url ))
            return itemlist

    if url:
           servidor = servertools.get_server_from_url(url)
           if servidor and servidor != 'directo':
               url = servertools.normalize_url(servidor, url)

               itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = 'Esp', url = url ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def list_search(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article id="post-(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, 'rel="bookmark">(.*?)</a>')

        if not url or not title: continue

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title,
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

    return itemlist
