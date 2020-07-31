# -*- coding: utf-8 -*-
# -*- Channel AnimeJL -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re
import base64
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import logger
from channelselector import get_thumb
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urllib                               # Es muy lento en PY2.  En PY3 es nativo
else:
    import urllib


host = 'https://www.anime-jl.net/'

def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos Episodios", action="new_episodes",
                         thumbnail=get_thumb('new_episodes', auto=True), url=host))

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", thumbnail=get_thumb('all', auto=True),
                         url=host + 'animes'))

    itemlist.append(Item(channel=item.channel, title="Series", action="list_all",
                         thumbnail=get_thumb('tvshows', auto=True), url=host+'animes?type%5B%5D=1&order=default'))

    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all",
                         thumbnail=get_thumb('movies',auto=True), url=host + 'animes?type%5B%5D=2&order=default'))

    itemlist.append(
        Item(channel=item.channel, title="Buscar", action="search", thumbnail=get_thumb('search', auto=True),
             url=host + 'animes?q='))

    return itemlist


def get_source(url):
    logger.info()
    data = httptools.downloadpage(url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}|\(|\)', "", data)
    return data


def new_episodes(item):
    logger.info()

    itemlist = []

    data = get_source(item.url)
    data = scrapertools.find_single_match(data, "<h2>Últimos episodios agregados</h2>.*?</ul>")
    patron = "<li><a href='(.*?)' class.*?<img src='(.*?)' alt='(.*?)'></span><span class='Capi'>(.*?)</span>"

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedepi in matches:
        url = scrapedurl
        thumbnail = host+scrapedthumbnail
        title = '%s %s' % (scrapedtitle.replace('ver ', ''), scrapedepi)
        itemlist.append(Item(channel=item.channel, action='findvideos',
                             title=title,
                             url=url,
                             thumbnail=thumbnail,
                             contentSerieName=scrapedtitle,
                             ))

    return itemlist


def list_all(item):
    logger.info()

    itemlist = []

    data = get_source(item.url)
    patron = "<article class='Anime alt B'><a href='([^']+)'>.*?class=.*?<img src='([^']+)' alt='([^']+)'>"
    patron += "</figure><span class='Type' .*?>([^']+)</span>.*?star.*?<p>([^<]+)</p>"

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, type, plot in matches:
        url = scrapedurl
        thumbnail = host+scrapedthumbnail
        title = scrapedtitle
        type = type
        season = ''
        if 'season' in scrapedtitle.lower():
            season = scrapertools.find_single_match(scrapedtitle, 'season (\d+)')
            scrapedtitle = scrapertools.find_single_match(scrapedtitle, '(.*?) season')

        new_item = Item(channel=item.channel, action='episodios',
                        title=title,
                        url=url,
                        thumbnail=thumbnail,
                        plot=plot,
                        type=item.type,
                        infoLabels={}
                        )
        if type.lower() == 'anime':
            new_item.contentSerieName = scrapedtitle
            new_item.contentSeasonNumber = season
        else:
            new_item.contentTitle = scrapedtitle

        itemlist.append(new_item)

    # Paginacion
    next_page = scrapertools.find_single_match(data,
                                               "<li><a href='([^']+)'><span>&raquo;</span></a></li></ul>")
    if next_page != '':
        itemlist.append(Item(channel=item.channel,
                             action="list_all",
                             title=">> Página siguiente",
                             url=host+next_page,
                             thumbnail='https://s16.postimg.cc/9okdu7hhx/siguiente.png'
                             ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = get_source(item.url)
    patron = '\[(\d+),"([^"]+)","([^"]+)",[^]]+\]'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for epi_num, epi_url, epi_thumb in matches:
        title = 'Episodio %s' % epi_num
        url = item.url +'/'+ epi_url
        itemlist.append(Item(channel=item.channel, title=title, thumbnail=item.thumbnail, url=url,
                             action='findvideos'))
        if item.type.lower != 'anime' and len(itemlist) == 1:
            return findvideos(itemlist[0])
        else:
            return itemlist[::-1]


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    try:
        if texto != '':
            return list_all(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def findvideos(item):
    logger.info()

    itemlist = []

    data = get_source(item.url)
    patron = 'video\[\d+\] = \'<iframe.*?src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl in matches:
        enc_url = scrapertools.find_single_match(scrapedurl, r'hs=(.*)$')
        url = urllib.unquote(base64.b64decode(rot13(enc_url)))
        if url != '':
            itemlist.append(Item(channel=item.channel, title='%s', url=url, action='play'))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'anime':
            item.url = host
        itemlist = new_episodes(item)
        if itemlist[-1].title == '>> Página siguiente':
            itemlist.pop()
        return itemlist
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []


def rot13(s):
    d = {chr(i+c): chr((i+13) % 26 + c) for i in range(26) for c in (65, 97)}
    return ''.join([d.get(c, c) for c in s])
