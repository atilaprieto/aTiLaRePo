# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from core.item import Item
from core import httptools
from core import scrapertools
from core import servertools
from platformcode import config, logger


host= "http://dato.porn"

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="lista", title="Nuevos", url=host + "/latest-updates/"))
    itemlist.append(item.clone(action="lista", title="Mejor valorado", url=host + "/top-rated/"))
    itemlist.append(item.clone(action="lista", title="Mas visto", url=host + "/top-rated/"))

    itemlist.append(item.clone(action="categorias", title="Categorías", url=host + "/categories/"))
    itemlist.append(item.clone(title="Buscar...", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "http://dato.porn/?k=%s&op=search" % texto
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<a class="item" href="([^"]+)" title="([^"]+)".*?'
    patron += '<div class="videos">([^<]+) videos<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle, numero in matches:
        if numero:
            scrapedtitle = "%s  (%s)" % (scrapedtitle, numero)
        itemlist.append(item.clone(action="lista", title=scrapedtitle, url=scrapedurl, thumbnail=""))
    return sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", data)
    patron = '<div class="item">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'data-original="([^"]+)"(.*?)'
    patron += '<div class="duration">([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedtitle, scrapedthumbnail, quality, duration in matches:
        title = '[COLOR yellow] %s [/COLOR] %s' % (duration , scrapedtitle)
        if "HD" in quality:
            title = '[COLOR yellow] %s [/COLOR] [COLOR red] HD [/COLOR] %s' % (duration , scrapedtitle)
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=scrapedurl, thumbnail=scrapedthumbnail,
                             fanart=scrapedthumbnail.replace("_t.jpg", ".jpg"), contentTitle=title, plot = ""))
    next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    if "#" in next_page:
        next_page = scrapertools.find_single_match(data, 'data-parameters="([^"]+)">Next')
        next_page = next_page.replace(":", "=").replace(";", "&").replace("+from_albums", "")
        next_page = "?%s" % next_page
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

