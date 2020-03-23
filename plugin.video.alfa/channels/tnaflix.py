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
from core import tmdb
from core import jsontools

host = 'https://www.tnaflix.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevas" , action="peliculas", url=host + "/new/?d=all&period=all"))
    itemlist.append( Item(channel=item.channel, title="Popular" , action="peliculas", url=host + "/popular/?d=all&period=all"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorado" , action="peliculas", url=host + "/toprated/?d=all&period=month"))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "/channels/all/top-rated/1/all"))
    itemlist.append( Item(channel=item.channel, title="PornStars" , action="categorias", url=host + "/pornstars"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search.php?what=%s&tab=" % (host, texto)
    try:
        return peliculas(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '<div class="vidcountSp">(\d+)</div>.*?'
    patron  += '<a class="categoryTitle channelTitle" href="([^"]+)" title="([^"]+)">.*?'
    patron  += 'data-original="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for cantidad,scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        title = "%s (%s)" % (scrapedtitle,cantidad)
        scrapedplot = ""
        itemlist.append( Item(channel=item.channel, action="peliculas", title=title, url=scrapedurl,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail, plot=scrapedplot) )
    next_page_url = scrapertools.find_single_match(data,'<a class="llNav" href="([^"]+)">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append( Item(channel=item.channel , action="catalogo" , title="Página Siguiente >>" , text_color="blue", url=next_page_url , folder=True) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    if "pornstars" in item.url:
        data = scrapertools.find_single_match(data,'</i> Hall Of Fame Pornstars</h1>(.*?)</section>')
    patron  = '<a class="thumb" href="([^"]+)">.*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<div class="vidcountSp">(.*?)</div>.*?'
    patron += '<a class="categoryTitle".*?>([^"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,cantidad,scrapedtitle in matches:
        scrapedplot = ""
        if not scrapedthumbnail.startswith("https"):
            scrapedthumbnail = "https:%s" % scrapedthumbnail
        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
        if not scrapedurl.startswith("https"):
            scrapedurl = "https:%s" % scrapedurl
        if "profile" in scrapedurl:
            scrapedurl += "?section=videos"
        scrapedtitle = "%s (%s)" % (scrapedtitle,cantidad)
        itemlist.append( Item(channel=item.channel, action="peliculas", title=scrapedtitle , url=scrapedurl ,
                              fanart=scrapedthumbnail, thumbnail=scrapedthumbnail , plot=scrapedplot) )
    next_page_url = scrapertools.find_single_match(data,'<a class="llNav" href="([^"]+)">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append( Item(channel=item.channel , action="categorias" , title="Página Siguiente >>" , text_color="blue", url=next_page_url , folder=True) )
    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<a class=\'thumb no_ajax\' href=\'(.*?)\'.*?'
    patron += 'data-original=\'(.*?)\' alt="([^"]+)"><div class=\'videoDuration\'>([^<]+)</div>(.*?)<div class=\'watchedInfo'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,duracion,quality in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = "[COLOR yellow]%s[/COLOR] %s" % (duracion, scrapedtitle)
        if quality:
            quality= scrapertools.find_single_match(quality, '>(\d+p)<')
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (duracion, quality, scrapedtitle)
        contentTitle = title
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append(Item(channel=item.channel, action="play" , title=title , url=url, thumbnail=thumbnail,
                             fanart=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page_url = scrapertools.find_single_match(data,'<a class="llNav" href="([^"]+)">')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(item.clone(action="peliculas", title="Página Siguiente >>", text_color="blue", url=next_page_url) )
    return itemlist


def ref(url):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(url).data
    VID = scrapertools.find_single_match(data,'id="VID" type="hidden" value="([^"]+)"')
    vkey = scrapertools.find_single_match(data,'id="vkey" type="hidden" value="([^"]+)"')
    thumb = scrapertools.find_single_match(data,'id="thumb" type="hidden" value="([^"]+)"')
    nkey= scrapertools.find_single_match(data,'id="nkey" type="hidden" value="([^"]+)"')
    url = "https://cdn-fck.tnaflix.com/tnaflix/%s.fid?key=%s&VID=%s&nomp4=1&catID=0&rollover=1&startThumb=%s" % (vkey, nkey, VID, thumb)
    url += "&embed=0&utm_source=0&multiview=0&premium=1&country=0user=0&vip=1&cd=0&ref=0&alpha"
    return url


def play(item):
    logger.info()
    itemlist = []
    url= ref(item.url)
    headers = {'Referer': item.url}
    data = httptools.downloadpage(url, headers=headers).data
    patron = '<res>(.*?)</res>.*?'
    patron += '<videoLink><([^<]+)></videoLink>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for title, url in matches:
        url= url.replace("![CDATA[", "http:").replace("]]", "")
        itemlist.append([".mp4 %s" % (title), url])
    itemlist.reverse()
    return itemlist


