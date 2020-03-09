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

host = 'http://www.absoluporn.com/en'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/wall-date-1.html"))
    itemlist.append( Item(channel=item.channel, title="Mas valorados" , action="lista", url=host + "/wall-note-1.html"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/wall-main-1.html"))
    itemlist.append( Item(channel=item.channel, title="Mas largos" , action="lista", url=host + "/wall-time-1.html"))

    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search-%s-1.html" % (host, texto)
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
    patron  = '&nbsp;<a href="([^"]+)" class="link1b">([^"]+)</a>&nbsp;<span class="text23">([^<]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        title = "%s %s" %(scrapedtitle,cantidad)
        scrapedurl = scrapedurl.replace(".html", "_date.html")
        scrapedurl = "%s/%s" % (host, scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="thumb-main-titre"><a href="([^"]+)".*?'
    patron += 'title="([^"]+)".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<div class="time">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,scrapedtime in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = "[COLOR yellow]%s[/COLOR] %s" % (scrapedtime, scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail, plot=plot,
                              fanart=thumbnail, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<span class="text16">\d+</span> <a href="..([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = 'servervideo = \'([^\']+)\'.*?'
    patron += 'path = \'([^\']+)\'.*?'
    patron += 'filee = \'([^\']+)\'.*?'
    matches = scrapertools.find_multiple_matches(data, patron)
    for servervideo,path,filee  in matches:
        scrapedurl = "%s%s56ea912c4df934c216c352fa8d623af3%s" % (servervideo, path, filee)
        itemlist.append(item.clone(action="play", title= item.title, url=scrapedurl))
    return itemlist

