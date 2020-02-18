# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://www.tubxxporn.com'  #  https://www.pornktube.porn


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "/top-rated/"))
    itemlist.append( Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "/most-popular/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search/?q=%s" % texto
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    data= scrapertools.find_single_match(data, '>Back</a>(.*?)</div>')
    patron = '<a href="([^"]+)">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = ""
        plot = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="item">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'src="([^"]+)" alt="([^"]+)".*?'
    patron += '<div class="length">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedtime in matches:
        title = '[COLOR yellow] %s [/COLOR] %s' % (scrapedtime , scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class="mobnav">Next')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    id,data,server = scrapertools.find_single_match(data, '<div id="player" data-id="(\d+)".*?data-q="([^"]+)".*?data-n="(\d+)"')
    patron = '&nbsp;([A-z0-9]+);\d+;(\d+);([^,"]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,number,key in matches:
        nt = int(int(id)/1000)
        n = str(nt*1000)
        url = "http://s%s.fapmedia.com/cqpvid/%s/%s/%s/%s/%s_%s.mp4" % (server,number,key,n,id,id,quality)
        url= url.replace("_720p", "")
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist


