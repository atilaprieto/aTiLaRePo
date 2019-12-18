# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools

host = 'http://free-porn-videos.xyz'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Peliculas" , action="lista", url=host + "/genre/adult-movies-online/"))
    itemlist.append( Item(channel=item.channel, title="Videos" , action="lista", url=host + "/genre/xxx-videos"))
    itemlist.append( Item(channel=item.channel, title="Videos amateur" , action="lista", url=host + "/genre/xxx-videos/real-amateur-porn/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/?s=%s" % texto
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
    patron = '<div data-movie-id="\d+".*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img data-original="([^"]+)".*?'
    patron += 'alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedplot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, contentTitle=scrapedtitle, plot=scrapedplot) )
    next_page_url = scrapertools.find_single_match(data,'<li class=\'active\'>.*?href=\'([^\']+)\'>')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page_url) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    scrapedurl = scrapertools.find_single_match(data,'<iframe src="([^"]+)"')
    url = scrapedurl.replace("%28", "(").replace("%29", ")")
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

