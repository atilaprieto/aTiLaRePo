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
list_servers = ['pornhub']

host = 'http://www.eroticage.net'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Novedades" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Popular" , action="lista", url=host + "/?filter=popular"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
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


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data,'>TAGS</h2>(.*?)</section>')
    patron  = '<a href="([^"]+)".*?>([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                               thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '<article id="post-\d+".*?'
    patron  += '<a href="([^"]+)" title="([^"]+)".*?'
    patron  += '<img data-src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        contentTitle = scrapedtitle
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl, thumbnail=thumbnail,
                               plot=plot, fanart=scrapedthumbnail, contentTitle=contentTitle ))
    next_page = scrapertools.find_single_match(data,'<li><a href="([^"]+)">Next')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist

# http://www.eroticage.net/three-aka-survival-island-2005-stewart-raffill/
# https://video.meta.ua/iframe/8118651/


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data,'<div class="responsive-player">(.*?)</div>')
    patron = 'data-src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl in matches:
        if "cine-matik.com" in scrapedurl:
            n = "yandex"
            m = scrapedurl.replace("https://cine-matik.com/player/play.php?", "")
            post = "%s&alternative=%s" %(m,n)
            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            data1 = httptools.downloadpage("https://cine-matik.com/player/ajax_sources.php", post=post, headers=headers).data
            if data1=="":
                n = "blogger"
                m = scrapedurl.replace("https://cine-matik.com/player/play.php?", "")
                post = "%s&alternative=%s" %(m,n)
                headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
                data1 = httptools.downloadpage("https://cine-matik.com/player/ajax_sources.php", post=post, headers=headers).data
            scrapedurl = scrapertools.find_single_match(data1,'"file":"([^"]+)"')
            if not scrapedurl:
                n = scrapertools.find_single_match(data1,'"alternative":"([^"]+)"')
                post = "%s&alternative=%s" %(m,n)
                headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
                data1 = httptools.downloadpage("https://cine-matik.com/player/ajax_sources.php", post=post, headers=headers).data
                scrapedurl = scrapertools.find_single_match(data1,'"file":"([^"]+)"')
            scrapedurl = scrapedurl.replace("\/", "/")
        if not "meta" in scrapedurl:
            itemlist.append(item.clone(action="play", title= "%s", contentTitle= item.title, url=scrapedurl))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
