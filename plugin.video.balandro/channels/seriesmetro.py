# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

host = 'https://seriesmetro.com/'


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title='Todas las series', action ='list_all', url = host + 'series' ))

    itemlist.append(item.clone ( title='Por orden alfabético', action = 'alfabetico' ))

    itemlist.append(item.clone ( title='Por género', action = 'generos' ))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        ('genero-accion','Acción'), 
        ('accion','Acción (bis)'), 
        ('action-adventure','Action & Adventure'), 
        ('aventura','Aventura'), 
        ('animacion','Animación'), 
        ('genero-animes','Anime'), 
        ('genero-ciencia-ficcion','Ciencia ficción'), 
        ('ciencia-ficcion','Ciencia ficción (bis)'), 
        ('comedia','Comedia'), 
        ('genero-comedia','Comedia (bis)'), 
        ('crimen','Crimen'), 
        ('genero-dibujos','Dibujos'), 
        ('documental','Documental'), 
        ('genero-documental','Documental (bis)'), 
        ('genero-drama','Drama'), 
        ('drama','Drama (bis)'), 
        ('familia','Familia'), 
        ('fantasia','Fantasía'), 
        ('genero-fantastico','Fantástico'), 
        ('kids','Kids'), 
        ('misterio','Misterio'), 
        ('musica','Música'), 
        ('reality','Reality'), 
        ('genero-romance','Romance'), 
        ('romance','Romance (bis)'), 
        ('sci-fi-fantasy','Sci-Fi & Fantasy'), 
        ('talk','Talk'), 
        ('genero-telenovela','Telenovela'), 
        ('genero-thriller','Thriller'), 
        ('terror','Terror'), 
        ('war-politics','War & Politics'), 
        ('western','Western'), 
    ]
    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url=host + 'ver/' + opc + '/', action='list_all' ))

    return itemlist

def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        itemlist.append(item.clone ( title = letra, url = host + 'ver/letter/%s/' % (letra.replace('#', '0-9')), action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    if '</main>' in data: data = data.split('</main>')[0]
    elif '<aside class="sidebar"' in data: data = data.split('<aside class="sidebar"')[0]

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)" class="lnk-blk"')
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>')
        if not url or not title: continue
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + url
        year = scrapertools.find_single_match(article, '<span class="date">(\d+)</span>')
        if not year: year = '-'
        plot = scrapertools.find_single_match(article, '<p><p>(.*?)</p>')

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                    contentType='tvshow', contentSerieName=title, 
                                    infoLabels={'year': year, 'plot': scrapertools.htmlclean(plot)} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><i class="fa-arrow-right">')
    if next_page:
       itemlist.append(item.clone (url = next_page, title = '>> Página siguiente', action = 'list_all'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    dobject = scrapertools.find_single_match(data, 'data-object\s*=\s*"([^"]+)')
    if not dobject: return itemlist

    matches = scrapertools.find_multiple_matches(data, '<li class="sel-temp"><a data-post="([^"]+)" data-season="([^"]+)')
    for dpost, tempo in matches:
        itemlist.append(item.clone( action='episodios', title='Temporada ' + tempo, dobject=dobject, dpost=dpost,
                                    contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist

#TODO!? limitar episodios a mostrar y no hacer paginación automàtica (menos añadiendo a videoteca) !? Ej: El señor de los cielos (74 episodios temp 1)
def episodios(item): 
    logger.info()
    itemlist = []

    if not item.dobject or not item.dpost or not item.contentSeason: return itemlist

    post = {'action': 'action_select_season', 'post': item.dpost, 'object': item.dobject, 'season': item.contentSeason}
    data = httptools.downloadpage(host + 'wp-admin/admin-ajax.php', post=post).data
    # ~ logger.debug(data)

    # ~ while True:
    for i in range(10):
        matches = scrapertools.find_multiple_matches(data, '<li><a href="([^"]+)"[^>]*>([^<]+)')
        for url, title in matches:
            s_e = scrapertools.find_single_match(title, '(\d+)(?:x|X)(\d+)')
            if not s_e: continue
            season = int(s_e[0])
            episode = int(s_e[1])

            itemlist.append(item.clone( action='findvideos', url=url, title=title, 
                                        contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

        next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="[^"]*page/(\d+)/')
        if next_page:
            post = {'action': 'action_pagination_ep', 'object': item.dobject, 'season': item.contentSeason, 'page': next_page}
            data = httptools.downloadpage(host + 'wp-admin/admin-ajax.php', post=post).data
            # ~ logger.debug(data)
        else:
            break

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Español Latino':'Lat', 'Latino':'Lat', 'Español Castellano':'Esp', 'Español':'Esp', 'Sub Latino':'VOSE', 'Sub Español':'VOSE', 'Sub':'VOSE', 'Ingles':'VO'}

    data = httptools.downloadpage(item.url).data
    # ~ logger.debug(data)

    dterm = scrapertools.find_single_match(data, ' data-term="([^"]+)')
    if not dterm: return itemlist

    matches = scrapertools.find_multiple_matches(data, '<a data-opt="([^"]+)".*?<span class="option">(?:Cload|CinemaUpload) - ([^<]*)')
    for dopt, lang in matches:
        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo',
                              title = '', dterm = dterm, dopt = dopt, url = item.url, 
                              language = IDIOMAS.get(lang, lang) #, other = dopt
                       ))

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    post = {'action': 'action_player_series', 'term_id': item.dterm, 'ide': item.dopt}
    data = httptools.downloadpage(host + 'wp-admin/admin-ajax.php', post=post, raise_weberror=False).data
    # ~ logger.debug(data)

    url = scrapertools.find_single_match(data, '<iframe[^>]* src="([^"]+)')
    if not url: return itemlist
    url = url.replace('&#038;', '&')

    data = httptools.downloadpage(url, headers={'Referer': item.url}, raise_weberror=False).data
    # ~ logger.debug(data)

    url = scrapertools.find_single_match(data, '<iframe[^>]* src="([^"]+)')
    if not url: return itemlist

    if 'embed.cload' in url:
        data = httptools.downloadpage(url, headers={'Referer': host}, raise_weberror=False).data
        # ~ logger.debug(data)
        if '<div class="g-recaptcha"' in data or 'Solo los humanos pueden ver' in data:
            headers = {'Referer': host, 'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)'}
            data = httptools.downloadpage(item.url, headers=headers, raise_weberror=False).data
            # ~ logger.debug(data)
            new_url = scrapertools.find_single_match(data, '<div id="option-players".*?src="([^"]+)"')
            if new_url:
                new_url = new_url.replace('/cinemaupload.com/', '/embed.cload.video/')
                data = httptools.downloadpage(new_url, raise_weberror=False).data
                # ~ logger.debug(data)

        url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
        if url:
            if '/manifest.mpd' in url:
                if platformtools.is_mpd_enabled():
                    itemlist.append(['mpd', url, 0, '', True])
                itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
            else:
                itemlist.append(['m3u8', url])

    else:
        if 'dailymotion' in url: url = 'https://www.dailymotion.com/' + url.split('/')[-1]

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
