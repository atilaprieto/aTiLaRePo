# -*- coding: utf-8 -*-
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from core import httptools
from core import servertools
from core import scrapertools
from core.item import Item
from platformcode import logger

host = 'http://pornhub.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="lista", title="Novedades", fanart=item.fanart,
                         url="%s/video?o=cm" %host))
    itemlist.append(Item(channel=item.channel, action="lista", title="Mas visto", fanart=item.fanart,
                         url="%s/video?o=mv" %host))
    itemlist.append(Item(channel=item.channel, action="lista", title="Mejor valorado", fanart=item.fanart,
                         url="%s/video?o=tr" %host))
    itemlist.append(Item(channel=item.channel, action="lista", title="Mas largo", fanart=item.fanart,
                         url="%s/video?o=lg" %host))
    itemlist.append(Item(channel=item.channel, action="catalogo", title="Canal", fanart=item.fanart,
                         url= "%s/channels?o=tr" % host))
    itemlist.append(Item(channel=item.channel, action="catalogo", title="PornStar", fanart=item.fanart,
                         url= "%s/pornstars?o=t" % host))
    itemlist.append(Item(channel=item.channel, action="categorias", title="Categorias", fanart=item.fanart,
                         url= "%s/categories" % host))
    itemlist.append(Item(channel=item.channel, action="search", title="Buscar", fanart=item.fanart))
    return itemlist


def search(item, texto):
    logger.info()

    item.url = "%s/video/search?search=%s&o=mr" % (host, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if "channels" in item.url:
        patron = '<div class="channelsWrapper.*?'
        patron += 'href="([^"]+)".*?'
        patron += 'alt="([^"]+)".*?'
        patron += 'data-thumb_url="([^"]+)".*?'
        patron += 'Videos<span>([^<]+)<'
    else:
        patron = 'data-mxptype="Pornstar".*?'
        patron += 'href="([^"]+)".*?'
        patron += 'data-thumb_url="([^"]+)".*?'
        patron += 'alt="([^"]+)".*?'
        patron += '"videosNumber">(\d+) Videos'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle, cantidad in matches:
        if "channels" in scrapedurl:
            scrapedthumbnail, scrapedtitle = scrapedtitle, scrapedthumbnail
            url = urlparse.urljoin(item.url, scrapedurl + "/videos?o=da")
        else:
            url = urlparse.urljoin(item.url, scrapedurl + "/videos?o=cm")
        scrapedtitle = "%s (%s)" % (scrapedtitle,cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                             fanart=scrapedthumbnail, thumbnail=scrapedthumbnail))
        # Paginador
    if itemlist:
        patron = '<li class="page_next"><a href="([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if matches:
            url = urlparse.urljoin(item.url, matches[0].replace('&amp;', '&'))
            itemlist.append(
                Item(channel=item.channel, action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]",
                     fanart=item.fanart, url=url))
    return itemlist

def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div class="category-wrapper.*?'
    patron += 'href="([^"]+)".*?'
    patron += 'data-thumb_url="([^"]+)".*?'
    patron += 'alt="([^"]+)".*?'
    patron += '<var>(.*?)</var>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle, cantidad in matches:
        if "?" in scrapedurl:
            url = urlparse.urljoin(item.url, scrapedurl + "&o=cm")
        else:
            url = urlparse.urljoin(item.url, scrapedurl + "?o=cm")
        scrapedtitle = "%s (%s)" % (scrapedtitle,cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                             fanart=scrapedthumbnail, thumbnail=scrapedthumbnail))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div class="phimage">.*?'
    patron += '<a href="([^"]+)" title="([^"]+).*?'
    patron += 'data-mediumthumb="([^"]+)".*?'
    patron += '<var class="duration">([^<]+)</var>(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, scrapedtitle, thumbnail, duration, scrapedhd in matches:
        scrapedhd = scrapertools.find_single_match(scrapedhd, '<span class="hd-thumbnail">(.*?)</span>')
        if scrapedhd  == 'HD':
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s"% (duration,scrapedhd,scrapedtitle)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (duration,scrapedtitle)
        url = urlparse.urljoin(item.url, url)
        itemlist.append(Item(channel=item.channel, action="play", title=title, contentTitle = title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail))
    if itemlist:
        # Paginador
        patron = '<li class="page_next"><a href="([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if matches:
            url = urlparse.urljoin(item.url, matches[0].replace('&amp;', '&'))
            itemlist.append(
                Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]",
                     fanart=item.fanart, url=url))
    return itemlist


def play(item):
    logger.info(item)
    itemlist = servertools.find_video_items(item.clone(url = item.url))
    return itemlist

