# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools, jsontools

host = 'https://repelis.io/'

perpage = 20


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Últimas actualizadas', action = 'list_all', url = host + 'explorar/' ))

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'peliculas-castellano/', grupo = 'lang', grupo_det='es-es' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'peliculas-latino/', grupo = 'lang', grupo_det='es-mx' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'peliculas-subtituladas/', grupo = 'lang', grupo_det='en' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data, '<a href="(/genero/[^"]+)">([^<]+)</a>')

    for url, title in matches:
        if url.startswith('/'): url = host + url[1:]

        genre_id = scrapertools.find_single_match(url, '-([^-]+)$')

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, grupo = 'genr', grupo_det = genre_id ))

    return sorted(itemlist, key = lambda it: it.title)

def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1940, -1):
        anyo = str(x)
        itemlist.append(item.clone( action = 'list_all', title = anyo, url = host + 'estrenos', grupo = 'anys', grupo_det = anyo ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 1
    v_offset = (item.page - 1) * perpage

    post = {}
    if item.grupo == 'anys': # order: releaseDate
        post["query"] = "query ($first: Int!, $offset: Int!) {movies2019: allMovies (filter: {releaseYear: "+item.grupo_det+"}, order: {releaseDate: \"DESC\"}, first: $first, offset: $offset) {id slug title rating releaseDate released poster nowPlaying}}"
        post["variables"] = {"first": perpage, "offset": v_offset}

    elif item.grupo == 'lang': # order: creation
        post["query"] = "query ($first: Int!, $offset: Int!) {movies: allMovies (filter: {mirror: \""+item.grupo_det+":*\"}, order: {creation: \"DESC\"}, first: $first, offset: $offset) {id slug title rating releaseDate released poster nowPlaying}}"
        post["variables"] = {"first": perpage, "offset": v_offset}

    elif item.grupo == 'genr': # order: rating
        post["query"] = "query ($genreId: ID!, $first: Int!, $offset: Int!) {genre: Genre (id: $genreId) {id slug name} movies: allMovies (filter: {genres: [$genreId]}, order: {rating: \"DESC\"}, first: $first, offset: $offset) {...MovieFields}} fragment MovieFields on Movie {id slug title rating releaseDate released poster nowPlaying}"
        post["variables"] = {"genreId": item.grupo_det, "first": perpage, "offset": v_offset}

    else: # order: creation
        post["query"] = "query ($first: Int!, $offset: Int!) {movies: allMovies (order: {creation: \"DESC\"}, first: $first, offset: $offset) {id slug title rating releaseDate released poster nowPlaying}}"
        post["variables"] = {"first": perpage, "offset": v_offset}

    post = jsontools.dump(post)

    headers = {'referer': item.url + '?page=' + str(item.page), 'Content-Type': 'application/json'}

    data = httptools.downloadpage(host + 'graph', post = post, headers = headers).data
    # ~ logger.debug(data)

    try:
        matches = jsontools.load(data)
        # ~ logger.debug(matches)
        
        key = 'movies2019' if item.grupo == 'anys' else 'movies'

        for movie in matches['data'][key]:
            if not movie['title'] or not movie['slug'] or not movie['id']: continue
            # ~ logger.debug(movie)

            title = movie['title']
            url = host + 'pelicula/%s-%s' % (movie['slug'], movie['id'])
            thumb = host + '_images/posters/%s/180x270.jpg' % (movie['poster'])
            year = movie['releaseDate'][:4] #.split('-')[0]

            itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb, 
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        tmdb.set_infoLabels(itemlist)

        if len(itemlist) > 1:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_all' ))
    except:
        pass

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    orden = ['Low', 'Good', 'High']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

# Si hay excepciones concretas de este canal, añadir aquí, si son genéricas añadir en servertools.corregir_servidor
def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'myv': return 'myvi'
    return servidor

def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es-es': 'Esp', 'es-mx': 'Lat', 'en': 'VOSE'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    try:
        servidores = jsontools.load(scrapertools.find_single_match(data, 'window\.__NUXT__=(.*?);</script>'))

        for server in servidores['data'][0]['movie']['mirrors']:
            # ~ logger.debug(server)
            servidor = server['hostname'].split('.')[0] if '.' in server['hostname'] else server['hostname']
            servidor = corregir_servidor(servidor)
            url = host[:-1] + server['url']
            lang = IDIOMAS.get(server['audio'])
            qlty = server['quality'].capitalize()

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                  language = lang, quality = qlty, quality_num = puntuar_calidad(qlty) ))
    except:
        pass

    if 'allow="autoplay"' in data:
       url = scrapertools.find_single_match(data, '</div>\s*<iframe src="([^"]+)"').replace('&amp;', '&')
       if url != 'about:blank':
           servidor = servertools.get_server_from_url(url)
           if servidor != 'directo':
               itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&amp;', '&')

    if url.startswith(host):
        url = httptools.downloadpage(url, follow_redirects = False, only_headers = True).headers.get('location', '')

    if url:
        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist



def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + 'graph'
        item.qry = texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def list_search(item):
    logger.info()
    itemlist = []

    post = '{"query": "query ($term: String) {movies: allMovies (search: $term) {id slug title releaseDate poster}}", "variables": {"term": "%s"}}' % item.qry

    headers = {'Content-Type': 'application/json'}

    data = httptools.downloadpage(item.url, post = post, headers = headers).data
    # ~ logger.debug(data)

    try:
        matches = jsontools.load(data)
        # ~ logger.debug(matches)

        for movie in matches['data']['movies']:
            if not movie['title'] or not movie['slug'] or not movie['id']: continue

            title = movie['title']
            url = host + 'pelicula/%s-%s' % (movie['slug'], movie['id'])
            thumb = host + '_images/posters/%s/180x270.jpg' % (movie['poster'])
            year = movie['releaseDate'].split('-')[0]

            itemlist.append(item.clone( action = 'findvideos', title = title, url = url, thumbnail = thumb, 
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

            tmdb.set_infoLabels(itemlist)
    except:
        pass

    return itemlist
