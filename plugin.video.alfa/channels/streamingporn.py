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
list_servers = ['gounlimited']

host = 'http://streamingporn.xyz'   #'http://sexgalaxy.net'

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(item.clone(title="Peliculas" , action="lista", url=host + "/category/movies/"))
    itemlist.append(item.clone(title="Videos" , action="lista", url=host + "/category/stream/"))
    itemlist.append(item.clone(title="Buscar", action="search"))

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


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<article id="post-\d+".*?'
    patron += '<a href="([^"]+)" rel="bookmark">([^<]+)<.*?'
    patron += 'data-lazy-src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail  in matches:
        url = scrapedurl
        title = scrapedtitle
        if 'HD' in scrapedtitle :
            calidad = scrapertools.find_single_match(scrapedtitle, '(\d+)p')
            title = "[COLOR red]HD[/COLOR] %s"  %scrapedtitle
            if calidad :
                title = "[COLOR red]HD%s[/COLOR] %s"  %(calidad,scrapedtitle)
        contentTitle = title
        thumbnail = scrapedthumbnail
        plot = ""
        if not "manyvids" in url:
            itemlist.append(item.clone(action="findvideos" , title=title , url=url, thumbnail=thumbnail, 
                              fanart=scrapedthumbnail, plot=plot, contentTitle = contentTitle) )
                              
    next_page_url = scrapertools.find_single_match(data,'rel="next" href="([^"]+)"')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page_url) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|amp;|\s{2}|&nbsp;", "", data)
    patron = '<a href="([^"]+)" rel="nofollow[^<]+>(?:Streaming|Download)'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        itemlist.append(item.clone(action='play',title="%s", contentTitle=item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

