# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse
import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['verystream']

host = "http://www.filmovix.net"

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append( Item(channel=item.channel, title="Peliculas" , action="lista", url=host + "/videoscategory/porno/"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data,'<h1 class="cat_head">XXX</h1>(.*?)<h3> Novo dodato </h3>')
    patron  = '<li class="clearfix">.*?'
    patron += 'src="([^"]+)".*?'
    patron += '<p class="title"><a href="([^"]+)" rel="bookmark" title="([^"]+)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedurl,scrapedtitle in matches:
        contentTitle = scrapedtitle
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="findvideos", title=title, url=scrapedurl,
                               thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle=contentTitle))
    next_page_url = scrapertools.find_single_match(data,'<a class="nextpostslink" rel="next" href="([^"]+)">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(item.clone(action="mainlist", title="Página Siguiente >>", text_color="blue", url=next_page_url) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist = servertools.find_video_items(item.clone(url = item.url, action='play', language='VO', contentTitle = item.title))
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
