# -*- coding: utf-8 -*-
# -*- Channel Yape -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import codecs
from channelselector import get_thumb
from channels import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger


IDIOMAS = {'Latino': 'Latino'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['fastplay', 'flashx', 'vimeo']


__channel__='allpeliculastv'

host = "https://allpeliculas.nu"

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []
    itemlist.append(Item(channel = item.channel, title = "Novedades", action = "peliculas", url = host, thumbnail = get_thumb("newest", auto = True), pagina=0))
    itemlist.append(Item(channel = item.channel, title = "Por género", action = "generos", url = host, thumbnail = get_thumb("genres", auto = True) ))
    itemlist.append(Item(channel = item.channel, title = "Destacadas", action = "destacadas", url = host, thumbnail = get_thumb("favorites", auto = True) ))
    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(Item(channel = item.channel, title = "Buscar", action = "search", url = host + "/?s=", thumbnail = get_thumb("search", auto = True)))
    autoplay.show_option(item.channel, itemlist)
    return itemlist

def destacadas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, 'destacadas.*?Agregadas')
    patron  = '(?is)poster-media-card"> <a href="([^"]+)'
    patron += '.*?title="([^"]+)'
    patron += '.*?data-lazy-src="([^"]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for url, titulo, thumbnail  in matches:
        year = scrapertools.find_single_match(titulo, ' \(.*?\)')
        titulo = titulo.replace(year, "")
        itemlist.append(item.clone(channel = item.channel,
                                   action = "findvideos",
                                   contentTitle = titulo,
                                   infoLabels={"filtro":thumbnail.replace("https://image.tmdb.org/t/p/w300","")},
                                   thumbnail = thumbnail,
                                   title = titulo,
                                   url = host + url,
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    item.url = host
    item.pagina = 0
    try:
        if categoria in ['peliculas','latino']:
            item.pagina = 0
        elif categoria == 'infantiles':
            item.query = '"category_name":"animacion"'
        elif categoria == 'terror':
            item.query = '"category_name":"terror"'
        itemlist = peliculas(item)
        if "Pagina" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def search(item, texto):
    logger.info()
    item.url = item.url + texto
    item.extra = "busca"
    item.query = '"s":"%s"' %texto
    item.patron = 'cula de (\w+)'
    item.pagina = 0
    if texto != '':
        return sub_search(item)
    else:
        return []


def sub_search(item):
    logger.info()
    itemlist = []
    post = 'action=loadmore&query={%s}&page=%s' %(item.query, item.pagina)
    data = httptools.downloadpage(host + "/wp-admin/admin-ajax.php", post=post).data
    patron  = '<a href="([^"]+).*?'
    patron += 'title="([^"]+).*?'
    patron += 'year="([^"]+).*?'
    patron += '(https://image[^"]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, title, year, thumbnail in matches:
        language = ""
        y = scrapertools.find_single_match(title, "\(....\)")
        title = title.replace("(" + year + ")", "").replace(y, "")
        itemlist.append(item.clone(action="findvideos",
                                   contentTitle = title,
                                   infoLabels={"year":year},
                                   language=language,
                                   thumbnail=thumbnail,
                                   title=title + " (%s)" %year,
                                   url=url
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    item.pagina += 1
    pagina = "Pagina: %s" %(item.pagina + 1)
    itemlist.append(Item(channel = item.channel, action = "peliculas", genero=item.genero, title = pagina, pagina = item.pagina))
    return itemlist


def generos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = 'navigation","name":"([^"]+).*?'
    patron += 'url":"([^"]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for titulo, url in matches:
        titulo = codecs.decode(titulo,"unicode-escape")
        url = url.replace("\\","")
        genero = scrapertools.find_single_match(url, "tv/([^/]+)")
        if "neros" in titulo or "Twitch" in titulo: continue
        itemlist.append(Item(channel = item.channel,
                             action = "peliculas",
                             query = '"category_name":"%s"' %genero,
                             pagina = 0,
                             title = titulo,
                             ))
    itemlist = sorted(itemlist, key=lambda i: i.title)
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    post = 'action=loadmore&query={%s}&page=%s' %(item.query, item.pagina)
    data = httptools.downloadpage(host + "/wp-admin/admin-ajax.php", post=post).data
    patron  = '<a href="([^"]+).*?'
    patron += 'title="([^"]+).*?'
    patron += 'alt="([^"]+).*?'
    patron += 'year="([^"]+).*?'
    patron += '(https://image[^"]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, title, language, year, thumbnail in matches:
        y = scrapertools.find_single_match(title, "\(....\)")
        title = title.replace("(" + year + ")", "").replace(y, "")
        itemlist.append(item.clone(action="findvideos",
                                   contentTitle = title,
                                   infoLabels={"year":year},
                                   language=language,
                                   thumbnail=thumbnail,
                                   title=title + " (%s)" %year,
                                   url=url
                                   ))
    tmdb.set_infoLabels_itemlist(itemlist, __modo_grafico__)
    item.pagina += 1
    pagina = "Pagina: %s" %(item.pagina + 1)
    itemlist.append(Item(channel = item.channel, action = "peliculas", genero=item.genero, title = pagina, pagina = item.pagina))
    return itemlist


def findvideos(item):
    itemlist = []
    encontrado = []
    data = httptools.downloadpage(item.url).data
    patron  = '#embed." data-src="([^"]+).*?'
    patron += 'class="([^"]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, language in matches:
        url = get_url(host + url)
        url = url.replace("feurl.com/v","feurl.com/f")
        encontrado.append(url)
        itemlist.append(Item(
                        channel=item.channel,
                        contentTitle=item.contentTitle,
                        contentThumbnail=item.thumbnail,
                        infoLabels=item.infoLabels,
                        language=language,
                        title="Ver en %s " + "(" + language + ")",
                        action="play",
                        url=url
                       ))
    patron = '(?is)<a href=".*?go.([^"]+)" class="btn btn-xs btn-info.*?<span>([^<]+)</span>.*?<td>([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, srv, language in matches:
        if url in encontrado or ".srt" in url:
            continue
        encontrado.append(url)
        new_item= Item(channel=item.channel, url=url, title="Ver en %s " + "(" + language + ")", action="play", contentTitle=item.contentTitle, contentThumbnail=item.thumbnail,
                       infoLabels=item.infoLabels, language="Latino")
        if "torrent" in srv.lower():
            new_item.server = "Torrent"
        itemlist.append(new_item)
    
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if itemlist and item.contentChannel != "videolibrary":
        itemlist.append(Item(channel=item.channel))
        itemlist.append(item.clone(channel="trailertools", title="Buscar Tráiler", action="buscartrailer", context="",
                                   text_color="magenta"))

        # Opción "Añadir esta película a la biblioteca de KODI"
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir a la videoteca", text_color="green",
                                 action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                                 contentTitle = item.contentTitle
                                 ))
    return itemlist


def get_url(url):
    itemlist = []
    data = httptools.downloadpage(url).data
    if "replay" in url:
        url = scrapertools.find_single_match(data, 'video-iframe" src="([^"]+)')
        if "cuevana3" in url:
            from channels import cuevana3
            item = Item(url=url)
            itemlist=cuevana3.play(item)
            url = itemlist[0].url
            return item.url
    return url


def play(item):
    item.thumbnail = item.contentThumbnail
    return [item]
