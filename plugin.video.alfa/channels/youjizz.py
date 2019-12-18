# -*- coding: utf-8 -*-
# ------------------------------------------------------------
import urlparse
import urllib2
import urllib
import re
import os
import sys
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://www.youjizz.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas", action="lista", url=host + "/newest-clips/1.html"))
    itemlist.append(Item(channel=item.channel, title="Popular", action="lista", url=host + "/most-popular/1.html"))
    itemlist.append(
        Item(channel=item.channel, title="Mejor valorada", action="lista", url=host + "/top-rated-week/1.html"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search/%s-1.html" % texto
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
    data = scrapertools.find_single_match(data, '>Trending Categories<(.*?)</ul>')
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<li><a href="([^"]+)">([^"]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapedtitle
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, plot=scrapedplot))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<div class="video-item">.*?'
    patron += 'class="frame image" href="([^"]+)".*?'
    patron += 'data-original="([^"]+)" />.*?'
    patron += '<div class="video-title">.*?'
    patron += '>(.*?)</a>.*?'
    patron += '<span class="time">(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle, duracion in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        title = "[COLOR yellow]" + duracion + "[/COLOR] " + scrapedtitle
        quality = ""
        if '-720-' in scrapedthumbnail:
            quality = "720"
        if '-1080-' in scrapedthumbnail:
            quality = "1080"
        if quality:
            title = "[COLOR yellow]" + duracion + "[/COLOR] " + "[COLOR red]" + quality + "p[/COLOR] " + scrapedtitle
        contentTitle = title
        thumbnail = "http:" + scrapedthumbnail
        plot = ""
        year = ""
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                             plot=plot, quality=quality, contentTitle=contentTitle))
    next_page = scrapertools.find_single_match(data, '<li><a class="pagination-next" href="([^"]+)">Next &raquo;</a>')
    if next_page != "":
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, 'var encodings(.*?)var')
    patron = '"quality":"(\d+)","filename":"([^"]+)",'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,scrapedurl in matches:
        url = "https:" + scrapedurl.replace("\\", "")
        itemlist.append(['%sp' %quality, url])
    return itemlist
