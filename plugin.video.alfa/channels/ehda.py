# -*- coding: utf-8 -*-
# -*- Channel Cine24h -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re
import sys
import urlparse

from channels import autoplay
from channels import filtertools
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import channeltools
from core import tmdb
from platformcode import config, logger
from channelselector import get_thumb
from lib import unshortenit



host = "https://elhogardelaprendiz.es/"



parameters = channeltools.get_channel_parameters("ehda")


fanart_host = parameters['fanart']
thumbnail_host = parameters['thumbnail']

IDIOMAS = {'Latino': 'LAT', 'Castellano': 'CAST'}
list_language = IDIOMAS.values()
list_quality = []
list_servers = ['uptobox', 'upstream', 'yourupload', 'cloudvideo']


def mainlist(item):
    logger.info()
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = [item.clone(title="Peliculas", action="menumovies", text_blod=True,
                           viewcontent='movies', viewmode="movie_with_plot", thumbnail=get_thumb('movies', auto=True)),

                item.clone(title="Series", action="list_all", extra='serie', url=host + "/series",
                           viewmode="movie_with_plot", text_blod=True, viewcontent='movies',
                           thumbnail=get_thumb('tvshows', auto=True), page=0),

                item.clone(title="Buscar", action="search", thumbnail=get_thumb('search', auto=True),
                           text_blod=True, url=host, page=0)]

    autoplay.show_option(item.channel, itemlist)
    return itemlist


def menumovies(item):
    logger.info()
    itemlist = [item.clone(title="Novedades", action="list_all", thumbnail=get_thumb('newest', auto=True),
                           text_blod=True, page=0, viewcontent='movies',
                           url=host + "/peliculas", viewmode="movie_with_plot"),

                item.clone(title="Estrenos 2019", action="peliculas", thumbnail=get_thumb('estrenos', auto=True),
                           text_blod=True, page=0, viewcontent='movies',
                           url=host + '?s=trfilter&trfilter=1&years%5B%5D=2019', viewmode="movie_with_plot"),
                                
                item.clone(title="Buscar", action="search", thumbnail=get_thumb('search', auto=True),
                           text_blod=True, url=host, page=0, extra='buscarP')]

    return itemlist


def search(item, texto):
    logger.info()

    texto = texto.replace(" ", "+")
    item.url = urlparse.urljoin(item.url, "?s={0}".format(texto))

    try:
        return list_all(item)

    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []


def list_all(item): 
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = '(?is)class="TPost C">.*?href="([^"]+)".*?'  # url
    patron += 'data-src="([^"]+)".*?>.*?'
    patron += 'Title">([^<]+)<.*?'
    patron += 'Year">([^<]+)<.*?'
    matches = scrapertools.find_multiple_matches(data, patron)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedyear in matches:

        new_item = Item(channel=item.channel, title=scrapedtitle, url=scrapedurl, action='findvideos',
                             thumbnail=scrapedthumbnail, infoLabels={})

        if "serie" in scrapedurl:
            new_item.contentSerieName = scrapedtitle
            new_item.action = 'seasons'
        else:
            new_item.contentTitle = scrapedtitle
            new_item.action = 'findvideos'
            new_item.infoLabels["year"] = scrapedyear

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)">')
    if next_page:
        itemlist.append(Item(channel=item.channel, url=next_page, title="[COLOR yellow]» Siguiente »[/COLOR]", action="list_all"))


    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url).data

    patron = 'data-tab="(\d+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    infoLabels = item.infoLabels
    for season in matches:
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action="episodesxseason",
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_serie_to_library",
                             extra="episodios",
                             contentSerieName=item.contentSerieName,
                             ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseason(tempitem)
    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = list()

    data = httptools.downloadpage(item.url).data

    season_block = scrapertools.find_single_match(data, 'data-tab="%s".*?</table>' % item.infoLabels["season"])
    patron = '"Num">(\d+)<.*?href="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(season_block)
    infoLabels = item.infoLabels
    for epi_num, url in matches:
        title = '%sx%s' % (infoLabels["season"], epi_num)
        infoLabels["episode"] = epi_num
        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos', infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist



def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|amp;|#038;|\(.*?\)|\s{2}|&nbsp;", "", data)
    data = scrapertools.decodeHtmlentities(data)
    patron = 'data-tplayernv="Opt(.*?)"><span>(.*?)</span>(.*?)</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for option, servername, quote in matches:
        patron = '<span>(.*?) -([^<]+)</span'
        match = re.compile(patron, re.DOTALL).findall(quote)
        lang, quality = match[0]
        quality = quality.strip()
        headers = {'Referer': item.url}
        url_1 = scrapertools.find_single_match(data,
                                               'id="Opt%s"><iframe width="560" height="315" src="([^"]+)"' % option)
        new_data = httptools.downloadpage(url_1, headers=headers).data
        new_data = re.sub(r"\n|\r|\t|amp;|\(.*?\)|\s{2}|&nbsp;", "", new_data)
        new_data = scrapertools.decodeHtmlentities(new_data)
        url2 = scrapertools.find_single_match(new_data, '<iframe width="560" height="315" src="([^"]+)"')
        url = url2
        if 'rapidvideo' in url2 or "verystream" in url2:
            url = url2

        lang = lang.lower().strip()
        languages = {'latino': '[COLOR cornflowerblue](LAT)[/COLOR]',
                     'español': '[COLOR green](CAST)[/COLOR]',
                     'subespañol': '[COLOR red](VOS)[/COLOR]',
                     'sub': '[COLOR red](VOS)[/COLOR]'}
        if lang in languages:
            lang = languages[lang]

        servername = servertools.get_server_from_url(url)

        title = "Ver en: [COLOR yellowgreen](%s)[/COLOR] [COLOR yellow](%s)[/COLOR] %s" % (
            servername.title(), quality, lang)

        itemlist.append(item.clone(action='play', url=url, title=title, language=lang, quality=quality))

    patron1 = 'href="([^>]+)" class="Button STPb">.*?<img src="([^>]+)".*?alt="Imagen (.*?)">.*?<span>(\d+)'
    matches1 = re.compile(patron1, re.DOTALL).findall(data)
    for url, img, lang, quality in matches1:
        if "ehda" in url or "short." in url:
            continue
        else:    
            url, c = unshortenit.unshorten_only(url)
            if "short." in url:
                continue
            elif "google." in url:
                for item in itemlist:
                    if "google." in item.url:
                        item.url = url
                    #logger.error("url=%s" % item.url)
    itemlist = servertools.get_servers_itemlist(itemlist)

    itemlist.sort(key=lambda it: it.language, reverse=False)


    itemlist = filtertools.get_links(itemlist, item, list_language)

    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'episodios':
        itemlist.append(Item(channel="ehda", url=item.url, action="add_pelicula_to_library", extra="findvideos",
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             thumbnail=thumbnail_host, contentTitle=item.contentTitle))

    return itemlist
