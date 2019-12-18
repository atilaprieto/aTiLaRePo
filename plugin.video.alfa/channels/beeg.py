# -*- coding: utf-8 -*-

import re
import urllib

from core import jsontools as json
from core import scrapertools
from core.item import Item
from platformcode import logger
from core import httptools


url_api = ""
Host = "https://beeg.com"


def get_api_url():
    global url_api
    data = httptools.downloadpage(Host).data
    version = re.compile('var beeg_version = ([\d]+)').findall(data)[0]
    url_api = Host + "/api/v6/" + version    # https://beeg.com/api/v6/1568386822920/


get_api_url()


def mainlist(item):
    logger.info()
    get_api_url()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="videos", title="Útimos videos", url=url_api + "/index/main/0/pc",
                         viewmode="movie"))
    itemlist.append(Item(channel=item.channel, action="canal", title="Canal",
                        url=url_api + "/channels"))
    itemlist.append(Item(channel=item.channel, action="listcategorias", title="Categorias",
                         url=url_api + "/index/main/0/pc", extra="nonpopular"))
    itemlist.append(
        Item(channel=item.channel, action="search", title="Buscar"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = url_api + "/index/tag/0/pc?tag=%s" % (texto)
    
    try:
        return videos(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def videos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    JSONData = json.load(data)
    for Video in JSONData["videos"]:
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
        th2= Video['thumbs']
        image= scrapertools.find_single_match(str(th2),"'image': '([^']+)'")
        thumbnail = "http://img.beeg.com/264x198/4x3/%s" %image
        url = '%s/video/%s?v=2' % (url_api, Video['svid'])
        title = Video["title"]
        title = "[COLOR yellow]" + duration + "[/COLOR] " + title
        itemlist.append(
            Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail, plot="", 
                 folder=True, contentType="movie"))
    # Paginador
    Actual = int(scrapertools.find_single_match(item.url, url_api + '/index/[^/]+/([0-9]+)/pc'))
    if JSONData["pages"] - 1 > Actual:
        scrapedurl = item.url.replace("/" + str(Actual) + "/", "/" + str(Actual + 1) + "/")
        itemlist.append(
            Item(channel=item.channel, action="videos", title="Página Siguiente", url=scrapedurl, thumbnail="",
                 viewmode="movie"))
    return itemlist


def listcategorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    JSONData = json.load(data)
    for Tag in JSONData["tags"]:
        url = url_api + "/index/tag/0/pc?tag=" + Tag["tag"]
        url = url.replace("%20", "-")
        title = '%s (%s)' % (str(Tag["tag"]), str(Tag["videos"]))
        itemlist.append(
            Item(channel=item.channel, action="videos", title=title, url=url, viewmode="movie", type="item"))
    return itemlist


def canal(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    JSONData = json.load(data)
    for Tag in JSONData["channels"]:
        url = url_api + "/index/channel/0/pc?channel=" + Tag["channel"]
        url = url.replace("%20", "-")
        title = '%s (%s)' % (str(Tag["ps_name"]), str(Tag["videos"]))
        itemlist.append(
            Item(channel=item.channel, action="videos", title=title, url=url, viewmode="movie", type="item"))
    return itemlist

def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    JSONData = json.load(data)
    for key in JSONData:
        videourl = re.compile("([0-9]+p)", re.DOTALL).findall(key)
        if videourl:
            videourl = videourl[0]
            if not JSONData[videourl] == None:
                url = JSONData[videourl]
                url = url.replace("{DATA_MARKERS}", "data=pc.ES")
                if not url.startswith("https:"): url = "https:" + url
                title = videourl
                itemlist.append(["%s %s [directo]" % (title, url[-4:]), url])
    itemlist.sort(key=lambda item: item[0])
    return itemlist

