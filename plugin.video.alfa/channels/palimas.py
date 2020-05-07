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
from channels import filtertools
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['mixdrop']

host = 'https://palimas.tv/'

def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?do=recently-added&th=month"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?do=most-viewed&th=month"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?do=most-rated&th=month"))
    itemlist.append( Item(channel=item.channel, title="1080-4K" , action="lista", url=host + "?do=1080-4k"))
    itemlist.append( Item(channel=item.channel, title="Canal" , action="catalogo", url=host + "channels"))
    itemlist.append( Item(channel=item.channel, title="PornStar" , action="pornstar", url=host + "pornstars?do=most-rated"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categories"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "?query=%s" % texto
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
    patron = '<h3 class="middle-video-container-h3-dt">.*?'
    patron += '<a href="([^"]+)"><img src="([^"]+)".*?'
    patron += 'class="middle-video-container-aa-channels">([^<]+)<.*?'
    patron += '</i>([^<]+)<.*?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle, cantidad in matches:
        title = "%s (%s)" %(scrapedtitle,cantidad)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, "<li><a href='([^']+)' id='next_previous'")
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def pornstar(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<li><a href=\'([^\']+)\'><img src=\'([^\']+)\'.*?'
    patron += '>([^<]+)</a></h2>.*?'
    patron += '</i> ([^<]+) &'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle,cantidad in matches:
        title = "%s (%s)" %(scrapedtitle,cantidad)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, "<li><a href='([^']+)' id='next_previous'")
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="pornstar", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<li>\s*<a href="([^"]+)"><img src="([^"]+)".*?'
    patron += '>([^<]+)</a></h2>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '<h3 class="middle-video-container-h3-dt">.*?'
    patron += '<a href="([^"]+)"\s*><img src="([^"]+)".*?'
    patron += 'class="middle-video-container-aa">([^<]+)</a><h2>([^<]+)<.*?'
    patron += '</i>([^<]+)<.*?'
    patron += '</i>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedthumbnail,pornstar,scrapedtitle,quality,time in matches:
        time = time.strip()
        title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s - %s" % (time, quality, pornstar, scrapedtitle)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="findvideos", title=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, "<li><a href='([^']+)' id='next_previous'>Next")
    if not next_page:
            next_page = scrapertools.find_single_match(data, "<li><a href=\"([^\"]+)\" id='next_previous'>Next")
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    # se obtiene el player 1
    ref = item.url
    player_url = scrapertools.find_single_match(data, '<iframe id="viframe".*?src="([^"]+)"')
    player_data = httptools.downloadpage(player_url, headers={"referer": ref}).data
    url = scrapertools.find_single_match(player_data, '<iframe src="([^"]+)" scrolling="no".*?</iframe>')
    itemlist.append(item.clone(action="play", title="%s", contentTitle=item.title, url=url))
    # se obtienen el resto
    patron = 'class="fa fa-angle-right".*?<a href="(video\?id[^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for player in matches:
        player_url = "%s%s" % (host, player)
        ref = player_url
        player_data = httptools.downloadpage(player_url).data
        player_url = scrapertools.find_single_match(player_data, '<iframe id="viframe".*?src="([^"]+)"')
        player_data = httptools.downloadpage(player_url, headers={"referer": ref}).data
        url = scrapertools.find_single_match(player_data, '<iframe src="([^"]+)" scrolling="no".*?</iframe>')
        if not url:
            continue
        itemlist.append(item.clone(action="play", title="%s", contentTitle=item.title, url=url))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language, list_quality)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

