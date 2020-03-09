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

host = 'https://www.shameless.com'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/videos/1/"))
    # itemlist.append( Item(channel=item.channel, title="Mas popular" , action="lista", url=host + "/videos/popular/week/"))
    # itemlist.append( Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "/videos/rated/week/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/?q=%s" % (host, texto)
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
    patron = '<a href="(https://www.shameless.com/categories/[^"]+)".*?'
    patron += '<span itemprop="name">(.*?)</span> <sup>(.*?)</sup>.*?'
    patron += 'src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,cantidad,scrapedthumbnail in matches:
        scrapedplot = ""
        title = "%s %s " % (scrapedtitle,cantidad)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<div class="icnt.*?'
    patron += '<a href="([^"]+)".*?'
    patron += 'data-src="([^"]+)" alt="([^"]+)".*?'
    patron += '<div class="bg"></div>([^<]+)</time>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedtime in matches:
        title = "[COLOR yellow]%s[/COLOR] %s" %(scrapedtime, scrapedtitle)
        thumbnail = scrapedthumbnail + "|Referer=https://www.shameless.com/"
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=scrapedurl,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, 'class="active">.*?<a href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                              url=next_page) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '(?:video_url|video_alt_url[0-9]*):\s*\'([^\']+)\'.*?'
    patron += '(?:video_url_text|video_alt_url[0-9]*_text):\s*\'([^\']+)\''
    matches = scrapertools.find_multiple_matches(data, patron)
    for url, quality in matches:
        headers = {'Referer': item.url}
        url = httptools.downloadpage(url, headers=headers , follow_redirects=False, only_headers=True).headers.get("location", "")
        url += "|Referer=%s" % item.url
        itemlist.append([quality, url])
    return itemlist


