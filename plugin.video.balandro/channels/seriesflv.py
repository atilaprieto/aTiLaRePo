# -*- coding: utf-8 -*-

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, jsontools, servertools, tmdb


host = 'https://seriesf.lv/'

headers = {'Referer': host, 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'}

perpage = 20 # preferiblemente un múltiplo de los elementos que salen en la web (40) para que la subpaginación interna no se descompense

IDIOMAS = {'esp':'Esp', 'lat':'Lat', 'espsub':'VOSE', 'eng':'VO', 'engsub':'VOS'}


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Últimos episodios en castellano', action='last_episodes', lang='es' ))
    itemlist.append(item.clone( title='Últimos episodios en latino', action='last_episodes', lang='la' ))
    itemlist.append(item.clone( title='Últimos episodios en VOSE', action='last_episodes', lang='sub' ))
    itemlist.append(item.clone( title='Últimos episodios en VO', action='last_episodes', lang='en' ))

    itemlist.append(item.clone( title='Lista de series', action='list_all', url=host + 'series/' ))

    itemlist.append(item.clone( title='Por género', action = 'generos' ))
    itemlist.append(item.clone( title='Por letra (A - Z)', action='alfabetico' ))

    itemlist.append(item.clone( title='Buscar serie ...', action='search', search_type='tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        ('action','Acción'), 
        ('animation','Animación'), 
        ('anime','Anime'), 
        ('adventure','Aventura'), 
        ('comedy','Comedia'), 
        ('science-fiction','Ciencia Ficción'), 
        ('crime','Crimen'), 
        ('sport','Deporte'), 
        ('documentary','Documental'), 
        ('dorama','Dorama'), 
        ('drama','Drama'), 
        ('fantasy','Fantasía'), 
        ('children','Infantil'), 
        ('mistery','Misterio'), 
        ('news','Noticias'), 
        ('soap','Novelas'), 
        ('reality','Reality Show'), 
        ('talk-show','Talk Show'), 
        ('western','Western'), 
    ]
    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url=host + 'genero/' + opc, action='list_all' ))

    return itemlist

def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'abcdefghijklmnopqrstuvwxyz':
        itemlist.append(item.clone ( title = letra.upper(), url = host+'letra/'+letra+'/', action = 'list_all' ))

    return itemlist


# Una página devuelve todos los episodios (usar cache de una hora: 60x60=3600)
def last_episodes(item):
    logger.info()
    itemlist = []

    perpage = 10 # para que no tarde tanto por las múltiples llamadas a tmdb (serie / temporada / episodio)
    if not item.page: item.page = 0
    if not item.lang: item.lang = 'es'

    data = httptools.downloadpage(host, headers=headers, use_cache=True, cache_duration=3600).data

    matches = scrapertools.find_multiple_matches(data, '<a href="([^"]+)" class="item-one" lang="%s"(.*?)</a>' % item.lang)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for url, resto in matches[desde:hasta]:
        try:
            title = scrapertools.find_single_match(resto, '<div class="i-title">(.*?)</div>').strip()
            season, episode = scrapertools.find_single_match(url, '-(\d+)(?:x|X)(\d+)\.html')
        except:
            continue
        if not title or not season or not episode: continue
        
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, 
                                    contentType='episode', contentSerieName=title, contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    if num_matches > hasta: # subpaginación interna
        itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='last_episodes' ))

    return itemlist


