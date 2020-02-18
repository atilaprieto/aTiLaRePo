# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from channels import cumlouder

host = 'https://www.foxtube.com' #https://www.muyzorras.com

#Falta channel ajax {url:"/users/doIFollow/749/"

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Ultimos" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + '/pornstars/'))
    # itemlist.append( Item(channel=item.channel, title="Canal" , action="catalogo", url=host + '/channels/'))
    
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/buscador/%s" % texto
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<article>.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img.*?src="([^"]+)".*?'
    patron += 'alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle  in matches:
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail.replace("https","http") + "|Referer=%s/pornstars/" %host
        plot = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=plot) )
    next_page = scrapertools.find_single_match(data,'<a rel="next" href="([^"]+)">&gt')
    if not next_page:
        next_page = scrapertools.find_single_match(data,'<span class="">.*?href="([^"]+)"')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="catalogo" , title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<li><a href="([^"]+)" title="([^"]+)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<article>.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img.*?src="([^"]+)".*?'
    patron += 'alt="([^"]+)".*?'
    patron += '<span class="r\w">(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,duracion  in matches:
        time = scrapertools.find_single_match(duracion, '<span>([^<]+)</span></span>')
        title = "[COLOR yellow]" + time + "[/COLOR] " + scrapedtitle
        if 'HD' in duracion :
            title = "[COLOR yellow]" + time + "[/COLOR] " + "[COLOR red]" + "HD" + "[/COLOR]  " + scrapedtitle
        thumbnail = scrapedthumbnail.replace("https","http") + "|Referer=%s/" %host
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data,'<a rel="next" href="([^"]+)">&gt')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista" , title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    url = ""
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data,'<iframe title="[^"]+" class="lz" data-src="([^"]+)"')
    if "cumlouder" in url:
        item1 = item.clone(url=url)
        itemlist = cumlouder.play(item1)
        return itemlist
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


