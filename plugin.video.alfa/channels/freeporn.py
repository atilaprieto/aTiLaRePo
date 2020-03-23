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

host = 'https://frprn.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevas" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "/top-rated/"))
    itemlist.append( Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "/longest/"))
    itemlist.append( Item(channel=item.channel, title="Modelos" , action="categorias", url=host + "/models/most-popular/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = "%s/search/%s/?mode=async&action=get_block&block_id=list_videos_videos&from2=%s&fromStart=1&fromEnd=%s" % (host, texto,1,1)
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
    patron  = '<li class="thumb thumb-\w+">.*?'
    patron += '<a href="([^"]+)">.*?'
    patron += '<img class="lazy" data-original="([^"]+)".*?'
    patron += '<div class="title">(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedplot = ""
        title = scrapertools.find_single_match(scrapedtitle,'<div class="text">([^<]+)<')
        if "/categories/" in item.url:
            cantidad = scrapertools.find_single_match(scrapedtitle,'<div class="count">(\d+)</div>')
            scrapedtitle = scrapertools.find_single_match(scrapedtitle,'<div class="name">([^<]+)</div>')
            title = "%s (%s)" %(scrapedtitle, cantidad)
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail,  plot=scrapedplot) )
    next_page = scrapertools.find_single_match(data,'<li class="pagination-next"><a href="([^"]+)">')
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<div class="thumb">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img class="lazy" data-original="([^"]+)" alt="([^"]+)".*?'
    patron += '<span class="duration">([^"]+)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,duracion  in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = "[COLOR yellow]%s[/COLOR] %s" % (duracion, scrapedtitle)
        contentTitle = title
        thumbnail = scrapedthumbnail
        plot = ""
        year = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, contentTitle = contentTitle))
    patron = 'data-from="([^"]+)" data-id="([^"]+)" data-total="([^"]+)" data-page="([^"]+)" data-url="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for dfrom,id,total,page,purl in matches:
        page = int(page)
        page += page
        next_page = "%s?action=get_block&block_id=%s&%s=%s" %(purl, id, dfrom, page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '<meta property="og:video" content="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl  in matches:
        itemlist.append(item.clone(action="play", title=item.title, url=scrapedurl))
    return itemlist

