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
import base64

host = 'https://daftsex.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host, page=0))
    itemlist.append( Item(channel=item.channel, title="Hot" , action="lista", url=host + "/hottest")) 
    itemlist.append( Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/pornstars"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s/video/%s" % (host, texto)
    item.page=0
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
    if "pornstar" in item.url:
        patron = '<div class="pornstar">.*?'
    else:
        patron = '<div class="video-item">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title=scrapedtitle
        thumbnail = urlparse.urljoin(host,scrapedthumbnail)
        url = urlparse.urljoin(host,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="", page=0) )
    next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)" title="Next page">Next')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="categorias", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    logger.info("Intel11 %s" %item)
    page=item.page
    if item.next_page:
        page += 1
        post = "page=%s" %page
        logger.info("Intel33 %s" %post)
        data = httptools.downloadpage(item.url, post=post).data
    else:
        data = httptools.downloadpage(item.url).data
    logger.info("Intel22 %s" %page)
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<a href="([^"]+)" data-webm=.*?'
    patron += '<img src="([^"]+)" alt="([^"]+)".*?'
    patron += '<span class="video-time">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,time in matches:
        title = "[COLOR yellow]%s[/COLOR] %s" % (time, scrapedtitle)
        thumbnail = scrapedthumbnail
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<div class="(more)"')
    if not next_page:
        next_page = scrapertools.find_single_match(data, '<li><a href="([^"]+)" title="Next page">Next')
    if next_page:
        if "more" in next_page:
            itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                                  url=item.url, next_page="more", page=page) )
        else:
            next_page = urlparse.urljoin(host,next_page)
            itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page, page=page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    url = scrapertools.find_single_match(data, 'class="frame_wrapper">.*?src="([^"]+)"')
    headers = {'Referer': item.url}
    data = httptools.downloadpage(url, headers=headers).data
    server = scrapertools.find_single_match(data, 'thumb: "([^"]+)"')
    server = base64.b64decode(server).decode('utf-8').replace("/thumb.jpg", "")
    server = "https:%s" % server
    patron = '"mp4_\d+":"(\d+).([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        url = "%s/%s.mp4?extra=%s" %(server,quality,url)
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist

