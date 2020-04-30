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
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import logger

host = 'http://www.submityourflicks.com'

                                # KT PLAYER 5.1.1

def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Útimos videos", action="lista", url= host + "/latest-updates/?&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos", action="lista", url= host + "/most-popular/?&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorados", action="lista", url= host + "/top-rated/?&from=1"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url= host))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/search/%s/?from_videos=1" % (host, texto)
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
    patron = '<div class="item thumb">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'data-original="([^"]+)".*?'
    patron += '<div class="sticky">(.*?)<div class="tools">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedtime in matches:
        quality = ""
        if "HD" in scrapedtime:
            quality = "HD"
        scrapedtime = scrapertools.find_single_match(scrapedtime, '<div class="time">([^<]+)</div>')
        title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" %(scrapedtime,quality,scrapedtitle)
        url = scrapedurl
        thumbnail = scrapedthumbnail.replace(" ", "%20")
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                             fanart=thumbnail, contentTitle = title))
    current_page = int(scrapertools.find_single_match(item.url,'.*?=(\d+)'))
    page = scrapertools.find_single_match(item.url, "(.*?)=\d+")
    if ">Load more...<" in data or ">Next<" in data:
        current_page = current_page + 1
        next_page = "%s=%s" %(page,current_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page))
    return itemlist  


def play(item):
    logger.info(item)
    itemlist = servertools.find_video_items(item.clone(url = item.url, contentTitle = item.title))
    return itemlist

