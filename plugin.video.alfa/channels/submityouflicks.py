# -*- coding: utf-8 -*-

import re
import urlparse

from core import httptools
from core import scrapertools
from core.item import Item
from platformcode import logger

host = 'http://www.submityourflicks.com'

def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Útimos videos", action="lista", url= host + "/top-rated/?&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos", action="lista", url= host + "/most-popular/?&from=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorados", action="lista", url= host + "/top-rated/?&from=1"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url= host))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = host + "/search/%s/?from_videos=1" % texto
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
                             fanart=thumbnail))
    current_page = int(scrapertools.find_single_match(item.url,'.*?=(\d+)'))
    page = scrapertools.find_single_match(item.url, "(.*?)=\d+")
    if ">Load more...<" in data or ">Next<" in data:
        current_page = current_page + 1
        next_page = "%s=%s" %(page,current_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue",
                             url=next_page))
    return itemlist  


def play(item):
    logger.info(item)
    itemlist = servertools.find_video_items(item.clone(url = item.url, contentTitle = item.title))
    return itemlist
