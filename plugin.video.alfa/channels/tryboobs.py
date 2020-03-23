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

host = 'http://www.tryboobs.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevas" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Popular" , action="lista", url=host + "/most-popular/week/"))
    itemlist.append( Item(channel=item.channel, title="Mejor Valorado" , action="lista", url=host + "/top-rated/week/"))
    itemlist.append( Item(channel=item.channel, title="Modelos" , action="categorias", url=host + "/models/model-viewed/1/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/?q=%s" % (host, texto)
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<a href="([^"]+)" class="th-[^"]+">.*?'
    patron += 'src="([^"]+)" alt=.*?'
    patron += '<span>(\d+)</span>.*?'
    patron += '<span class="title">([^"]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,cantidad,scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = "%s (%s)" % (scrapedtitle,cantidad)
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<li><a class="pag-next" href="([^"]+)"><ins>Next</ins></a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = 'href="([^"]+)"\s*class="th-video.*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<span class="time">([^"]+)</span>.*?'
    patron += '<span class="title">([^"]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,duracion,scrapedtitle  in matches:
        url = scrapedurl
        contentTitle = scrapedtitle
        title = "[COLOR yellow]%s[/COLOR] %s" % (duracion, scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play" , title=title, url=url, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page = scrapertools.find_single_match(data,'<li><a class="pag-next" href="([^"]+)"><ins>Next</ins></a>')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '<video src="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url  in matches:
        url += "|Referer=%s" % host
        itemlist.append(item.clone(action="play", contentTitle=item.title, url=url))
    return itemlist

