# -*- coding: utf-8 -*-


from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'http://www.lacartoons.com/'


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = host + '/?Categoria_id=1' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'categorias', url = host ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron  = 'a href="(/serie[^"]+).*?'
    patron += 'src="([^"]+).*?'
    patron += 'nombre-serie">(.*?)</p>.*?class="marcador marcador-ano">(.*?)</span>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, year in matches:
        if item.filtro_search:
            buscado = item.filtro_search.lower().strip()
            titulo = title.lower().strip()

            if len(buscado) == 1:
                letra_titulo = titulo[0]
                if not letra_titulo == buscado:
                    if not buscado == '#': continue
                    if letra_titulo in '0123456789': pass
                    else: continue
            elif not buscado in titulo: continue

        if url.startswith('/'): url = host[:-1] + url

        if thumb.startswith('/'): thumb = host[:-1] + thumb

        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if '<ul class=" pagination">' in data:
        next_page = scrapertools.find_single_match(data, '(?is)next" href="([^"]+)"')

        if next_page:
            if next_page.startswith('/'): next_page = host[:-1] + next_page

            itemlist.append(item.clone (action = 'list_all', title = '>> Página siguiente', url = next_page, text_color='coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, 'botontes-categorias.*?</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'submit" value="([^"]+).*?value="([^"]+)')

    for title, id in matches:
        if id == '1': continue

        itemlist.append(item.clone( title = title, url = host + '?Categoria_id=' + id, action = 'list_all' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'abcdefghijklmnopqrstuvwxyz#':
        itemlist.append(item.clone ( title = letra.upper(), url = host + '?utf8=✓&Titulo=' + letra, action = 'list_all', filtro_search = letra ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '"fa fa-chevron-right"></span>(.*?)<')

    for season in matches:
        season = season.replace('Temporada', '').strip()

        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = season, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '"fa fa-chevron-right"></span> Temporada ' + str(item.contentSeason) + '(.*?)</div>')
    matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)".*?<span>(.*?)</span>(.*?)</a>')

    for url, capitulo, title in matches[item.page * perpage:]:
        if url.startswith('/'): url = host[:-1] + url

        epis = scrapertools.find_single_match(capitulo, 'Capitulo(.*?)-').strip()

        title = '%sx%s %s %s' % (str(item.contentSeason), epis, capitulo, title)
        title = title.replace('--', '').replace('-', '')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title,
                                    contentType='episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage:
            break

    if len(matches) > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title = ">> Página siguiente", action = "episodios", page = item.page + 1, text_color='coral' ))
    else:
        next_page = scrapertools.find_single_match(data, '(?is)next" href="([^"]+)"')

        if next_page:
            if next_page.startswith('/'): next_page = host[:-1] + next_page

            itemlist.append(item.clone (action = 'episodios', title = '>> Página siguiente', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron  = '<iframe src="([^"]+)'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url in matches:
        servidor = servertools.get_server_from_url(url)

        if servidor:
            url = normalize_other(url)
            if url:
               itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Lat' ))

    return itemlist


def normalize_other(url):
    url = servertools.corregir_servidor(url)

    if url == 'netutv': url = ''
    elif url == 'powvideo': url = ''
    elif url == 'streamplay': url = ''
    elif url == 'uploadedto': url = ''

    elif '/openload.' in url: url = ''
    elif '/oload.' in url: url = ''
    elif '/www.rapidvideo.' in url: url = ''
    elif '/streamango.' in url: url = ''
    elif '/streamcloud.' in url: url = ''
    elif '/thevid.' in url: url = ''
    elif '/thevideo.' in url: url = ''
    elif '/www.uploadmp4.' in url: url = ''

    return url


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?utf8=✓&Titulo=' + texto.replace(" ", "+") + '&button='
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
