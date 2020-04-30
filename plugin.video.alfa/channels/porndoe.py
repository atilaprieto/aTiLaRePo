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

host = 'https://porndoe.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host +"/videos"))
    itemlist.append( Item(channel=item.channel, title="Exclusivos" , action="lista", url=host + "/category/74/premium-hd"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/videos?sort=views-down"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/videos?sort=likes-down"))
    itemlist.append( Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "/videos?sort=duration-down"))
    itemlist.append( Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/pornstars"))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/channels?sort=ranking"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search?keywords=%s" % (host,texto)
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|amp;", "", data)
    data = scrapertools.find_single_match(data, '<head>(.*?)<footer>')
    patron  = 'class="item">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for match in matches:
        scrapedurl = scrapertools.find_single_match(match,'href="([^"]+)"')
        thumbnail = scrapertools.find_single_match(match,'data-src="([^"]+)"')
        scrapedtitle = scrapertools.find_single_match(match,'data-src="[^"]+"\s+alt="([^"]+)"')
        quality = ""
        if "/category" in scrapedurl:
            quality = scrapertools.find_single_match(match,'<span class="count">([^<]+)<')
        if "/pornstars-profile" in scrapedurl:
            quality = scrapertools.find_single_match(match,'<span class="txt">([^<]+)<')
            quality = "(%s)" % quality
        title = "%s %s" % (scrapedtitle, quality)
        scrapedurl = scrapedurl.replace("https://letsdoeit.com", "")
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, '<li class="page page-mobile current">.*?href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = 'data-title="([^"]+)".*?'
    patron += 'ng-preview="([^"]+)-preview.mp4".*?'
    patron += 'data-src="([^"]+)".*?'
    patron += '<span class="txt">([^<]+)<(.*?)<\/span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedtitle,scrapedurl,scrapedthumbnail,time,quality in matches:
        time = time.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time, scrapedtitle)
        if "icon-hd" in quality or "icon-vr" in quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time, scrapedtitle)
        thumbnail = scrapedthumbnail
        url = scrapedurl
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li class="page page-mobile current">.*?href="([^"]+)"').replace("amp;", "")
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    for i in ["240p-400.mp4","360p-750.mp4","480p-1000.mp4","720p-hd-2500.mp4"]:
        url = "%s-%s" %(item.url, i)
        if "240p" in url: quality="240p"
        if "360p" in url: quality="360p"
        if "480p" in url: quality="480p"
        if "720p" in url: quality="720p"
        if "HD" in item.title and not "360p" in url:
            itemlist.append(['.mp4 %s' %quality, url])
        if not "HD" in item.title and not "480p" in url and not "720p" in url:
            itemlist.append(['.mp4 %s' %quality, url])
    return itemlist

