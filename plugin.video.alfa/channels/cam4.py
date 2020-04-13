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
from core import jsontools as json

host = 'https://www.cam4.com'

def mainlist(item):
    logger.info()
    itemlist = []
    all = "https://www.cam4.es/directoryCams?directoryJson=true&online=true&url=true&page=1"
    url1= "https://www.cam4.es/directoryCams?directoryJson=true&online=true&url=true&gender=female&broadcastType=female_group&broadcastType=solo&broadcastType=male_female_group&page=1"
    url2= "https://www.cam4.es/directoryCams?directoryJson=true&online=true&url=true&broadcastType=female_group&broadcastType=male_female_group&page=1"
    url3= "https://www.cam4.es/directoryCams?directoryJson=true&online=true&url=true&gender=male&broadcastType=male_group&broadcastType=solo&page=1"
    url4= "https://www.cam4.es/directoryCams?directoryJson=true&online=true&url=true&gender=shemale&page=1"

    itemlist.append( Item(channel=item.channel, title="Trending Cams" , action="lista", url=all))
    itemlist.append( Item(channel=item.channel, title="Females" , action="lista", url=url1))
    itemlist.append( Item(channel=item.channel, title="Couples" , action="lista", url=url2))
    itemlist.append( Item(channel=item.channel, title="Males" , action="lista", url=url3))
    itemlist.append( Item(channel=item.channel, title="Trans" , action="lista", url=url4)) 
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "")
    item.url = "https://www.cam4.es/directoryCams?directoryJson=true&online=true&url=true&showTag=%s&page=1" % texto
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|#038;", "", data)
    JSONData = json.load(data)
    for Video in  JSONData["users"]:
        title = Video["username"]
        pais = Video["countryCode"]
        thumbnail = Video["snapshotImageLink"]
        video_url = Video["hlsPreviewUrl"]
        title =  "%s (%s)" % (title,pais)
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=video_url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=plot, contentTitle = title))
    last_page= scrapertools.find_single_match(data,'<a href=".*?/latest/(\d+)"><div style="display:inline">Last<')
    page = scrapertools.find_single_match(item.url, "(.*?=)\d+")
    current_page = scrapertools.find_single_match(item.url, ".*?&page=(\d+)")
    if current_page:
        current_page = int(current_page)
        current_page += 1
        next_page = "%s%s" %(page,current_page)
    itemlist.append( Item(channel=item.channel, action="lista", title="Página Siguiente >>", text_color="blue", 
                          url=next_page) )
    return itemlist

