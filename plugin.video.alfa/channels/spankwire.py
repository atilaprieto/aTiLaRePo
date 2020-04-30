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

from core import jsontools as json
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://www.spankwire.com'
url_api = host + "/api/video/list.json?segment=Straight&limit=33&sortby="


# Error el Curl de kodi 18.4 quita .net//

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevas" , action="lista", url=url_api + "recent&page=1"))
    itemlist.append( Item(channel=item.channel, title="Mas Vistas" , action="lista", url=url_api + "views&period=Month&page=1"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorada" , action="lista", url=url_api + "rating&period=Month&page=1"))
    itemlist.append( Item(channel=item.channel, title="Longitud" , action="lista", url=url_api + "duration&period=Month&page=1"))
    itemlist.append( Item(channel=item.channel, title="Pornstar" , action="catalogo", url=host + "/api/pornstars?limit=48&sort=popular&page=1"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/api/categories/list.json?segmentId=0&limit=100&sort=abc&page=1"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/api/video/search.json?segment=Straight&limit=33&query=%s&page=1" % (host, texto)
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
    JSONData = json.load(data)
    for Video in  JSONData["items"]:
        title = Video["name"]
        id = Video["id"]
        cantidad = Video["videosNumber"]
        thumbnail = Video["image"]
        title =  "%s (%s)" % (title,cantidad)
        thumbnail = thumbnail.replace("\/", "/").replace(".webp", ".jpg")
        url =  "%srecent&category=%s&page=1" % (url_api, id)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot) )
    Actual = int(scrapertools.find_single_match(item.url, '&page=([0-9]+)'))
    if JSONData["pages"] - 1 > Actual:
        scrapedurl = item.url.replace("&page=" + str(Actual), "&page=" + str(Actual + 1))
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=scrapedurl))
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for Video in  JSONData["items"]:
        title = Video["name"]
        id = Video["id"]
        cantidad = Video["videos"]
        thumbnail = Video["thumb"]
        title =  "%s (%s)" % (title,cantidad)
        thumbnail = thumbnail.replace("\/", "/").replace(".webp", ".jpg")
        url = "%s/api/video/list.json?pornstarId=%s&limit=25&sortby=recent&page=1" % (host, id)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot) )
    Actual = int(scrapertools.find_single_match(item.url, '&page=([0-9]+)'))
    if JSONData["pages"] - 1 > Actual:
        scrapedurl = item.url.replace("&page=" + str(Actual), "&page=" + str(Actual + 1))
        itemlist.append(item.clone(action="catalogo", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=scrapedurl))
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for Video in  JSONData["items"]:
        segundos = Video["duration"]
        horas=int(segundos/3600)
        segundos-=horas*3600
        minutos=int(segundos/60)
        segundos-=minutos*60
        if segundos < 10:
            segundos = "0%s" %segundos
        if minutos < 10:
            minutos = "0%s" %minutos
        if horas == 00:
            duration = "%s:%s" % (minutos,segundos)
        else:
            duration = "%s:%s:%s" % (horas,minutos,segundos)
        id = Video["id"]
        title = Video["title"]
        thumbnail = Video["flipBookPath"]
        url = "https://www.spankwire.com/api/video/%s.json"  % id
        title = "[COLOR yellow]%s[/COLOR] %s" % (duration,title)
        thumbnail = thumbnail.replace("\/", "/").replace("{index}", "2")
        url = url.replace("\/", "/")
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, contentTitle = title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot))
    Actual = int(scrapertools.find_single_match(item.url, '&page=([0-9]+)'))
    if JSONData["pages"] - 1 > Actual:
        scrapedurl = item.url.replace("&page=" + str(Actual), "&page=" + str(Actual + 1))
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=scrapedurl))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    json_data = httptools.downloadpage(item.url).json
    url = json_data["HLS"]
    itemlist.append(["m3u", url])
    for quality, url in json_data["videos"].items():
        url = url.replace("%3D", "=").replace("%2B", "+")
        itemlist.append(['%s' %quality.replace("quality_", ""), url])
    return itemlist

