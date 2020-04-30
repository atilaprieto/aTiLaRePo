# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['bitp']

host = 'http://yuuk.net'


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append( Item(channel=item.channel, title="Peliculas" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/list-genres/"))
    itemlist.append( Item(channel=item.channel, title="Buscar" , action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host, texto)
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
    itemlist.append( Item(channel=item.channel, title="Censored" , action="lista", url=host + "/category/censored/"))
    itemlist.append( Item(channel=item.channel, title="Uncensored" , action="lista", url=host + "/category/uncensored/"))
    patron = '<li><a href="([^"]+)" title="[^"]+"><span>([^"]+)</span><span>([^"]+)</span></a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl,scrapedtitle,cantidad in matches:
        scrapedtitle = "%s (%s)" %(scrapedtitle,cantidad)
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div class="featured-wrap clearfix">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += '>#([^"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl,scrapedtitle,scrapedthumbnail,calidad in matches:
        scrapedplot = ""
        calidad = calidad.replace(" Full HD JAV", "")
        title = "[COLOR red]%s[/COLOR] %s" % (calidad, scrapedtitle)
        itemlist.append( Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<li class=\'current\'>.*?<a rel=\'nofollow\' href=\'([^\']+)\' class=\'inactive\'>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    data = scrapertools.find_single_match(data,'Streaming Server<(.*?)Screenshot<')
    patron = '(?:src|SRC)="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        if "http://stream.yuuk.net/embeds.php" in url:
            data = httptools.downloadpage(url).data
            url = scrapertools.find_single_match(data,'"file": "([^"]+)"')
        itemlist.append( Item(channel=item.channel, action="play", title = "%s", contentTitle=item.contentTitle, url=url ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

