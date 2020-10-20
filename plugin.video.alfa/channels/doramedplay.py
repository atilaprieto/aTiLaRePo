# -*- coding: utf-8 -*-
# -*- Channel DoramedPlay -*-
# -*- BASED ON: Channel DramasJC -*-
# -*- Created for Alfa-addon -*-

import requests
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger
from channels import autoplay
from channels import filtertools


host = 'https://doramedplay.com/'

IDIOMAS = {'VOSE': 'VOSE', 'LAT':'LAT'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['okru', 'mailru', 'openload']

def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()
    itemlist.append(Item(channel=item.channel, title="Doramas", action="list_all", url=host+'tvshows/',
                         type="tvshows", thumbnail=get_thumb('tvshows', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Películas", action="list_all", url=host+'movies/',
                         type='movies', thumbnail=get_thumb('movies', auto=True)))
    
    # itemlist.append(Item(channel=item.channel, title="Generos", action="section",
    #                      url=host + 'catalogue', thumbnail=get_thumb('genres', auto=True)))

    # itemlist.append(Item(channel=item.channel, title="Por Años", action="section", url=host + 'catalogue',
    #                      thumbnail=get_thumb('year', auto=True)))

    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host+'?s=',
                               thumbnail=get_thumb('search', auto=True)))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def get_source(url):
    logger.info()
    data = httptools.downloadpage(url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return data


def list_all(item):
    logger.info()
    itemlist = []
    
    data = get_source(item.url)
    patron = '<article id="post-\d+.*?<img src="([^"]+)".*?<span class="icon-star.*?\/span>'
    patron += '\s?([^<]+)<\/div>.*?<h3><a href="([^"]+)">([^<]+)<.*?<span>([^<]+).*?<\/article>'
    patron += '.*?<div class=\"texto\">([^<]+)<.*?<\/article>'
    
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedthumbnail, scrapedrating, scrapedurl, scrapedtitle, scrapedyear, scrapedplot in matches:

        url = scrapedurl
        year = scrapedyear
        contentname = scrapedtitle
        title = '%s (%s) [%s]'%(contentname, scrapedrating, year)
        thumbnail = scrapedthumbnail
        new_item = Item(channel=item.channel,
                        title=title,
                        plot=scrapedplot,
                        url=url,
                        thumbnail=thumbnail,
                        infoLabels={'year':year}
                        )

        new_item.contentSerieName = contentname
        if item.type == 'tvshows':
            new_item.action = 'seasons'
        else:
            new_item.action = 'findvideos'
            
        itemlist.append(new_item)
    tmdb.set_infoLabels_itemlist(itemlist, False)

    #  Paginación
    url_next_page = scrapertools.find_single_match(data,"<span class=\"current\">.?<\/span>.*?<a href='([^']+)'")
    if url_next_page:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all'))
    return itemlist


def seasons(item):
    logger.info()
    
    itemlist = []
    data = get_source(item.url)

    patron = "<div id='seasons'>.*?>Temporada([^<]+)<i>([^<]+).*?<\/i>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    logger.info("hola mundo")
    for temporada, fecha in matches:
        title = 'Temporada %s (%s)' % (temporada.strip(), fecha)
        contentSeasonNumber = temporada.strip()
        item.infoLabels['season'] = contentSeasonNumber
        itemlist.append(item.clone(action='episodesxseason',
                                   title=title,
                                   contentSeasonNumber=contentSeasonNumber
                                   ))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'episodios':
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_serie_to_library",
                             extra="episodios",
                             contentSerieName=item.contentSerieName,
                             contentSeasonNumber=contentSeasonNumber
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

    itemlist = []
    season = item.contentSeasonNumber
    data = get_source(item.url)
    data = scrapertools.find_single_match(data, ">Temporada %s .*?<ul class='episodios'>(.*?)<\/ul>" % season)
    patron = "<a href='([^']+)'>([^<]+)<\/a>.*?<span[^>]+>([^<]+)<\/span>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    ep = 1
    for scrapedurl, scrapedtitle, fecha in matches:
        epi = str(ep)
        title = season + 'x%s - Episodio %s (%s)' % (epi, epi, fecha)
        url = scrapedurl
        contentEpisodeNumber = epi
        item.infoLabels['episode'] = contentEpisodeNumber
        itemlist.append(item.clone(action='findvideos',
                                    title=title,
                                    url=url,
                                    contentEpisodeNumber=contentEpisodeNumber,
                                    ))
        ep += 1
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    return itemlist

def findvideos(item):
    logger.info()

    itemlist = []
    data = get_source(item.url)
    post_id = scrapertools.find_single_match(data, "'https:\/\/doramedplay\.com\/\?p=(\d+)'")
    body = "action=doo_player_ajax&post=%s&nume=1&type=tv" % post_id

    source_headers = dict()
    source_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    source_headers["X-Requested-With"] = "XMLHttpRequest"
    source_headers["Referer"] = host
    source_result = httptools.downloadpage(host + "wp-admin/admin-ajax.php", post=body, headers=source_headers)
    
    # logger.info(source_result.json)
    if source_result.code == 200:
        source_json = source_result.json
        if source_json['embed_url']:
            source_url = source_json['embed_url']
            logger.info("source: " + source_url)
            DIRECT_HOST = "v.pandrama.com"
            if DIRECT_HOST in source_url:
                # logger.info(source_url)
                directo_result = httptools.downloadpage(source_url, headers={"Referer": item.url})
                directo_result = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", directo_result.data)
                metadata_url = scrapertools.find_single_match(directo_result, 'videoSources\":\[{\"file\":\"([^"]+)\"')
                metadata_url = re.sub(r'\\', "", metadata_url)
                metadata_url = re.sub(r'/1/', "/" + DIRECT_HOST + "/", metadata_url)
                metadata_url += "?s=1&d="
                # logger.info(metadata_url)
                # logger.info('metadata_url: ' + re.sub(r'\\', "", metadata_url))
                # get metadata_url
                logger.info(source_url)
                # metadata_headers = dict()
                # metadata_headers["Referer"] = source_url
                # metadata = httptools.downloadpage(metadata_url, headers=metadata_headers)
                # metadata = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", metadata.data)
                metadata = requests.get(metadata_url, headers={"Referer": source_url}).content
                # metadata = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", metadata)
                # Get URLs
                patron = "RESOLUTION=(.*?)http([^#]+)"
                video_matches = re.compile(patron, re.DOTALL).findall(metadata)
                for video_resolution, video_url in video_matches:
                    final_url = "http" + video_url
                    logger.info(final_url)
                    itemlist.append(Item(channel=item.channel, title='%s (' + video_resolution.strip() + ')', url=final_url, action='play'))
                # https://1/cdn/hls/9be120188fe6b91e70db037b674c686d/master.txt
            else:
                itemlist.append(Item(channel=item.channel, title='%s', url=source_json['embed_url'], action='play'))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server.capitalize())

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                 action="add_pelicula_to_library", extra="findvideos", contentTitle=item.contentTitle))


    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = get_source(item.url)

    patron = '<div class="result-item">.*?<div class="thumbnail.*?<a href="([^"]+)">'
    patron += '<img src="([^"]+)".*?<span class="([^"]+)".*?<div class="title">'
    patron += '<a href="[^"]+">([^<]+)<.*?<span class="year">([^<]+)<.*?<p>([^<]+)<'

    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtype, scrapedtitle, scrapedyear, scrapedplot in matches:
        # logger.info(scrapedurl)
        url = scrapedurl
        year = scrapedyear
        contentname = scrapedtitle
        title = '%s (%s) (%s)'%(contentname, scrapedtype, year)
        thumbnail = scrapedthumbnail
        new_item = Item(channel=item.channel,
                        title=title,
                        url=url,
                        thumbnail=thumbnail,
                        plot=scrapedplot,
                        type=scrapedtype,
                        action='list_all',
                        infoLabels={'year':year}
                        )

        new_item.contentSerieName = contentname
        if new_item.type == 'tvshows':
            new_item.action = 'seasons'
        else:
            new_item.action = 'findvideos'
        itemlist.append(new_item)

    # tmdb.set_infoLabels_itemlist(itemlist, True)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        return list_search(item)
    else:
        return []

