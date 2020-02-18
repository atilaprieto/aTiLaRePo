# -*- coding: utf-8 -*-
# -*- Channel lacartoons -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-


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
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['okru']


__channel__='lacartoons'

host = "https://www.lacartoons.com"

try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = []
    itemlist.append(Item(channel = item.channel, title = "Novedades", action = "lista", url = host, page = 1, thumbnail = get_thumb("newest", auto = True)))
    itemlist.append(Item(channel = item.channel, title = "Categorias", action = "categorias", url = host, thumbnail = get_thumb("categories", auto = True) ))
    itemlist.append(Item(channel = item.channel, title = "Buscar", action = "search", url = host + "/?Titulo=", thumbnail = get_thumb("search", auto = True)))
    autoplay.show_option(item.channel, itemlist)
    return itemlist
    
   
def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.find_single_match(data, 'botontes-categorias.*?</ul>')
    patron  = 'submit" value="([^"]+).*?'
    patron += 'value="([^"]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for title, id in matches:
        itemlist.append(Item(channel = item.channel,
                             action = "lista",
                             page = 0,
                             title = title,
                             url = host + "/?Categoria_id=" + id
                        ))
    return itemlist

    
def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = 'a href="(/serie[^"]+).*?'
    patron += 'src="([^"]+).*?'
    patron += 'nombre-serie">([^<"]+).*?'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, thumbnail, title in matches:
        itemlist.append(Item(channel = item.channel,
                             action = "episodios",
                             contentserieName = title,
                             thumbnail = host + thumbnail,
                             title = title,
                             url = host + url
                        ))
    tmdb.set_infoLabels(itemlist)
    page = item.page + 1
    if not item.extra:
        itemlist.append(Item(channel = item.channel,
                                action = "lista",
                                contentserieName = title,
                                page = page,
                                thumbnail = host + thumbnail,
                                title = "Pagina: %s" %page,
                                url = item.url + "?page=%s" %(page)
                    ))
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = 'listas-de-episodion.*?href="([^"]+).*?'
    patron += 'span>(.*?)</a>.*?'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, title in matches:
        title = title.replace("</span>","")
        itemlist.append(item.clone(action = "findvideos",
                                   title = title,
                                   url = host + url
                                   ))
    next_page = scrapertools.find_single_match(data, '(?is)next" href="([^"]+)"')
    if next_page:
        itemlist.append(item.clone(action = "episodios",
                                   title = "Siguiente Pagina",
                                   url = host + next_page
                                   ))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    item.extra = "busca"
    item.page = 0
    if texto != '':
        return lista(item)
    else:
        return []


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '<iframe src="([^"]+)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        itemlist.append(item.clone(action = "play",
                                   title = "Ver en %s",
                                   url = url
                                   ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    tmdb.set_infoLabels(itemlist, __modo_grafico__)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    if itemlist and item.contentChannel != "videolibrary":
        itemlist.append(Item(channel = item.channel))
        # Opción "Añadir esta película a la biblioteca de KODI"
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir a la videoteca", text_color="green",
                                 action="add_pelicula_to_library", url=item.url, thumbnail = item.thumbnail,
                                 contentTitle = item.contentTitle
                                 ))
    return itemlist


def play(item):
    item.thumbnail = item.contentThumbnail
    return [item]
