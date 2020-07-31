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

host = 'http://www.gameofporn.net'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "/videos/1"))
    itemlist.append(item.clone(title="Top" , action="lista", url=host + "/top-videos"))
    itemlist.append(item.clone(title="New PornStar" , action="categorias", url=host + "/pornstars"))
    itemlist.append(item.clone(title="Top PornStar" , action="categorias", url=host + "/pornstars?sort=rank"))

    itemlist.append(item.clone(title="Sitios" , action="categorias", url=host))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search.html?q=%s" % (host, texto)
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
    if "Sitios" in item.title:
        data= scrapertools.find_single_match(data, '<li>Porn Categories</li>(.*?)<li>NEWEST</li>')
        patron = '<a href="([^"]+)" title="([^"]+)">(.*?)</a>'
    else:
        patron = '<div  class="bx".*?'
        patron += '<a href="([^"]+)".*?'
        patron += '<img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle
        if "Sitios" in item.title:
            title = scrapedthumbnail
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=plot) )
    if "Sitios" in item.title:
        itemlist.sort(key=lambda x: x.title)
    next_page = scrapertools.find_single_match(data, '<a class="current".*?<a class="" href="([^"]+)">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if "videos" in item.url:
        data= scrapertools.find_single_match(data, '<div class="thumblist" style="margin-left:17px;(.*?)alt="Next Page">')
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div  class="bx".*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=scrapedurl,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = scrapedtitle))
    next_page = scrapertools.find_single_match(data, '<a class="current".*?<a class="" href="([^"]+)">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    matches =scrapertools.find_single_match(data,'onClick="toplay\((.*?)\)')
    matches = matches.replace("'", "")
    link = matches.split(",")
    url = "http://www.gameofporn.net/ajax.php?page=video_play&thumb=%s&theme=%s&video=%s&id=%s&catid=%s&tip=%s&server=%s" % (link[0],link[1],link[2],link[3],link[4],link[5],link[6])
    headers = {'Referer': item.url, 'X-Requested-With': 'XMLHttpRequest'}
    data = httptools.downloadpage(url, headers=headers).data
    url = scrapertools.find_single_match(data,'<iframe src="([^"]+)"')
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

