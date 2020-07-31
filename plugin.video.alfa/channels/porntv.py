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

host = 'https://www.porntv.com'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "/videos/straight/all-recent.html"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "/videos/straight/all-view.html"))
    itemlist.append(item.clone(title="Mejor valorada" , action="lista", url=host + "/videos/straight/all-rate.html"))
    itemlist.append(item.clone(title="Mas popular" , action="lista", url=host + "/videos/straight/all-popular.html"))
    itemlist.append(item.clone(title="Mas largos" , action="lista", url=host + "/videos/straight/all-length.html"))
    

    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "")
    item.url = "%s/videos/straight/%s-recent.html" % (host, texto)
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
    patron = '<div class="item video-category".*?'
    patron += '<a href="([^"]+)".*?' 
    patron += 'src="([^"]+)".*?'
    patron += '>([^<]+)</a></h2>.*?'
    patron += '<h2>(\d+)</h2>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        title = "%s (%s)" %(scrapedtitle,cantidad)
        itemlist.append(item.clone(action="lista", title=title, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="item">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'src="([^"]+)" alt="([^"]+)"(.*?)'
    patron += '<span class="time">([^<]+)<.*?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,quality,scrapedtime in matches:
        title = "[COLOR yellow]%s[/COLOR] %s" % (scrapedtime,scrapedtitle)
        if "flag-hd" in quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (scrapedtime,scrapedtitle)
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=scrapedurl,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot, contentTitle = title))
                              
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class="next"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    data = scrapertools.find_single_match(data, 'sources: \[(.*?)\]')
    patron = 'file: "([^"]+)",.*?label: "([^"]+)",'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,quality in matches:
        itemlist.append([".mp4 %s" % quality, url])
    return itemlist


