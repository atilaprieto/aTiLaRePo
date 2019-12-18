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

host = 'https://www.xozilla.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas", action="lista", url=host + "/latest-updates/"))
    itemlist.append(Item(channel=item.channel, title="Popular", action="lista", url=host + "/most-popular/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada", action="lista", url=host + "/top-rated/"))

    itemlist.append(Item(channel=item.channel, title="PornStar", action="categorias", url=host + "/models/"))
    itemlist.append(Item(channel=item.channel, title="Canal", action="categorias", url=host + "/channels/"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="categorias", url=host + "/categories/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search/%s/" % texto
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
    patron = '<a class="item" href="([^"]+)" title="([^"]+)">.*?'
    patron += '<img class="thumb" src="([^"]+)".*?'
    patron += '(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedthumbnail, cantidad in matches:
        scrapedplot = ""
        scrapedurl += "1/" 
        cantidad = scrapertools.find_single_match(cantidad, '(\d+) videos</div>')
        if cantidad:
            scrapedtitle += " (" + cantidad + ")"
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                             thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot))
    if not "models" in item.url:
        itemlist.sort(key=lambda x: x.title)

    next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    page = scrapertools.find_single_match(item.url, '([^"]+/)\d+/')
    if next_page != "#videos" and next_page != "":
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(item.clone(action="categorias", title="Página Siguiente >>", text_color="blue", url=next_page))
    if next_page == "#videos":
        next_page = scrapertools.find_single_match(data, 'from:(\d+)">Next</a>')
        next_page = page + next_page + "/"
        itemlist.append(item.clone(action="categorias", title="Página Siguiente >>", text_color="blue", url=next_page))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<a href="([^"]+)" class="item.*?'
    patron += 'data-original="([^"]+)".*?'
    patron += 'alt="([^"]+)".*?'
    patron += '<div class="duration">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle, duracion in matches:
        url = scrapedurl
        title = "[COLOR yellow]" + duracion + "[/COLOR] " + scrapedtitle
        contentTitle = title
        thumbnail = scrapedthumbnail
        plot = ""
        year = ""
        itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                             fanart=thumbnail, plot=plot, contentTitle=contentTitle))
    next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    page = scrapertools.find_single_match(item.url, '([^"]+/)\d+/')
    if next_page != "#videos" and next_page != "#search":
        next_page = urlparse.urljoin(item.url, next_page)
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page))
    if next_page == "#videos" or next_page == "#search":
        next_page = scrapertools.find_single_match(data, 'from:(\d+)">Next</a>')
        next_page = page + next_page + "/"
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if "video_url_text" in data:
        patron = '(?:video_url|video_alt_url[0-9]*):\s*\'([^\']+)\'.*?'
        patron += '(?:video_url_text|video_alt_url[0-9]*_text):\s*\'([^\']+)\''
    else:
        patron = '(?:video_url|video_alt_url[0-9]*):\s*\'([^\']+)\'.*?'
        patron += 'postfix:\s*\'([^\']+)\''
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,quality in matches:
        itemlist.append(['%s' %quality, url])
    return itemlist
