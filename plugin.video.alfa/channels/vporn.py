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

from core import jsontools as json
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools

host = 'https://www.vporn.com' #https://pornone.com/


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Novedades" , action="lista", url=host + "/newest/month/"))
    itemlist.append(item.clone(title="Mas Vistas" , action="lista", url=host + "/views/month/"))
    itemlist.append(item.clone(title="Mejor Valoradas" , action="lista", url=host + "/rating/month/"))
    itemlist.append(item.clone(title="Favoritas" , action="lista", url=host + "/favorites/month/"))
    itemlist.append(item.clone(title="Mas Votada" , action="lista", url=host + "/votes/month/"))
    itemlist.append(item.clone(title="Longitud" , action="lista", url=host + "/longest/month/"))
    itemlist.append(item.clone(title="PornStar" , action="catalogo", url=host + "/pornstars/"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search?q=%s" % (host, texto)
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
    patron = '<div class=\'star\'>.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)" alt="([^"]+)".*?'
    patron += '<span> (\d+) Videos'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        title = "%s (%s)" %(scrapedtitle,cantidad)
        url = "%s%s" %(host,scrapedurl)
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<a class="next" href="([^"]+)">')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '"name":"([^"]+)".*?'
    patron  += '<a href="([^"]+)".*?'
    patron  += '<span class="categoryCount">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedtitle,scrapedurl,cantidad in matches:
        title = "%s (%s)" %(scrapedtitle,cantidad)
        plot = ""
        thumbnail = "https://th-eu3.vporn.com/images/categories/%s.jpg" % scrapedtitle.lower()
        url = "%s%s" %(host,scrapedurl)
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<div class="video">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<span class="time">(.*?)</span>(.*?)</span>.*?'
    patron += '<img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,time,calidad,scrapedthumbnail,scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("&comma; ", " & ").replace("&lpar;", "(").replace("&rpar;", ")") 
        title = "[COLOR yellow]%s[/COLOR] %s" % (time, scrapedtitle)
        if "hd-marker is-hd" in  calidad:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time, scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(item.clone(action="play" , title=title , url=scrapedurl,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data,'<link rel="next" href="([^"]+)">')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '<source src="([^"]+)" type="video/mp4" label="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        itemlist.append(['%s' %quality, url])
    return itemlist

