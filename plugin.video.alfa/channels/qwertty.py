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

from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools

host = 'http://qwertty.net'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Recientes" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Mas Vistas" , action="lista", url=host + "/?filter=most-viewed"))
    itemlist.append( Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "/?filter=popular"))
    itemlist.append( Item(channel=item.channel, title="Mejor valoradas" , action="lista", url=host + "/?filter=random"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host, texto)
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
    patron  = '<li><a href="([^<]+)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = host + scrapedurl
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<article id="post-\d+".*?'
    patron += '<a href="(https://qwertty.net/\d+/).*?" title="([^"]+)">.*?'
    patron += '<div class="post-thumbnail(.*?)<span class="views">.*?'
    patron += '<span class="duration"><i class="fa fa-clock-o"></i>([^<]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,duracion in matches:
        scrapedplot = ""
        thumbnail = scrapertools.find_single_match(scrapedthumbnail, 'poster="([^"]+)"')
        if thumbnail == "":
            thumbnail = scrapertools.find_single_match(scrapedthumbnail, "data-thumbs='(.*?jpg)")
        title = "[COLOR yellow]%s[/COLOR] %s" % (duracion,scrapedtitle)
        itemlist.append( Item(channel=item.channel, action="play", title=title, contentTitle = title, url=scrapedurl,
                              fanart=thumbnail, thumbnail=thumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<li><a href="([^"]+)">Next</a>')
    if next_page=="":
        next_page = scrapertools.find_single_match(data,'<li><a class="current">.*?<li><a href="([^"]+)" class="inactive">')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url1 = scrapertools.find_single_match(data,'<meta itemprop="embedURL" content="([^"]+)"')
    if "spankwire" in url1: 
        data = httptools.downloadpage(item.url).data
        data = scrapertools.get_match(data,'Copy Embed Code(.*?)For Desktop')
        patron  = '<div class="shareDownload_container__item__dropdown">.*?<a href="([^"]+)"'
        matches = scrapertools.find_multiple_matches(data, patron)
        for scrapedurl  in matches:
            url = scrapedurl
            if url=="#":
                url = scrapertools.find_single_match(data,'playerData.cdnPath480         = \'([^\']+)\'')
            itemlist.append(item.clone(action="play", title=url, contentTitle = url, url=url))
    else:
        data = httptools.downloadpage(url1).data
        url  = scrapertools.find_single_match(data,'"quality":"\d+","videoUrl":"([^"]+)"')
    if not url:
        url=url1
    url = url.replace("\/", "/")

    itemlist.append(item.clone(action="play", title= "%s  " + url1, contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    return itemlist

