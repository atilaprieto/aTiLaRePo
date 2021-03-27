﻿# -*- coding: utf-8 -*-

import base64

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

host = 'https://www.pelispedia.de/'


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

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        ('Acción', 'accion'),
        ('Action & Adventure', 'action-adventure'),
        ('Animación', 'animacion'),
        ('Aventura', 'aventura'),
        ('Bélica', 'belica'),
        ('Ciencia ficción', 'ciencia-ficcion'),
        ('Comedia', 'comedia'),
        ('Crimen', 'crimen'),
        ('Documental', 'documental'),
        ('Drama', 'drama'),
        ('Familia', 'familia'),
        ('Fantasía', 'fantasia'),
        ('Halloween', 'halloween'),
        ('Historia', 'historia'),
        ('Kids', 'kids'),
        ('Misterio', 'misterio'),
        ('Música', 'musica'),
        ('Película de TV', 'pelicula-de-tv'),
        ('Reality', 'reality'),
        ('Romance', 'romance'),
        ('Sci-Fi & Fantasy', 'sci-fi-fantasy'),
        ('Suspense', 'suspense'),
        ('Terror', 'terror'),
        ('War & Politics', 'war-politics'),
        ('Western', 'western')
        ]

    for tit, opc in opciones:
        if item.search_type == 'movie':
           if tit == 'Kids': continue
           elif tit == 'Reality': continue
           elif tit == 'Sci-Fi & Fantasy': continue
           elif tit == 'War & Politics': continue
        else:
           if tit == 'Aventura': continue
           elif tit == 'Bélica': continue
           elif tit == 'Ciencia ficción': continue
           elif tit == 'Familia': continue
           elif tit == 'Fantasía': continue
           elif tit == 'Halloween': continue
           elif tit == 'Historia': continue
           elif tit == 'Música': continue
           elif tit == 'Película de TV': continue
           elif tit == 'Romance': continue
           elif tit == 'Suspense': continue
           elif tit == 'Terror': continue
           elif tit == 'Western': continue

        itemlist.append(item.clone( title = tit, url = host + opc + '/', action='list_all' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1949, -1):
        itemlist.append(item.clone( title=str(x), url= host + 'release/' + str(x) + '/', action='list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, raise_weberror=False).data
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        if not url: url = scrapertools.find_single_match(article, ' href=([^ >]+)')

        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(article, '<h4>(.*?)</h4>')
        if not title: title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=([^ >]+)')

        year = scrapertools.find_single_match(article, '<span class="year">(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(article, ' (\d{4})</span>')
        if not year and '/release/' in item.url: year = scrapertools.find_single_match(item.url, '/release/(\d{4})')
        if not year: year = '-'

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if item.search_type not in ['all', tipo]: continue
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type == 'tvshow': continue

            qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if '<nav class="pagination mat2 tac">' in data:
        bloque = scrapertools.find_single_match(data, '<nav class="pagination mat2 tac">(.*?)</nav>')

        prev_page = ''
        if 'Anterior' in bloque: prev_page = 'Anterior.*?'
        next_page = scrapertools.find_single_match(bloque, prev_page + '<a href="(.*?)"')

        if '/page/' in next_page:
            itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'click="tab = ' + "'season-(.*?)'" + '">T(.*?)</button>')
    for nro_temp, tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.url = item.url
            item.nrotemp = nro_temp
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = item.url, nrotemp = nro_temp, 
                                    contentType = 'season', contentSeason = tempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
# ~ def tracking_all_episodes(item):
    # ~ return episodios(item)

def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    tempo = scrapertools.find_single_match(data, 'x-show="tab === ' + "'season-" + str(item.nrotemp) + '(.*?)</div>')

    matches = scrapertools.find_multiple_matches(tempo, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="([^"]+)')

        season = scrapertools.find_single_match(match, 'class="pdx brd1 dib vat black-bg mar yellow-co">(.*?) -').strip()
        episode = scrapertools.find_single_match(match, 'class="pdx brd1 dib vat black-bg mar yellow-co">.*? - (.*?)</span>').strip()

        if not url or not season or not episode: continue

        thumb = scrapertools.find_single_match(match, ' data-src="([^"]+)')
        title = scrapertools.find_single_match(match, '<h2 class="ttl tvw fz4 mab">(.*?)</h2>')
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title = ">> Página siguiente", action = "episodios", page = item.page + 1, text_color='coral' ))

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()
    orden = ['cam', 'tsscreener', 'brscreener', 'sd240p', 'sd480p', 'dvdrip', 'hd', 'hdrip', 'hd720p', 'hd1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def corregir_servidor(servidor):
    # ~ 'streams3' no se ha conseguido
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'fcom': return 'fembed'
    elif servidor in ['mp4', 'api', 'drive']: return 'gvideo'
    elif servidor == 'streamcrypt': return ''
    elif servidor in ['stream', 'stream-mx', 'stream mx', 'streammx', 'mx server']: return 'directo'
    else: return servidor

def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es': 'Esp',
       'mx': 'Lat',
       'en': 'Vose',
       'spanish': 'Esp',
       'español': 'Esp',
       'latino': 'Lat',
       'subtitulado': 'Vose',
       'inglés': 'VO',
       'ingles': 'VO'
       }

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, '<div class="op-srv brd1"(.*?)</div>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' data-url="(.*?)"')
        if not url: url = scrapertools.find_single_match(match, ' data-src="(.*?)"')
        if not url: continue

        server = scrapertools.find_single_match(match, '<span class="ttu db tvw white-co">(.*?)</span>').lower()
        if not server: continue

        server = corregir_servidor(server)

        modif = scrapertools.find_single_match(match, '<span class="ttu db tvw fz2">(.*?)</span>')
        modif = modif.replace(' | ', ' - ')

        lang = scrapertools.find_single_match(modif, '(.*?) -').lower().strip()
        qlty = scrapertools.find_single_match(modif, '- (.*?)$').strip()

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, referer = item.url, title = '', url = url, 
                              language = IDIOMAS.get(lang, lang), quality = qlty ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if not '//' in url:
        url_b64 = base64.b64decode(url)
        url_b64 = url_b64.replace('&#038;', '&').replace('&amp;', '&')

        data = httptools.downloadpage(url_b64, raise_weberror = False).data
        # ~ logger.debug(data)

        new_url = scrapertools.find_single_match(data, '<h1 class.*?<a href="(.*?)"')
        if not new_url: new_url = scrapertools.find_single_match(data, ' src="(.*?)"')
        if not new_url: new_url = scrapertools.find_single_match(data, ' SRC="(.*?)"')

        if new_url:
            new_url = new_url.replace('&#038;', '&').replace('&amp;', '&')

            if 'stream-mx.com/' in new_url:
                fid = scrapertools.find_single_match(new_url, "id=([^&]+)")
                if not fid: return itemlist

                url = 'https://stream-mx.com/player.php?id=%s&v=2&ver=si' % fid
                data = httptools.downloadpage(url, headers={'Referer': new_url}).data
                # ~ logger.debug(data)

                bloque = scrapertools.find_single_match(data, '"sources":\s*\[(.*?)\]')
                for enlace in scrapertools.find_multiple_matches(bloque, "\{(.*?)\}"):
                    v_url = scrapertools.find_single_match(enlace, '"file":\s*"([^"]+)')
                    if not v_url: continue

                    v_type = scrapertools.find_single_match(enlace, '"type":\s*"([^"]+)')
                    if v_type == 'hls':
                       itemlist.append(item.clone(url = v_url, server = 'm3u8hls'))
                    else:
                      v_lbl = scrapertools.find_single_match(enlace, '"label":\s*"([^"]+)')
                      itemlist.append([v_lbl, v_url])

                return itemlist
				
            servidor = servertools.get_server_from_url(new_url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor:
               itemlist.append(item.clone(server = servidor, url = new_url))
            else:
               itemlist.append(item.clone(server = '', url = new_url))

        return itemlist

    if '/o.php?l=' in item.url:
        url = scrapertools.find_single_match(item.url, "/o\.php\?l=(.*)")
        for i in range(9): # range(5)
            url = base64.b64decode(url)
            if url.startswith('http'): break

        if not url.startswith('http'): url = None
    else:
        item.url = item.url.replace('&#038;', '&').replace('&amp;', '&')
        resp = httptools.downloadpage(item.url, headers={'Referer': item.referer}, follow_redirects=False)
        if 'location' in resp.headers: 
            url = resp.headers['location']
        else:
            # ~ logger.debug(resp.data)
            url = scrapertools.find_single_match(resp.data, "src='([^']+)")
            if not url: url = scrapertools.find_single_match(resp.data, 'src="([^"]+)')
            if not url: url = scrapertools.find_single_match(resp.data, 'src=([^ >]+)')
            if not url: url = scrapertools.find_single_match(resp.data, '"embed_url":"([^"]+)')

    if url:
        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
