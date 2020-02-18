# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://0dayporn.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/videos?o=mr"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/videos?o=mv"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/videos?o=tr"))
    itemlist.append( Item(channel=item.channel, title="Mas largo" , action="lista", url=host + "/videos?o=lg"))
    itemlist.append( Item(channel=item.channel, title="Mas comentados" , action="lista", url=host + "/videos?o=md")) 
    itemlist.append( Item(channel=item.channel, title="Pornstar" , action="categorias", url=host + "/models?o=tr"))
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
    patron = 'col-sm-6.*?'
    patron += 'href="([^"]+)".*?'
    if "models" in item.url:
        patron += 'src="([^"]+)".*?'
        patron += '<span class="model-title.*?>([^<]+)</span>.*?'
        patron += '</i>([^<]+)</span>'
    else:
        patron += 'src="([^"]+)" title="([^"]+)".*?'
        patron += '<div class="float-right">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        thumbnail = urlparse.urljoin(host,scrapedthumbnail)
        title = "%s (%s)" %(scrapedtitle,cantidad)
        url = urlparse.urljoin(host,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, '<a class="page-link" href="([^"]+)" class="prevnext"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="categorias", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist

def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = 'col-sm-6.*?'
    patron += '<a href="([^"]+)".*?'
    patron += '<img src="([^"]+)" title="([^"]+)".*?'
    patron += '<div class="duration">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedtime in matches:
        if "HD" in scrapedtime:
            time= scrapedtime.replace('<span class="hd-text-icon">HD</span> ', '')
            quality = "HD"
        else:
            time = scrapedtime
        title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR]%s" % (time, quality, scrapedtitle)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = host + scrapedurl
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<a class="page-link" href="([^"]+)" class="prevnext"')
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
    patron = '<div class="video-embedded">.*?(?:src|SRC)="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url in matches:
        itemlist.append(item.clone(action="play", title= "%s", contentTitle= item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
