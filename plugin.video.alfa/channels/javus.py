# -*- coding: utf-8 -*-
import urlparse
import re

from platformcode import config, logger
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from channels import filtertools
from channels import autoplay

IDIOMAS = {'vo': 'VO'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['bitp']

host = 'http://javuss.com'


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append( Item(channel=item.channel, title="Peliculas" , action="lista", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/?s=%s" % texto
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
    patron = '<a href="([^"]+)" title="([^"]+)" rel="nofollow" class="post-image post-image-left".*?\s*<div class="featured-thumbnail"><img width="203" height="150" src="([^"]+)" class="attachment-featured size-featured wp-post-image" alt="" title="" \/><\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        url = scrapedurl
        title = scrapedtitle.decode('utf-8')
        thumbnail = scrapedthumbnail
        fanart = ''
        itemlist.append(
            Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail))
    next_page = scrapertools.find_single_match(data,'<link rel="next" href="([^"]+)"')
    next_page = next_page.replace('"', '')
    if next_page!="":
        itemlist.append(item.clone(action="lista", title="Página Siguiente >>", text_color="blue", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist = servertools.find_video_items(item.clone(url = item.url, action='play', language='VO', contentTitle = item.title))
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist
