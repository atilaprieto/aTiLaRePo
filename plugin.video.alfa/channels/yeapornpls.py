# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://yeapornpls.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/videos?o=mr"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/videos?o=mv"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/videos?o=tr"))
    itemlist.append( Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "/videos?o=lg"))
    itemlist.append( Item(channel=item.channel, title="Mas comentados" , action="lista", url=host + "/videos?o=md")) 
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/search/videos?search_query=%s" % texto
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
    patron = '<div class="col-sm-6.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'title="([^"]+)".*?'
    patron += '<span class="badge">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,cantidad in matches:
        thumbnail = ""
        title = "%s (%s)" %(scrapedtitle,cantidad)
        url = scrapedurl
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    return itemlist

def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = 'col-lg-4">.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)" title="([^"]+)".*?'
    patron += '<div class="duration">([^>]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,time in matches:
        title = "[COLOR yellow]%s[/COLOR] %s" % (time, scrapedtitle)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = scrapedurl
        logger.debug(url)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li class="active">.*?<a href="([^"]+)">\d+<')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="video-embedded"> <iframe width="100%" height="100%" src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url in matches:
        itemlist.append(item.clone(action="play", title= "%s", contentTitle= item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
