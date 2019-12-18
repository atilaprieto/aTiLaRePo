# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://www.pornohdmega.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/?filter=latest"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorados" , action="lista", url=host + "/?filter=top-rated"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/?filter=most-viewed"))
    itemlist.append( Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "/?filter=popular"))
    
    itemlist.append( Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/tags/"))
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<a href="([^"]+)" class="tag.*?'
    patron += 'aria-label="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        numero = scrapertools.find_single_match(scrapedtitle, '\((\d+)')
        thumbnail = ""
        scrapedplot = ""
        if int(numero) > 10:
            itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                                  thumbnail=thumbnail , plot=scrapedplot) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<article id="post-\d+".*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        scrapedplot = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=thumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<article id="post-\d+".*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot,))
    next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)">Next')
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
    patron = '<div class="responsive-player">.*?src="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        itemlist.append(item.clone(action="play", title= "%s", contentTitle=item.title, url=url))
        itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

