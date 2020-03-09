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

host = 'https://netfapx.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/?orderby=newest"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/?orderby=popular"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "/?orderby="))
    itemlist.append( Item(channel=item.channel, title="PornStar" , action="catalogo", url=host + "/pornstar/?orderby=popular"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<article class=pinbox>.*?'
    patron += 'href=([^>]+).*?'
    patron += 'src=([^\s]+).*?'
    patron += 'alt="([^"]+)".*?'
    patron += 'title=Videos>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle, cantidad in matches:
        title = "%s (%s)" %(scrapedtitle,cantidad)
        thumbnail = scrapedthumbnail
        url = scrapedurl.replace("pornstar", "videos")
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, '<link rel=next href=([^<]+)>')
    if next_page:
        next_page =next_page.replace("\"", "")
        itemlist.append( Item(channel=item.channel, action="catalogo", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    data = scrapertools.find_single_match(data, '<div class=cat-thumb>(.*?)</div>')
    patron = '<a href=([^<]+)><img src=([^<]+)>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail in matches:
        title = scrapertools.find_single_match(scrapedurl, 'category/(.*?)/')
        thumbnail = scrapedthumbnail
        url = scrapedurl
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<article class=pinbox>.*?'
    patron += 'href=([^>]+).*?'
    patron += 'src=([^\s]+).*?'
    patron += 'alt="([^"]+)".*?'
    patron += 'title=Duration>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,time in matches:
        time = time.strip()
        title = "[COLOR yellow]%s[/COLOR] %s" % (time, scrapedtitle)
        thumbnail = scrapedthumbnail
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<link rel=next href=([^<]+)>')
    if not next_page:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" class=next>Next')
    if next_page:
        next_page =next_page.replace("\"", "")
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    url = scrapertools.find_single_match(data, 'source:"([^"]+)"')
    itemlist.append(item.clone(action="play", title = url, url=url))
    return itemlist

