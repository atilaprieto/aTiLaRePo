# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://www.youporn.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevas", action="lista", url=host + "/browse/time/"))
    itemlist.append(item.clone(title="Mas Vistas", action="lista", url=host + "/browse/views/"))
    itemlist.append(item.clone(title="Mejor valorada", action="lista", url=host + "/top_rated/"))
    itemlist.append(item.clone(title="Canal", action="categorias", url=host + "/channels/most_popular/"))
    itemlist.append(item.clone(title="Pornstars", action="catalogo", url=host + "/pornstars/most_popular/"))
    itemlist.append(item.clone(title="Categorias", action="categorias", url=host + "/categories/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/?query=%s" % (host, texto)
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
    data1 = scrapertools.find_single_match(data,'>Most Popular Pornstars<(.*?)<i class=\'icon-menu-right\'></i></a>')
    patron = '<div class=\'porn-star-list three-column\' data-espnode="pornstar">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'data-original="([^"]+)".*?'
    patron += '<span class="porn-star-name">([^"]+)</span>.*?'
    patron += '<span class="video-count">([^"]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data1)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        title = "%s (%s)" %(scrapedtitle,cantidad)
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(item.clone(action="lista", title=title, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<div class="currentPage".*?<a href="([^"]+)"')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    if item.title == "Canal":
        data = scrapertools.find_single_match(data,'Most Popular Porn Channels </h1>(.*?)<footer data-espnode="footer">')
    if item.title == "Categorias":
        data = scrapertools.find_single_match(data,'<div class="container categoryListWrapper">(.*?)>Popular by Country</h2>')
    patron = '<a href="([^"]+)".*?'
    patron += '<img src=([^>]+).*?'
    patron += '>([^<]+)(?:Videos|videos)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,cantidad in matches:
        scrapedplot = ""
        thumbnail = scrapertools.find_single_match(scrapedthumbnail,'data-original="([^"]+)"') 
        scrapedtitle = scrapertools.find_single_match(scrapedthumbnail,'alt="([^"]+)"')
        if scrapedtitle == "" :
            scrapedtitle = scrapertools.find_single_match(scrapedthumbnail,'alt=\'([^\']+)\'')
        title = "%s (%s)" %(scrapedtitle,cantidad)
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(item.clone(action="lista", title=title, url=scrapedurl,
                              fanart=thumbnail, thumbnail=thumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<div class="currentPage".*?<a href="([^"]+)"')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<a href="(/watch/[^"]+)" class=\'video-box-image\'.*?'
    patron += 'data-original="([^"]+)".*?'
    patron += '<div class="video-box-title" title="([^"]+)".*?'
    patron += '<div class="video-duration">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,duracion  in matches:
        url = urlparse.urljoin(item.url,scrapedurl).replace("watch", "embed")
        title = "[COLOR yellow]%s[/COLOR] %s" % (duracion, scrapedtitle)
        contentTitle = title
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(item.clone(action="play" , title=title , url=url, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page = scrapertools.find_single_match(data,'<link rel="next" href="([^"]+)"')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page).replace("amp;", "")
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

