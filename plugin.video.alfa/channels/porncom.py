# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://www.porn.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host +"/videos?o=d"))
    itemlist.append( Item(channel=item.channel, title="Destacado" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/videos?o=v7"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/videos?o=r7"))
    itemlist.append( Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "/videos?o=f7"))
    itemlist.append( Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "/videos?o=l7"))
    itemlist.append( Item(channel=item.channel, title="Mas comentado" , action="lista", url=host + "/videos?o=m7"))
    itemlist.append( Item(channel=item.channel, title="PornStar" , action="categorias", url=host + "/pornstars"))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="categorias", url=host + "/channels"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/videos/search?q=%s" % texto
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
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|\\", "", data)
    if "Categorias" in item.title:
        data = scrapertools.find_single_match(data, '<h2>All Categories</h2>(.*?)<h2>')
    if "/channels" in item.url:
        patron = '<img src="([^"]+)" alt="[^"]+" class="channel-cover">.*?'
    else:
        patron = '<img src="([^"]+)".*?'
    patron += 'href="([^"]+)">([^<]+)<'
    patron += '(.*?)(?:<div class="item"|</section>)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail,scrapedurl,scrapedtitle,cantidad in matches:
        title = scrapedtitle 
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = scrapedthumbnail
        num = scrapertools.find_single_match(cantidad, '<div class="meta"><p>([^<]+)<')
        if num:
            title = "%s (%s)" % (scrapedtitle, num)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class="next">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="categorias", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>|amp;", "", data)
    patron = '<div class="thumb".*?'
    patron += '<a href="([^"]+)" title="([^"]+)".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '</picture>(.*?)<h3>.*?'
    patron += '<span>(\d+) min</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail,quality,time in matches:
        title = "[COLOR yellow]%s min[/COLOR] %s" % (time, scrapedtitle)
        if "HD" in quality:
            title = "[COLOR yellow]%s min[/COLOR] [COLOR red]HD[/COLOR] %s" % (time, scrapedtitle)
        thumbnail = scrapedthumbnail
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class="next">')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = 'id:"([^"]+)",url:"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for quality,url in matches:
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist

