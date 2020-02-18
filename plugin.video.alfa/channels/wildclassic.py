# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'http://www.wildclassic.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/vintage/newest-videos/"))
    itemlist.append( Item(channel=item.channel, title="Popular" , action="lista", url=host + "/vintage/"))
    itemlist.append( Item(channel=item.channel, title="Mas largos" , action="lista", url=host + "/vintage/longest-videos/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/?query=%s" % texto
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
    patron = '<a href="([^"]+)" class="cle">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    
    
    patron = '<li>.*?'
    patron += '<a class=thumba href="([^"]+)".*?'
    patron += '<img alt="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<strong>([^<]+)</strong>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle ,scrapedthumbnail,scrapedtime in matches:
        title = "[COLOR yellow]" + scrapedtime + "[/COLOR] " + scrapedtitle
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li class="next visible"><a href="([^"]+)"')
    if next_page =="":
        next_page = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist



def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    url = scrapertools.find_single_match(data, '<iframe src=\'([^\']+)\'')
    url = urlparse.urljoin(item.url,url)
    data = httptools.downloadpage(url).data
    url = scrapertools.find_single_match(data, '<source src="([^"]+)"')
    if not url:
        url = scrapertools.find_single_match(data, 'src="([^"]+)"')
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


