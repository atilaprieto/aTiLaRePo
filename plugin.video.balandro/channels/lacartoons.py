# -*- coding: utf-8 -*-

from platformcode import logger
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

        thumb = host + thumb

        if not year: year = '-'

        itemlist.append(item.clone( action = 'episodios', url = host + url, title = title, thumbnail = thumb,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if '<ul class=" pagination">' in data:
        next_page = scrapertools.find_single_match(data, '(?is)next" href="([^"]+)"')

        if next_page:
            itemlist.append(item.clone (action = 'list_all', title = '>> Página siguiente', url = host + next_page, text_color='coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, 'botontes-categorias.*?</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'submit" value="([^"]+).*?value="([^"]+)')

    for title, id in matches:
        if id == '1': continue

        itemlist.append(item.clone( title = title, url = host + '/?Categoria_id=' + id, action = 'list_all' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'abcdefghijklmnopqrstuvwxyz#':
        itemlist.append(item.clone ( title = letra.upper(), url = host + '/?utf8=✓&Titulo=' + letra, action = 'list_all', filtro_search = letra ))

    return itemlist


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.temporada: item.temporada = 1

    if not item.last_epi: item.last_epi = 1

    temporada = item.temporada
    last_epi = item.last_epi

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'listas-de-episodion.*?href="([^"]+).*?span>(.*?)</a>.*?')

    for url, title in matches:
        title = title.replace('</span>', '')

        capitulo = scrapertools.find_single_match(title, 'Capitulo(.*?)-').strip()
        if not capitulo: capitulo = '1'

        num_epi = capitulo
        if len(num_epi) == 1: num_epi = '0' + num_epi

        if num_epi < last_epi:
            temporada += 1
            last_epi = 1
        else: last_epi = num_epi

        titulo = title.replace(capitulo, '').replace('Capitulo', '').replace('-', '').strip()

        title = '%sx%s %s' % (temporada, capitulo, titulo)

        itemlist.append(item.clone( action = 'findvideos', url = host + url, title = title,
                                    contentType='episode', contentSeason = temporada, contentEpisodeNumber = num_epi ))

    next_page = scrapertools.find_single_match(data, '(?is)next" href="([^"]+)"')

    if next_page:
        itemlist.append(item.clone (action = 'episodios', title = '>> Página siguiente', url = host + next_page,
                                    temporada = temporada, last_epi = last_epi, text_color='coral' ))

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
        item.url = host + '/?utf8=✓&Titulo=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
