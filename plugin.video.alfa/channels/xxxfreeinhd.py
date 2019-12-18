# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse
import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['vidlox']

host = 'https://watchxxxfreeinhd.com'


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/?filtre=date&cat=0"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/?display=tube&filtre=views"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "/?display=tube&filtre=rate"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "search.php?q=%s&language=en&search=Search" % texto
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
    patron = '<li class="border-radius-5 box-shadow">.*?src="([^"]+)".*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += '<span class="nb_cat border-radius-5">(\d+) videos</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedurl,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        title = scrapedtitle + " (" + cantidad + ")"
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<li class="border-radius-5 box-shadow">.*?'
    patron += '<img width="\d+" height="\d+" src="([^"]+)" class=.*?'
    patron += '<a href="([^"]+)" title="([^"]+)">.*?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = scrapedthumbnail + "|https://watchxxxfreeinhd.com/" 
        plot = ""
        itemlist.append( Item(channel=item.channel, action="findvideos", title=title, url=scrapedurl,
                              thumbnail=thumbnail, plot=plot, fanart=scrapedthumbnail ))
    next_page = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)"')
    if next_page:
        next_page =  urlparse.urljoin(item.url,next_page)
        if "?filtre=date&cat=0" in item.url: next_page += "?filtre=date&cat=0"
        elif "?display=tube&filtre=views" in item.url: next_page += "?display=tube&filtre=views"
        elif "?display=tube&filtre=rate" in item.url: next_page += "?display=tube&filtre=rate"
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    data = scrapertools.find_single_match(data,'<div class="video-embed">(.*?)<div class="views-infos">')
    patron = 'data-lazy-src="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl in matches:
        if "strdef" in scrapedurl: 
            url = decode_url(scrapedurl)
        else:
            url = scrapedurl
        if not "videoxseries" in scrapedurl: #netu
            itemlist.append( Item(channel=item.channel, action="play", title = "%s", contentTitle= item.title, url=url ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist


def decode_url(txt):
    import base64
    logger.info()
    itemlist = []
    data = httptools.downloadpage(txt).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    n = 2
    while n > 0:
        b64_url = scrapertools.find_single_match(data, '\(dhYas638H\("([^"]+)"\)')
        b64_url = base64.b64decode(b64_url + "=")
        b64_url = base64.b64decode(b64_url + "==")
        data = b64_url
        n -= 1
    url = scrapertools.find_single_match(b64_url, '<iframe src="([^"]+)"')
    url = httptools.downloadpage(url).url
    logger.debug (url)
    return url
