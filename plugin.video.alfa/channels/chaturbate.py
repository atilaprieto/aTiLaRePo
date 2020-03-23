# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://es.chaturbate.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Mujeres" , action="lista", url=host + "/female-cams/"))
    itemlist.append( Item(channel=item.channel, title="Hombres" , action="lista", url=host + "/male-cams/"))
    itemlist.append( Item(channel=item.channel, title="Parejas" , action="lista", url=host + "/couple-cams/"))
    itemlist.append( Item(channel=item.channel, title="Trans" , action="lista", url=host + "/trans-cams/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/tags/"))
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|\\", "", data)
    patron = '<span class="tag">.*?<a href="([^"]+)" title="([^"]+)".*?'
    patron += '<span class="rooms">(\d+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,cantidad in matches:
        title = "%s (%s)" % (scrapedtitle, cantidad) 
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<li class="room_list_room".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<div class="title"><a href="([^"]+)".*?>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)" class="next')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = data.replace("\u0022" , "\"").replace("\u002D", "-")
    url = scrapertools.find_single_match(data, '"hls_source"\: "([^"]+)"')
    itemlist.append(item.clone(action="play", url=url))
    return itemlist
