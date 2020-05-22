# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://seriemega.net/'

def do_downloadpage(url, post=None):
    url = url.replace('seriemega.com', 'seriemega.net') # por si viene de enlaces guardados
    data = httptools.downloadpage(url, post=post).data
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

    itemlist.append(item.clone ( title = 'Últimas películas', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Últimas series', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        ('accion','Acción'), 
        ('action-adventure','Action & Adventure'),
        ('animacion','Animación'), 
        ('aventura','Aventura'),
        ('belica','Belica'), 
        ('ciencia-ficcion','Ciencia ficción'), 
        ('comedia','Comedia'), 
        ('crimen','Crimen'), 
        ('documental','Documental'), 
        ('drama','Drama'), 
        ('familia','Familiar'), 
        ('fantasia','Fantasía'), 
        ('historia','Historia'), 
        ('kids','Infantil'), 
        ('misterio','Misterio'), 
        ('musica','Música'), 
        ('pelicula-de-tv','Película de TV'), 
        ('reality','Reality'), 
        ('romance','Romance'), 
        ('sci-fi-fantasy','Sci-Fi & Fantasy'), 
        ('suspense','Suspense'), 
        ('terror','Terror'),
        ('western','Western'), 
    ]
    if item.search_type == 'movie': 
        opciones.remove(('action-adventure','Action & Adventure'))
        opciones.remove(('kids','Infantil'))
        opciones.remove(('reality','Reality'))
        opciones.remove(('sci-fi-fantasy','Sci-Fi & Fantasy'))
    elif item.search_type == 'tvshow': 
        opciones.remove(('suspense','Suspense'))

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url=host + 'categoria/' + opc + '/', action='list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h3 class="Title">(.*?)</h3>')
        if not url or not title or '/pagina-ejemplo/' in url: continue
        thumb = scrapertools.find_single_match(article, ' data-lazy-src="([^"]+)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src="([^"]+)"') # search
        year = scrapertools.find_single_match(article, '<span class="Year">(\d+)</span>')
        if not year: year = '-'

        tipo = 'tvshow' if 'TV</span>' in article else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)')
            
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')
    if next_page:
       itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    
    matches = re.compile(' data-tab="(\d+)"', re.DOTALL).findall(data)
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

    data = do_downloadpage(item.url)

    if item.contentSeason: # reducir datos a la temporada pedida
        data = scrapertools.find_single_match(data, ' data-tab="%s"(.*?)</table>' % item.contentSeason)

    matches = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(data)
    for data_epi in matches:
        # ~ logger.debug(data_epi)
        try:
            url, title = scrapertools.find_single_match(data_epi, '<a href="([^"]+)">([^<]*)</a>')
            season, episode = scrapertools.find_single_match(re.sub('-hd-\d+/$', '/', url), '-(\d+)(?:x|X)(\d+)/$')
        except:
            continue
        if not url or not season or not episode: continue
        if item.contentSeason and item.contentSeason != int(season): continue

        thumb = scrapertools.find_single_match(data_epi.replace('&quot;','"'), ' src="([^"]+)')
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist



# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'tsscreener', 'brscreener', 'dvdrip', 'hdrip', 'hd720', 'hd720p', 'hd1080', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def normalize_server(server):
    if '.' in server: server = server.split('.')[0]
    server = servertools.corregir_servidor(server)
    if server == 'embed': server = 'mystream'
    elif 'opción' in server: server = ''
    elif server.startswith('online'): server = ''
    return server

def findvideos(item):
    logger.info()
    itemlist = []
    
    IDIOMAS = {'español': 'Esp', 'castellano': 'Esp','latino': 'Lat', 'subespañol': 'VOSE', 'subtitulado': 'VOSE', 'sub': 'VO'}

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    # Enlaces en embeds
    trid_trtype = scrapertools.find_single_match(data, '(trid=[^"]+)')
    if trid_trtype:
        patron = ' data-tplayernv="([^"]+)"><span>(.*?)</span><span>(.*?)</span></li>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        for opt, server, lang_qlty in matches:
            trembed = scrapertools.find_single_match(data, 'id="%s".*?trembed=([^&"]+)' % opt)
            if not trembed: continue
            url = host + '?trembed=' + trembed + '&' + trid_trtype
            l_q = scrapertools.find_single_match(lang_qlty, '(.*?)-(.*?)$')
            if l_q:
                lang = l_q[0].strip().lower()
                qlty = l_q[1].strip()
                othr = ''
            else:
                lang = ''
                qlty = ''
                othr = lang_qlty
            server = normalize_server(server)
            if server == 'mega': continue # van a través de un acortador con recaptcha

            itemlist.append(Item( channel = item.channel, action = 'play', server = server, referer = item.url,
                                  title = '', url = url, 
                                  language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty), other = othr
                           ))

    # Enlaces en descargas
    if '<div class="TPTblCn">' in data:
        bloque = scrapertools.find_single_match(data, '<div class="TPTblCn">(.*?)</table>')
        bloque = scrapertools.decodeHtmlentities(bloque)
        matches = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(bloque)
        for lin in matches:
            if '<th' in lin: continue
            url = scrapertools.find_single_match(lin, ' href="([^"]+)')
            server = scrapertools.find_single_match(lin, ' alt="Descargar ([^"]+)').strip().lower()
            lang = scrapertools.find_single_match(lin, ' alt="Imagen ([^"]+)').strip().lower()
            qlty = scrapertools.find_multiple_matches(lin, '<span>(.*?)</span>')[-1].strip()
            if not url or not server: continue
            server = normalize_server(server)
            if server == 'mega': continue # van a través de un acortador con recaptcha
            
            itemlist.append(Item( channel = item.channel, action = 'play', server = normalize_server(server), referer = item.url,
                                  title = '', url = url, 
                                  language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = puntuar_calidad(qlty) #, other = 'download'
                           ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []
    
    item.url = item.url.replace('&#038;', '&')
    if 'trdownload=' in item.url:
        url = httptools.downloadpage(item.url, headers={'Referer': item.referer}, follow_redirects=False, only_headers=True).headers.get('location', '')
    else:
        data = httptools.downloadpage(item.url, headers={'Referer': item.referer}).data
        # ~ logger.debug(data)
        url = scrapertools.find_single_match(data, '<iframe.*? src="([^"]+)')

    if url:
        if url.startswith('//'): url = 'https:' + url
        url = url.replace('https://uptostream/', 'https://uptostream.com/') # corregir url errónea en algunos links
        url = url.replace('https://www.seriemega.site/', 'https://www.fembed.com/')

    if url:
        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        # ~ url_extra = '&tr_post_type=2' if item.search_type == 'tvshow' else '&tr_post_type=1' if item.search_type == 'movie' else ''
        item.url = host + '?s=' + texto.replace(" ", "+") #+ url_extra
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