# Desde listado por letra se devuelven todas las series en la misma página. Desde listado de series se devuelven 40 con paginaciones.
def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url, headers=headers).data

    matches = scrapertools.find_multiple_matches(data, '<div class="row form-group">(.*?)</div>\s*</div>\s*</div>')
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' title="([^"]+)').strip()
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')
        plot = scrapertools.find_single_match(article, '<div class="search-description">(.*?)$')

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                    contentType='tvshow', contentSerieName=title, 
                                    infoLabels={'year': '-', 'plot': scrapertools.htmlclean(plot)} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all' ))
            buscar_next = False

    if buscar_next:
        next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)">&raquo;</a></li>')
        if next_page:
           itemlist.append(item.clone (url = next_page, page = 0, title = '>> Página siguiente', action = 'list_all'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    bloque = scrapertools.find_single_match(data, 'Temporadas </span></div>(.*?)</div>')

    matches = scrapertools.find_multiple_matches(bloque, 'Temporada (\d+)')
    for numtempo in matches:
        itemlist.append(item.clone( action='episodios', title='Temporada %s' % numtempo, 
                                    contentType='season', contentSeason=numtempo ))
        
    tmdb.set_infoLabels(itemlist)

    return itemlist

# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)

def episodios(item):
    logger.info()
    itemlist = []
    color_lang = config.get_setting('list_languages_color', default='red')

    data = httptools.downloadpage(item.url, headers=headers).data

    if item.contentSeason or item.contentSeason == 0: # reducir datos a la temporada pedida
        data = scrapertools.find_single_match(data, '<i class="glyphicon glyphicon"></i> Temporada %s(.*?)</table>' % item.contentSeason)

    matches = scrapertools.find_multiple_matches(data, '<tr>(.*?)</tr>')
    for data_epi in matches:
        if '<th' in data_epi: continue
        try:
            url, title = scrapertools.find_single_match(data_epi, '<a href="([^"]+)"[^>]*>([^<]*)</a>')
            season, episode = scrapertools.find_single_match(url, '-(\d+)(?:x|X)(\d+)\.html')
        except:
            continue
        if not url or not season or not episode: continue
        if item.contentSeason and item.contentSeason != int(season): continue

        languages = ', '.join([IDIOMAS.get(lang, lang) for lang in scrapertools.find_multiple_matches(data_epi, 'images/([^\.]+)')])
        
        titulo = title.replace(item.contentSerieName, '').strip()
        if languages: titulo += ' [COLOR %s][%s][/COLOR]' % (color_lang, languages) # descartar por no ser del todo real por servidores inhabilitados !?

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, 
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def normalize_server(server):
    server = servertools.corregir_servidor(server)
    # Corregir servidores mal identificados en la web ya que apuntan a otros servidores:
    if server == 'flashx': server = 'cloudvideo'
    elif server == 'vidabc': server = 'clipwatching'
    elif server == 'streamin': server = 'gounlimited'
    elif server == 'streamcloud': server = 'upstream'
    elif server == 'datafile': server = 'vidia'
    elif server == 'salesfiles': server = 'mixdrop'
    elif server == 'streame': server = 'vshare'
    elif server == 'bigfile': server = 'vidlox'
    elif server == 'playedtome': server = '1fichier'
    elif server == 'thevideome': server = 'vevio'
    return server

def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    # ~ logger.debug(data)

    for tipo in ['Ver online', 'Descargas']:
        bloque = scrapertools.find_single_match(data, '%s</div>.*?<tbody>(.*?)</table>' % tipo)
        # ~ logger.debug(bloque)

        # ~ matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>') # en Descargas no hay </tr> !?
        matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?) class="linkComent"')
        for data_epi in matches:

            url = scrapertools.find_single_match(data_epi, ' href="([^"]+)')
            # ~ url = url.replace('/seriesflv/', host) # !?
            if url.startswith('/'): url = host + url[1:]

            server = scrapertools.find_single_match(data_epi, ' class="e_server"[^>]*><img [^>]*>([^<]+)')
            server = normalize_server(server)

            # ~ logger.info('%s %s' % (server, url))
            if not url or not server: continue

            lang = scrapertools.find_single_match(data_epi, 'images/([^\.]+)')
            
            itemlist.append(Item( channel = item.channel, action = 'play', server = server,
                                  title = '', url = url, 
                                  language = IDIOMAS.get(lang, lang) #, other = tipo
                           ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    url = httptools.downloadpage(item.url, headers=headers, follow_redirects=False, only_headers=True).headers.get('location', '')
    if url:
        itemlist.append(item.clone(url=url))

    return itemlist



def search(item, texto):
    logger.info("texto: %s" % texto)
    itemlist = []
    try:
        data = httptools.downloadpage(host+'a/search', post='q='+texto.replace(' ', '+'), headers=headers).data
        data = jsontools.load(data)
        for datos in data:
            itemlist.append(item.clone( title=datos['title'], url=datos['permalink'], thumbnail=datos['image'], action='temporadas', 
                                        contentType='tvshow', contentSerieName=datos['title'], 
                                        infoLabels={'year': datos['year'], 'imdb_id': datos['imdb_id']} ))
        tmdb.set_infoLabels(itemlist)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return itemlist
