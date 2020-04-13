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

host = 'http://www.vintagexxxsex.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Top" , action="lista", url=host + "/all-top/1/"))
    itemlist.append( Item(channel=item.channel, title="Novedades" , action="lista", url=host + "/all-new/1/"))
    itemlist.append( Item(channel=item.channel, title="Longitud" , action="lista", url=host + "/all-longest/1/"))
    # itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s/en/search/%s/" % (host, texto)
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
    patron  = '<div class="preview">.*?'
    patron += '<a href="(/en/category/[^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<div class="name name-2">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        plot = ""
        url ="%s%s" %(host,scrapedurl)
        if not scrapedthumbnail.startswith("https"):
            thumbnail= "https:%s" %scrapedthumbnail
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="preview">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<div class="name">([^<]+)<.*?'
    patron += '<i class="fa fa-clock-o"></i>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedtime in matches:
        title = "[COLOR yellow]%s[/COLOR] %s" %(scrapedtime.strip(),scrapedtitle)
        scrapedurl = scrapedurl.replace("/real.php?tube=", "")
        scrapedurl = "%s%s" %(host,scrapedurl)
        if not scrapedthumbnail.startswith("https"):
            thumbnail= "https:%s" %scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play" , title=title , url=scrapedurl,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot))
    next_page = scrapertools.find_single_match(data,'<li><a href="([^"]+)" target="_blank">NEXT')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist



def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    txt = scrapertools.find_single_match(data,'<iframe src=".*?(aHR0[^"]+)"')
    import base64
    url = base64.b64decode(txt)
    itemlist.append( Item(channel=item.channel, action="play", title = "%s", url=url, contentTitle=item.title))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

