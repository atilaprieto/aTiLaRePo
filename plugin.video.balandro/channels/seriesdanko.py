# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


# ~ HOST = 'http://seriesdanko.to/'
HOST = 'https://seriesdanko.net/'
IDIOMAS = {'es': 'Esp', 'la': 'Lat', 'sub': 'VOSE'}


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + HOST + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, HOST)

def do_downloadpage(url, post=None):
    url = url.replace('seriesdanko.to', 'seriesdanko.net').replace('http://', 'https://') # por si viene de enlaces guardados
    data = httptools.downloadpage(url, post=post).data
    # ~ data = httptools.downloadpage_proxy('seriesdanko', url, post=post).data
    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Nuevos capítulos', action='novedades' ))

    itemlist.append(item.clone( title='Listado alfabético', action='listado_alfabetico' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    # ~ itemlist.append(item_configurar_proxies(item))
    return itemlist


def novedades(item):
    logger.info()
    itemlist = []

    if item.page == '': item.page = 0
    perpage = 11

    data = do_downloadpage(HOST)
    # ~ logger.debug(data)
    
    matches = re.findall('<article class="article mt-20">(.*?)</article>', data, re.DOTALL)

    for serie_data in matches[item.page * perpage:]:
        # ~ logger.debug(serie_data)

        url = scrapertools.find_single_match(serie_data, ' href="([^"]+)')
        if not url: continue

        spans = scrapertools.find_single_match(serie_data, '<span>(.*?)</span><span>(.*?)</span>')
        if not spans: continue
        titulo = spans[0] + ' - ' + spans[1]
        show = spans[0]
        s_e = scrapertools.find_single_match(spans[1], '(\d+)(?:x|X|-)(\d+)')
        if not s_e: continue
        season = int(s_e[0])
        episode = int(s_e[1])

        imgs = scrapertools.find_multiple_matches(serie_data, ' src="([^"]+)')
        if not imgs: img = ''
        else: img = imgs[-1]
        
        # Menú contextual: ofrecer acceso a temporada / serie
        context = []
        url_serie = scrapertools.find_single_match(serie_data, '<i class="icon-421"></i> <a href="([^"]+)"')
        if url_serie:
            context.append({ 'title': '[COLOR pink]Listar temporada %s[/COLOR]' % season, 
                             'action': 'episodios', 'url': url_serie, 'context': '', 'folder': True, 'link_mode': 'update' })
            context.append({ 'title': '[COLOR pink]Listar temporadas[/COLOR]',
                             'action': 'temporadas', 'url': url_serie, 'context': '', 'folder': True, 'link_mode': 'update' })

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=img, context=context, 
                                    contentType = 'episode', contentSerieName = show, contentSeason=season, contentEpisodeNumber=episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", page=item.page + 1 ))

    return itemlist


def listado_alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '0ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        itemlist.append(item.clone( action='series_por_letra', title='0-9' if letra == '0' else letra, url=HOST + 'lista-de-series/' + letra ))

    return itemlist

def series_por_letra(item):
    logger.info()
    itemlist = []

    if item.page == '': item.page = 0
    perpage = 15

    data = do_downloadpage(item.url)

    matches = re.findall('<article (.*?)</article>', data, re.DOTALL)

    for serie_data in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(serie_data, ' href="([^"]+)')
        if not url: continue

        title = scrapertools.find_single_match(serie_data, ' title="([^"]+)')
        if not title: continue

        imgs = scrapertools.find_multiple_matches(serie_data, ' src="([^"]+)')
        if not imgs: img = ''
        else: img = imgs[-1]

        itemlist.append(item.clone( action='temporadas', url=url, title=title, 
                                    contentType = 'tvshow', contentSerieName = title, thumbnail=img ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", page=item.page + 1 ))

    return itemlist



def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    # Si viene de novedades, limpiar season, episode
    if item.contentEpisodeNumber: item.__dict__['infoLabels'].pop('episode')
    if item.contentSeason: item.__dict__['infoLabels'].pop('season')

    temporadas = re.findall('Temporada (\d+)', data)
    for tempo in sorted(temporadas, key=lambda x: int(x)):
        tempo = int(tempo)

        itemlist.append(item.clone( action='episodios', title='Temporada ' + str(tempo), 
                                    contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)

def episodios(item):
    logger.info()
    itemlist = []
    color_lang = config.get_setting('list_languages_color', default='red')

    data = do_downloadpage(item.url)

    matches = re.findall('<tr>\s*<td class="sape">(.*?)</tr>', data, re.DOTALL)
    for epi_data in matches:

        s_e = scrapertools.find_single_match(epi_data, '(\d+)(?:x|X)(\d+)')
        if not s_e: continue
        season = int(s_e[0])
        episode = int(s_e[1])

        if item.contentSeason and item.contentSeason != int(season):
            continue

        url = scrapertools.find_single_match(epi_data, ' href="([^"]+)')
        if not url: continue

        # ~ languages = ', '.join([IDIOMAS.get(lang, 'VO') for lang in re.findall('img/language/([^\.]+)', epi_data)])
        languages = ', '.join([IDIOMAS.get(lang, 'VO') for lang in list(dict.fromkeys(re.findall('img/language/([^\.]+)', epi_data)))])

        titulo = '%sx%s [COLOR %s][%s][/COLOR]' % (season, episode, color_lang, languages)

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, 
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    txt = txt.replace('HD-720p', '720p HD')
    orden = ['360p', '480p', 'HDTV', 'Micro-720p HD', '720p HD', 'Micro-HD-1080p', '1080p HD']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    # Limitar a enlaces online descartando descargas
    data = scrapertools.find_single_match(data, '<table(.*?)</table')

    matches = re.findall('<tr>(.*?)</tr>', data, re.DOTALL)
    for datos in matches:
        if '</th>' in datos: continue
        
        srv = scrapertools.find_single_match(datos, ' data-server="([^"]+)').lower().replace('www.', '')
        if not srv: continue
        if '.' in srv: srv = srv.split('.')[0]

        url = scrapertools.find_single_match(datos, ' data-enlace="([^"]+)')
        if not url: continue
        if url.startswith('/'): url = HOST + url[1:]
        
        if 'streamcrypt.net/' in url:
            srv = scrapertools.find_single_match(url.replace('embed/', ''), 'streamcrypt\.net/([^./]+)').lower()
        srv = servertools.corregir_servidor(srv)

        tds = scrapertools.find_multiple_matches(datos, '<td[^>]*>(.*?)</td>')
        quality = tds[2].strip()

        lang = scrapertools.find_single_match(datos, '/img/language/([^\.]+)')

        itemlist.append(Item( channel = item.channel, action = 'play', server=srv,
                              title = '', url = url,
                              language = IDIOMAS.get(lang, 'VO'), quality = quality, quality_num = puntuar_calidad(quality)
                       ))

    # ~ if len(itemlist) > 0: itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist

def play(item):
    logger.info()
    itemlist = []

    if 'streamcrypt.net/' in item.url: # Ej: https://streamcrypt.net/[embed/]flashx.tv/...
        url = scrapertools.decode_streamcrypt(item.url)

        if not url: return itemlist
        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))
    else:
        itemlist.append(item.clone())

    return itemlist


def search(item, texto):
    logger.info("texto=%s" % texto)
    itemlist = []

    try:
        item.url = HOST + '?s=' + texto.replace(" ", "+")
        data = do_downloadpage(item.url)

        matches = re.findall('<article (.*?)</article>', data, re.DOTALL)

        for serie_data in matches:
            url = scrapertools.find_single_match(serie_data, ' href="([^"]+)')
            if not url: continue

            title = scrapertools.find_single_match(serie_data, ' title="([^"]+)')
            if not title: continue

            img = scrapertools.find_single_match(serie_data, ' src="([^"]+)')

            itemlist.append(item.clone( title=title, url=url, action='temporadas', 
                                        contentType='tvshow', contentSerieName=title, thumbnail=img ))

        tmdb.set_infoLabels(itemlist)

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    return itemlist
