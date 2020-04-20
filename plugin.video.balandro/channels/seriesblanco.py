# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://seriesblanco.org/'

IDIOMAS = { 'es':'Esp', 'la':'Lat', 'sub':'VOSE' }


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None, headers=None):
    url = url.replace('seriesblanco.info', 'seriesblanco.org').replace('http://', 'https://') # por si viene de enlaces guardados
    data = httptools.downloadpage(url, post=post, headers=headers).data
    # ~ data = httptools.downloadpage_proxy('seriesblanco', url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Últimas 30 añadidas', action='list_all', url= host + 'ultimas-series-anadidas/' ))
    itemlist.append(item.clone( title='Lista por orden alfabético', action='list_all', url= host + 'lista-de-series/' ))

    itemlist.append(item.clone( title='Por género', action='generos' ))
    itemlist.append(item.clone( title='Por letra (A - Z)', action='alfabetico' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = do_downloadpage(host)

    matches = re.compile('<li><a href="([^"]+)"><i class="fa fa-bookmark-o"></i> ([^<]+)</a></li>', re.DOTALL).findall(data)
    for url, title in matches:
        if descartar_xxx and scrapertools.es_genero_xxx(title): continue
        itemlist.append(item.clone( title=title, url=url, action='list_all' ))

    return itemlist

def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        itemlist.append(item.clone( title=letra, url=host + 'lista-de-series/' + letra, action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<div style="float.*?<a href="([^"]+)">.*?src="([^"]+)".*?data-original-title="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, thumb, title in matches:
        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                    contentType='tvshow', contentSerieName=title ))

    if len(matches) == 0:
        patron = '<div style="float.*?<a href="([^"]+)">.*?src="([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        for url, thumb in matches:
            title = url.split('/')[-2].replace('-', ' ').capitalize()

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                        contentType='tvshow', contentSerieName=title ))

    tmdb.set_infoLabels(itemlist)

    # #Paginacion
    if len(itemlist) > 0:
        next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')
        if next_page == '':
            next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" ><i class="Next fa fa-chevron-right"')
        if next_page != '':
            itemlist.append(item.clone( title='Página siguiente >>', url=next_page, action='list_all' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<span itemprop="seasonNumber" class="fa fa-arrow-down">.*?Temporada (\d+)', re.DOTALL).findall(data)
    for numtempo in matches:
        itemlist.append(item.clone( action='episodios', title='Temporada %s' % numtempo, 
                                    contentType='season', contentSeason=numtempo ))
        
    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.contentSeason)


# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []
    color_lang = config.get_setting('list_languages_color', default='red')

    data = do_downloadpage(item.url)

    if item.contentSeason: # reducir datos a la temporada pedida
        data = scrapertools.find_single_match(data, '<div id="collapse%d"(.*?)</table>' % item.contentSeason)

    matches = re.compile('<tr class="table-hover">(.*?)</tr>', re.DOTALL).findall(data)
    for data_epi in matches:

        url = scrapertools.find_single_match(data_epi, ' href="([^"]+)')
        try:
            season, episode, title = scrapertools.find_single_match(data_epi, '<span itemprop="episodeNumber">(\d+)\s*(?:x|X)\s*(\d+)</span>([^<]*)</a>')
        except:
            continue

        languages = scrapertools.find_multiple_matches(data_epi, 'images/language/([^.]+)\.png')
        languages = list(dict.fromkeys(languages))
        
        titulo = '%sx%s %s [COLOR %s][%s][/COLOR]' % (season, episode, title, color_lang, ', '.join([IDIOMAS.get(lang, lang) for lang in languages]))

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, 
                                    contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace('HD-720p', '720p HD')
    orden = ['360p', '480p', 'HDTV', 'Micro-720p HD', '720p HD', '1080p HD']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<tr class="odd">(.*?)</tr>', re.DOTALL).findall(data)
    for data_link in matches:
        if ' data-tipo="descarga"' in data_link and 'Uptobox' not in data_link: continue # descartar descargas (menos uptobox)
        
        age = scrapertools.find_single_match(data_link, '<span>([^<]+)').strip()[:10]  # quitar hora
        lang = scrapertools.find_single_match(data_link, 'images/language/([^.]+)\.png')
        calidad = scrapertools.find_single_match(data_link, '<td>([^<]+)</td>\s*<td>\s*<button').strip()

        try:
            url, href = scrapertools.find_single_match(data_link, ' data-enlace="([^"]+)" href="([^"]+)')
        except:
            url = scrapertools.find_single_match(data_link, ' data-enlace="([^"]+)')
            href = item.url
        servidor = scrapertools.find_single_match(data_link, ' data-server="([^"]+)').replace('www.', '').lower()
        servidor = servidor.split('.', 1)[0]
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, url_referer = href,
                              title = '', 
                              language = IDIOMAS.get(lang, lang), quality = calidad, quality_num = puntuar_calidad(calidad), other = age
                       ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + "?s=" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
