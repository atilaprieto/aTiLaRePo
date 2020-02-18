# -*- coding: utf-8 -*-

import re
import urlparse

from core import httptools
from core import scrapertools
from core import servertools
from platformcode import logger

host = 'http://www.eporner.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Últimos videos", action="videos", url=host + "/0/"))
    itemlist.append(item.clone(title="Más visto", action="videos", url=host + "/most-viewed/"))
    itemlist.append(item.clone(title="Mejor valorado", action="videos", url=host + "/top-rated/"))
    itemlist.append(item.clone(title="Pornstars", action="pornstars", url=host + "/pornstars/"))
    itemlist.append(item.clone(title="      Alfabetico", action="pornstars_list", url=host + "/pornstars/"))
    itemlist.append(item.clone(title="Categorias", action="categorias", url=host + "/categories/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = host + "/search/%s/" % texto
    try:
        return videos(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def pornstars_list(item):
    logger.info()
    itemlist = []
    for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        itemlist.append(item.clone(title=letra, url=urlparse.urljoin(item.url, letra), action="pornstars"))
    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div class="mbprofile">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)">.*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<div class="mbtim"><span>Videos: </span>([^<]+)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, title, thumbnail, count in matches:
        itemlist.append(
            item.clone(title="%s (%s videos)" % (title, count), url=urlparse.urljoin(item.url, url), action="videos",
                       thumbnail=thumbnail))
    # Paginador           
    next_page = scrapertools.find_single_match(data,"<a href='([^']+)' class='nmnext' title='Next page'>")
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="pornstars", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<span class="addrem-cat">.*?'
    patron += '<a href="([^"]+)" title="([^"]+)">.*?'
    patron +='<div class="cllnumber">([^<]+)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, title, cantidad in matches:
        url = urlparse.urljoin(item.url, url)
        title = title + " " + cantidad
        thumbnail = ""
        if not thumbnail:
            thumbnail = scrapertools.find_single_match(data,'<img src="([^"]+)" alt="%s"> % title')
        itemlist.append(item.clone(title=title, url=url, action="videos", thumbnail=thumbnail))
    return sorted(itemlist, key=lambda i: i.title)


def videos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div class="mvhdico"><span>([^<]+)</span>.*?'
    patron += 'src="([^"]+.jpg)".*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += 'class="mbtim">([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for quality, thumbnail, url, title, duration in matches:
        title = "[COLOR yellow]" + duration + "[/COLOR] " + "[COLOR red]" + quality + "[/COLOR] " +title
        itemlist.append(item.clone(title=title, url=urlparse.urljoin(item.url, url),
                                   action="play", thumbnail=thumbnail, contentThumbnail=thumbnail,
                                   contentType="movie", contentTitle=title))
    # Paginador
    next_page = scrapertools.find_single_match(data,"<a href='([^']+)' class='nmnext' title='Next page'>")
    if next_page!="":
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="videos", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def play(item):
    logger.info(item)
    itemlist = servertools.find_video_items(item.clone(url = item.url, contentTitle = item.title))
    return itemlist

