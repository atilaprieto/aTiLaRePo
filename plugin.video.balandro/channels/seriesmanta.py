# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb


host = 'https://seriesmanta.in/'


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None, headers=None):
    # ~ data = httptools.downloadpage_proxy('seriesmanta', url, post=post, headers=headers).data
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Buscar intérprete ...', action = 'search', group = 'star', search_type = 'person', 
                                plot = 'Debe indicarse el nombre y apellido/s del intérprete.', text_color='plum'))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más recientes', action = 'list_all', url = host + 'ver-pelicula/', orden = 'release_dateDesc', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más antiguas', action = 'list_all', url = host + 'ver-pelicula/', orden = 'release_dateAsc', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ver-pelicula/', orden = 'mc_user_scoreDesc', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por alfabético (orden A -Z)', action = 'list_all', orden = 'titleAsc', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por alfabético (orden Z -A)', action = 'list_all', orden = 'titleDesc', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-serie', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más recientes', action = 'list_all', url = host + 'ver-serie', orden = 'release_dateDesc', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más antiguas', action = 'list_all', url = host + 'ver-serie', orden = 'release_dateAsc', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ver-serie', orden = 'mc_user_scoreDesc', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por alfabético (orden A -Z)', action = 'list_all', orden = 'titleAsc', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por alfabético (orden Z -A)', action = 'list_all', orden = 'titleDesc', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))


    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    opciones = [
        ('Acción', 'action'),
        ('Aventura', 'adventure'),
        ('Animación', 'animation'),
        ('Biografía', 'biography'),
        ('Comedia', 'comedy'),
        ('Crimen', 'crime'),
        ('Documentales', 'documentary'),
        ('Drama', 'drama'),
        ('Familia', 'family'),
        ('Fantasía', 'fantasy'),
        ('Historia', 'history'),
        ('Horror', 'horror'),
        ('Música', 'music'),
        ('Músical', 'musical'),
        ('Misterio', 'mystery'),
        ('Romance', 'romance'),
        ('Sci-Fi', 'sci-fi'),
        ('Thriller', 'thriller'),
        ('War', 'war'),
        ('Western', 'western')
        ]

    for tit, opc in opciones:
        itemlist.append(item.clone( title = tit, action = 'list_all', genero = opc ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    top_year = 1948 if item.search_type == 'tvshow' else 1901

    for x in range(current_year, top_year, -1):
        itemlist.append(item.clone( title = str(x), action = 'list_all', year = x ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(host)

    token = scrapertools.find_single_match(data, "token: '(.*?)'")

    tipo = 'movie' if item.search_type == 'movie' else 'series'

    if item.group == 'star':
        tipo = 'movie'

    if not item.page: item.page = 1

    query = 'titles/paginate?_token=%s&perPage=12&minRating=&maxRating=&availToStream=1&type=%s&order=%s&page=%s' % (token, tipo, item.orden, str(item.page))

    if item.genero: query += '&genres[]=' + item.genero
    if item.year:
        before_year = item.year + 1
        after_year = item.year - 1

        query += '&before=' + str(before_year) + '-1-1' '&after=' + str(after_year) + '-12-31'

    if item.star:
        query += '&cast=' + item.star

    url = host + query

    data = do_downloadpage(url)
    # ~ logger.debug(data)

    dict_data = jsontools.load(data)

    if 'items' not in dict_data: return itemlist

    for element in dict_data['items']:
        thumb = element['poster'] if element['poster'] else item.thumbnail
        thumb = thumb.replace('\\/', '/')

        title = element['title'].strip()
        if not title: continue

        new_item = item.clone( title = title, thumbnail = thumb, infoLabels = {'year':element['year'], 'plot': element['plot']})

        id = element['id']
        if not id: continue

        if element['type'] == 'movie':
            new_item.url = host + 'ver-pelicula/' + str(id) + '-' + title

            new_item.action = 'findvideos'
            new_item.contentType = 'movie'
            new_item.contentTitle = title
        else:
            new_item.url = host + 'ver-serie/' + str(id) + '-' + title

            new_item.action = 'temporadas'
            new_item.contentType = 'tvshow'
            new_item.contentSerieName = title

        itemlist.append(new_item)

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(itemlist) == 12:
           itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<div class="lista-temporadas">(.*?)</div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        numtempo = scrapertools.find_single_match(match, '>Temporada(.*?)</a>').strip()

        if not url or not numtempo: continue

        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.url = url
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li class="media">(.*?)</li>')

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        episode = scrapertools.find_single_match(match, '<a class="col-sm-3".*?/episodes/(.*?)">')

        if not url or not title or not episode: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        titulo = '%sx%s %s' % (str(item.contentSeason), episode, title)

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<tr class="part2" data-id=.*?' + "'(.*?)'.*?<img src='(.*?)'" + '.*?<td class="quality1">(.*?)</td>')

    for url, lang, qlty in matches:
        lang = lang.strip()
        if lang == '/la.png': lang = 'Lat'
        elif lang == '/es.png': lang = 'Esp'
        elif lang == '/en.png': lang = 'VO'
        elif lang == '/vos.png': lang = 'VOS'
        elif lang == '/sub.png': lang = 'Vose'

        servidor = servertools.get_server_from_url(url)
        if not servidor or servidor == 'directo': continue

        itemlist.append(Item(channel = item.channel, action = 'play', title = '', server = servidor, url = url, quality = qlty, language = lang )) 

    if not matches:
       matches = scrapertools.find_multiple_matches(data, '<tr class="part2" data-id=.*?' + "'(.*?)'")

       for url in matches:
           lang = '?'
           qlty = ''

           servidor = servertools.get_server_from_url(url)
           if not servidor or servidor == 'directo': continue

           itemlist.append(Item(channel = item.channel, action = 'play', title = '', server = servidor, url = url, quality = qlty, language = lang )) 
	
    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []
    try:
       if item.group == 'star':
           item.star = texto.replace(" ", "+")
           return list_all(item)

       item.url = host + 'busca-series-y-peliculas?q=' + texto.replace(" ", "+")
       return list_search(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item.search_type == 'movie':
       bloque = scrapertools.find_single_match(data, ' id="movies">(.*?)</div>')
    elif item.search_type == 'tvshow':
       bloque = scrapertools.find_single_match(data, ' id="series">(.*?)</div>')
    else:
       pelis = scrapertools.find_single_match(data, ' id="movies">(.*?)</div>')
       series = scrapertools.find_single_match(data, ' id="series">(.*?)</div>')
       bloque = pelis + series

    matches = scrapertools.find_multiple_matches(bloque, '<figure(.*?)</figure>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not title: continue

        tipo = 'tvshow' if '/ver-serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        if '/ver-serie/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))
        else:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist
