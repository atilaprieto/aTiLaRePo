# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import jsontools as json

host = 'https://es.camsoda.com'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/api/v1/browse/online"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/api/v1/tags/index?page=1"))
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


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    patron = '"tag_slug":"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedtitle in matches:
        title = scrapedtitle
        thumbnail = ""
        url = "https://es.camsoda.com/api/v1/browse/tag-%s" % scrapedtitle
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    page = scrapertools.find_single_match(item.url, "(.*?)=\d+")
    current_page = scrapertools.find_single_match(item.url, ".*?=(\d+)")
    if current_page:
        current_page = int(current_page)
        current_page = current_page + 1
        next_page = "%s=%s" %(page,current_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
       
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    data = data.replace("\/", "/")
    patron = '"(//media.camsoda.com/thumbs/[^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail in matches:
        username = "guest_22596"
        title = scrapertools.find_single_match(scrapedthumbnail, '([A-z0-9-]+).jpg')
        url = "https://es.camsoda.com/api/v1/video/vtoken/%s?username=%s" % (title,username)
        if not scrapedthumbnail.startswith("https"):
            thumbnail = "https:%s" % scrapedthumbnail
        itemlist.append( Item(channel=item.channel, action="play", title=title, contentTitle=title, url=url,
                              thumbnail=thumbnail, fanart=thumbnail, plot=""))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    token = scrapertools.find_single_match(data, '"token":"([^"]+)"')
    server = scrapertools.find_single_match(data, '"edge_servers":\[(.*?)\],')
    server = server.replace("\"", "").split(",")
    dir = scrapertools.find_single_match(data, '"stream_name":"([^"]+)"')
    dir = dir.replace("\/", "/")
    if "vide" in server[0]:
        url = "https://%s/cam/mp4:%s_h264_aac_480p/chunklist_w206153776.m3u8?token=%s"  %(server[0],dir,token)
    else:
        url = "https://%s/%s_h264_aac_480p/tracks-v1a1/mono.m3u8?token=%s" %(server[0],dir,token)
    itemlist.append(item.clone(action="play", title=url, contentTitle = item.title, url=url))
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|<br/>", "", data)
    token = scrapertools.find_single_match(data, '"token":"([^"]+)"')
    server = scrapertools.find_single_match(data, '"edge_servers":\[(.*?)\],')
    server = server.replace("\"", "").split(",")
    dir = scrapertools.find_single_match(data, '"stream_name":"([^"]+)"')
    dir = dir.replace("\/", "/")
    if server =="":
        return False, "[%s] El video ha sido borrado o no existe" % server
    if "vide" in server[0]:
        url = "https://%s/cam/mp4:%s_h264_aac_480p/chunklist_w206153776.m3u8?token=%s"  %(server[0],dir,token)
    else:
        url = "https://%s/%s_h264_aac_480p/tracks-v1a1/mono.m3u8?token=%s" %(server[0],dir,token)
    itemlist.append(item.clone(action="play", title=url, contentTitle = item.title, url=url))
    return itemlist


