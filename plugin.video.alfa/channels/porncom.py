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

host = 'https://www.porn.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/pornstars"))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/channels"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/videos/search?q=%s" % (host,texto)
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|\\", "", data)
    patron = '<div class="list-global__item".*?'
    patron += 'href="([^"]+)">.*?'
    patron += 'data-src="([^"]+)" alt="([^"]+)".*?'
    patron += '<span>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        thumbnail = scrapedthumbnail
        scrapedtitle = scrapedtitle.replace(" Porn", "")
        title = "%s (%s)" % (scrapedtitle, cantidad)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, '<a class="next pagination__number" href="([^"]+)" rel="nofollow">Next')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="categorias", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>|amp;", "", data)
    patron = '<div class="list-global__item(.*?)'
    patron += 'class="go" title="([^"]+)".*?'
    patron += 'data-src="([^"]+)".*?'
    patron += 'duration">([^<]+)<.*?'
    patron += '<span><a href="[^"]+">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,time,server in matches:
        title = "[COLOR yellow]%s[/COLOR] [%s] %s" % (time, server, scrapedtitle)
        thumbnail = scrapedthumbnail
        url = ""
        url = scrapertools.find_single_match(scrapedurl,'<a href=".*?/(aHR0[^"]+)/\d+/\d+"') 
        url = url.replace("%3D", "=").replace("%2F", "/")
        if url=="":
            url = scrapertools.find_single_match(scrapedurl,'(//www.paidperview.com/video/embed/\d+)')
            url = "https:%s" %url
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<a class="next pagination__number" href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    if not "paidperview" in item.url:
        import base64
        url = item.url.replace("_", "/")
        url = base64.b64decode(url)
        itemlist = servertools.find_video_items(item.clone(url = url, contentTitle = item.title))
    else:
        data = httptools.downloadpage(item.url).data
        url = scrapertools.find_single_match(data, 'url:"([^"]+)"')
        itemlist.append(['.mp4', url])
    return itemlist

