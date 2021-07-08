# -*- coding: utf-8 -*-

import sys, re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, jsontools


if sys.version_info[0] >= 3:
    from urllib.parse import quote
else:
    from urllib import quote

host = "https://es.pornhub.com/"

perpage = 30


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []


    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + "video", page=0 ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + 'channels', page=0 ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por tipo', action = 'tipo', url = host + 'videos'))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars', page=0 ))

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul id="videoCategory" class="nf-videos videos search-video-thumbs">(.*?)<\/ul')
    if not bloque:
        bloque = scrapertools.find_single_match(data, '<ul class="videos recommendedContainerLoseOne">(.*?)<\/ul')
    if not bloque:
        bloque = scrapertools.find_single_match(data, '<ul class="videos row-5-thumbs search-video-thumbs scrollLazyload js-videoPlaylist viewPlaylist" id="videoPlaylist">(.*?)<\/ul')
    if not bloque and 'viewChunked' in item.url:
        bloque = data
    if not bloque:
        bloque = scrapertools.find_single_match(data, 'class="videos search-video-thumbs(.*?)<div class="reset"></div>')

    patron = '<a href="([^"]+)" title="([^"]+)"class="[^"]+"[^<]+<imgsrc="([^"]+)"data-thumb_url = "([^"]+)'

    matches = re.compile(patron).findall(bloque)

    for url, title, thumb, thumb2 in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title,
                                    thumbnail = thumb if not 'base64' else thumb2, contentType = 'movie', contentTitle = title ))

    if itemlist:
        patron = '<li class="page_next"><a href="([^"]+)'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            next_url = next_url.replace('&amp;', '&')
        else:
            token = scrapertools.find_single_match(data, '<input type="hidden" name="token" value="([^"]+)')
            playlistId = scrapertools.find_single_match(data, '<input name="edit-pl-id" id="js-editPlaylistId" type="hidden" value="([^"]+)')
            if token and playlistId:
                next_url = 'https://es.pornhub.com/playlist/viewChunked?id=%s&token=%s&page=%s' % (playlistId, token, str(item.page + 1))

        if next_url:
            itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_all', page = item.page + 1, text_color = 'coral' ))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data

    data = re.findall(r';var qualityItems_(?:\d+|[A-Z|a-z])\s*=\s*(\[[^\]]+\])', data)[0]
    jdata = jsontools.load(data)

    for match in jdata:
        if not match['url'] or not match['id']: continue
        calidad = re.compile('(?i)(\d+p)').findall(match['id'])[0]

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = calidad, url = match['url'], language = 'VO' ))

    return itemlist


def tipo(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="leftPanel videos">(.*?)<\/div>')
    patron = '<a class="js-mixpanel" data-mixpanel-listing="" '
    patron += 'href="([^"]+)".*?><i class="[^"]+"><\/i>([^<]+)'

    matches = re.compile(patron).findall(bloque)

    for url, title in matches:
        if title == 'Canales': continue
        if title == 'Listas de videos':
            action = 'listas'
        else:
            action = 'list_all'

        itemlist.append(item.clone( action = action, url = url if url.startswith('http') else host[:-1] + url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def listas(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloques = scrapertools.find_multiple_matches(data, '<li id="playlist_\d+" class="full-width">(.*?)<\/li>')

    for bloque in bloques:
        patron = 'data-image="([^"]+)"/>.*?<a class="title " title="([^"]+)" href="([^"]+)"'
        matches = re.compile(patron).findall(bloque)
        for thumb, title, url in matches:
            itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb))

    if itemlist:
        patron = '<li class="page_next"><a href="([^"]+)'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            next_url = next_url.replace('&amp;', '&')
            itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'listas', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'categories').data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="headerSubMenu">(.*?)<\/ul')

    patron = '<li class="big video"><a class="js-mixpanel" data-mixpanel-listing="" '
    patron += 'href="([^"]+)".*? alt="([^"]+)"><img class="js-menuSwap" data-image="([^"]+)'

    matches = re.compile(patron).findall(bloque)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb ))

    return sorted(itemlist, key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul id="popularPornstars" class="videos row-5-thumbs popular-pornstar">(.*?)<\/ul>')

    patron = '<a class="js-mxp" data-mxptype="Pornstar" data-mxptext="([^"]+)" '
    patron += 'href="([^"]+)">.*?<span class="rank_number">(\d+).*?thumb_url="([^"]+)'

    matches = re.compile(patron).findall(bloque)

    for title, url, rank, thumb in matches:
        if not url.endswith('/videos'):
            url += '/videos'

        itemlist.append(item.clone( action = 'list_pornstarts_videos', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<nav id="mainMenuChannels">(.*?)<\/nav>')

    patron = '<a href="([^"]+)"><span>([^<]+)'

    matches = re.compile(patron).findall(data)

    for url, title in matches:
        if 'Explorar todos los canales' in title: continue

        itemlist.append(item.clone( action = 'list_channels', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def list_channels(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<li class="wrap"><div class="channelsWrapper clearfix"><div class="imgWrapper">'
    patron += '<a href="([^"]+)".*?<imgalt="([^"]+)".*?thumb_url="([^"]+)'

    matches = re.compile(patron).findall(data)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action = 'list_channels_categories', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb ))

    if itemlist:
        patron = '<li class="page_next"><a href="([^"]+)'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            next_url = next_url.replace('&amp;', '&')

            itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_channels', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def list_channels_categories(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="floatLeft"><h2>([^<]+)</h2></div>'
    patron += '<div class="floatRight"><a class="seeAllButton greyButton light" href="([^"]+)'

    matches = re.compile(patron).findall(data)

    for title, url in matches:
        if 'premium' in title: continue

        itemlist.append(item.clone( action = 'list_channels_videos', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return itemlist


def list_channels_videos(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="videos row-5-thumbs videosGridWrapper" id="showAllChanelVideos">(.*?)<\/ul>')
    patron = '<a href="([^"]+)" title="([^"]+)"class="[^"]+"[^<]+<imgsrc="([^"]+)"data-thumb_url = "([^"]+)'

    matches = re.compile(patron).findall(bloque)

    for url, title, thumb, thumb2 in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb if not 'base64' else thumb2, contentType = 'movie', contentTitle = title ))

    if itemlist:
        patron = '<li class="page_next"><a href="([^"]+)'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            next_url = next_url.replace('&amp;', '&')
            itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_channels_videos', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def list_pornstarts_videos(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div id="profileContent" class="claimed profileVideos">(.*?)<div class="reset"><\/div>')
    patron = '<a href="([^"]+)" title="([^"]+)"class="[^"]+"[^<]+<imgsrc="([^"]+)"data-thumb_url = "([^"]+)'

    matches = re.compile(patron).findall(bloque)

    for url, title, thumb, thumb2 in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title,
                                    thumbnail = thumb if not 'base64' else thumb2, contentType = 'movie', contentTitle = title ))

    if itemlist:
        patron = '<li class="page_next"><a href="([^"]+)'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            next_url = next_url.replace('&amp;', '&')

            itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_pornstarts_videos', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "video/search?search=%s" % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
