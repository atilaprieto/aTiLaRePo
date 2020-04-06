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

host = 'https://letsjerk.to'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/?order=newest"))
    itemlist.append( Item(channel=item.channel, title="Mas valorados" , action="lista", url=host + "/?order=rating_month"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/?order=views_month"))
    itemlist.append( Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/?order=comments_month"))
    
    # itemlist.append( Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/studios/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s&s=%s" % (host,texto, texto)
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
    patron = '<a class="th" href="([^"]+)">.*?'
    patron += 'data-original="([^"]+)" alt="([^"]+)".*?'
    patron += '<div class="number">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        title = "%s (%s)" % (scrapedtitle, cantidad)
        thumbnail = scrapedthumbnail
        url = urlparse.urljoin(host,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    return sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<li style="list-style-type: none;"><a href="([^"]+)" title="([^"]+)".*?'
    patron += 'data-original="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    data = scrapertools.find_single_match(data, '<div class="video-container">(.*?)</div>')
    patron = '<source title="([^"]+)" src=([^\s]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality, url in matches:
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist

