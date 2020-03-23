# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re
from platformcode import logger
from core import scrapertools, httptools
from core.item import Item
from core import servertools

HOST = "http://es.xhamster.com/"


def mainlist(item):
    logger.info()

    itemlist = []
    itemlist.append(Item(channel=item.channel, action="videos", title="Útimos videos", url=HOST, viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="votados", title="Lo mejor"))
    itemlist.append(Item(channel=item.channel, action="vistos", title="Los mas vistos"))
    itemlist.append(Item(channel=item.channel, action="videos", title="Recomendados",
                         url=urlparse.urljoin(HOST, "/videos/recommended")))
    itemlist.append(Item(channel=item.channel, action="categorias", title="Categorías", url=HOST))
    itemlist.append(
        Item(channel=item.channel, action="search", title="Buscar", url=urlparse.urljoin(HOST, "/search?q=%s")))

    return itemlist


# REALMENTE PASA LA DIRECCION DE BUSQUEDA


def search(item, texto):
    logger.info()
    tecleado = texto.replace(" ", "+")
    item.url = item.url % tecleado
    item.extra = "buscar"
    try:
        return videos(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# SECCION ENCARGADA DE BUSCAR


def videos(item):
    logger.info()
    data = httptools.downloadpage(item.url).data
    itemlist = []

    data = scrapertools.find_single_match(data, '<article.+?>(.*?)</article>')

    patron = '(?s)<div class="thumb-list__item.*?'
    patron += 'href="([^"]+)".*?'
    patron += '<i class="([^"]+)">.*?'
    patron += 'src="([^"]+)".*?'
    patron += 'alt="([^"]+)">.*?'
    patron += '<div class="thumb-image-container__duration">(.+?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, quality, scrapedthumbnail, scrapedtitle, duration in matches:
        if "uhd" in quality: quality = "4K"
        if "hd" in quality: quality = "HD"
        else:  quality = ""
        title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (duration,quality, scrapedtitle.strip())
        itemlist.append(
            Item(channel=item.channel, action="play", title=title, url=scrapedurl, thumbnail=scrapedthumbnail,
                 folder=True))

    # Paginador
    patron = '(?s)<div class="pager-container".*?<li class="next">.*?href="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    if len(matches) > 0:
        url=matches[0].replace("&#x3D;", "=")
        itemlist.append(
            Item(channel=item.channel, action="videos", title="Página Siguiente >>", url=url, thumbnail="",
                 folder=True, viewmode="movie"))

    return itemlist


# SECCION ENCARGADA DE VOLCAR EL LISTADO DE CATEGORIAS CON EL LINK CORRESPONDIENTE A CADA PAGINA


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, '<div class="all-categories">(.*?)<li class="show-all-link">')
    patron = '<a href="([^"]+)".*?>([^<]+)\s+<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        contentTitle = scrapedtitle.strip()
        itemlist.append(Item(channel=item.channel, action="videos", title=contentTitle, url=scrapedurl))

    return itemlist


def votados(item):
    logger.info()
    itemlist = []

    itemlist.append(Item(channel=item.channel, action="videos", title="Día", url=urlparse.urljoin(HOST, "/best/daily"),
                         viewmode="movie"))
    itemlist.append(
        Item(channel=item.channel, action="videos", title="Semana", url=urlparse.urljoin(HOST, "/best/weekly"),
             viewmode="movie"))
    itemlist.append(
        Item(channel=item.channel, action="videos", title="Mes", url=urlparse.urljoin(HOST, "/best/monthly"),
             viewmode="movie"))
    itemlist.append(
        Item(channel=item.channel, action="videos", title="De siempre", url=urlparse.urljoin(HOST, "/best/"),
             viewmode="movie"))
    return itemlist


def vistos(item):
    logger.info()
    itemlist = []
    itemlist.append(
        Item(channel=item.channel, action="videos", title="Día", url=urlparse.urljoin(HOST, "/most-viewed/daily"),
             viewmode="movie"))
    itemlist.append(
        Item(channel=item.channel, action="videos", title="Semana", url=urlparse.urljoin(HOST, "/most-viewed/weekly"),
             viewmode="movie"))
    itemlist.append(
        Item(channel=item.channel, action="videos", title="Mes", url=urlparse.urljoin(HOST, "/most-viewed/monthly"),
             viewmode="movie"))
    itemlist.append(
        Item(channel=item.channel, action="videos", title="De siempre", url=urlparse.urljoin(HOST, "/most-viewed/"),
             viewmode="movie"))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '"embedUrl":"([^"]+)"')
    url = url.replace("\\", "")
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

