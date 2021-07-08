# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www10.animeflv.cc/'

perpage = 30


def mainlist(item):
    return mainlist_anime(item)


def mainlist_anime(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'browse', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'browse?genres=all&year=all&status=all&order=1&Tipo=4',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'browse?genres=all&year=all&status=all&order=1&Tipo=2',
                                search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + 'browse?genres=all&year=all&status=all&order=1&Tipo=3',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por categorías', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = url = host + 'browse'

    data = httptools.downloadpage(url_cat).data

    matches = re.compile(r'<li class="tmp "><a><label class="radio"><input  type="radio" value="(\d+)" name="order" data-text="([^"]+)').findall(data)

    for categorie_id, title in matches:
        url = '%s?order=%s' %(url_cat, categorie_id)
        title = title.strip()

        itemlist.append(item.clone( action = "list_all", url = url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def generos(item):
    logger.info()
    itemlist = []

    url_genre = url = host + 'browse'

    data = httptools.downloadpage(url_genre).data

    matches = re.compile(r'a><label><input  class="genre-ids" value="([^"]+)".*?type="checkbox">([^<]+)').findall(data)

    for genre_id, title in matches:
        url = '%s?genres=%s' %(url_genre, genre_id)

        itemlist.append(item.clone( action = "list_all", url = url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    url_anio = url = host + 'browse'

    tope_year = 1989

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        itemlist.append(item.clone( title = str(x), url = '%s?year=%s' % (url_anio, str(x)), action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<article class="Anime alt[^"]+"><a href="([^"]+)">'
    patron += '<.*?img src="([^"]+)".*?h3 class="Title">([^<]+).*?<span class="Type ([^"]+).*?<p class="des">([^<]+)'

    matches = re.compile(patron).findall(data)

    num_matches = len(matches)

    for url, thumb, title, tipo, info in matches[item.page * perpage:]:
        if not url or not title: continue

        if tipo == "movie":
            itemlist.append(item.clone( action='findvideos', url=url if url.startswith('http') else host[:-1] + url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url=url if url.startswith('http') else host[:-1] + url, title=title, thumbnail=thumb, 
                                        contentType = 'tvshow', plot = info, contentSerieName = title, infoLabels={'year':'-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
            buscar_next = False

    if buscar_next:
        if itemlist:
            next_url = scrapertools.find_single_match(data, "li\s*class=selected><a href='[^']+.*?<\/li><li.*?<a href='([^']+)")
            if next_url:
                itemlist.append(item.clone( title = '>> Página siguiente', url = next_url if url.startswith('http') else item.url + next_url if not '?' in item.url else item.url.split('?')[0] + next_url,
                                            action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<h2>Últimos episodios</h2>(.*?)<h2>Últimos animes agregados</h2>')

    patron = '<a href="(.*?)".*?<img src="(.*?)".*?<span class="Capi">(.*?)</span>.*?class="Title">(.*?)</strong>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for url, thumb, episode, title in matches:
        episode = episode.replace('Episodio', 'epis.')

        title = episode + ' ' + title

        if url:
            itemlist.append(item.clone( action='findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title,
                                        thumbnail=thumb, contentType = 'episode'))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="fa-play-circle"><a href="([^"]+)"><.*?this.src=\'([^\']+).*?<p>([^<]+)', re.DOTALL).findall(data)

    tot_epis = len(matches)

    all_epis = False

    if item.page == 0:
        if tot_epis > 100:
            if platformtools.dialog_yesno(config.__addon_name, 'La serie  ' + '[COLOR tan]' + item.contentSerieName + '[/COLOR] tiene [COLOR yellow]' + str(tot_epis) + '[/COLOR] episodios ¿ Desea cargarlos Todos de una sola vez ?'):
                color_infor = config.get_setting('notification_infor_color', default='pink')
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Cargando episodios[/B][/COLOR]' % color_infor)
                all_epis = True

    i = 0

    for url, thumb, title in matches[item.page * perpage:]:
        i += 1

        itemlist.append(item.clone( action='findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title,
                                    thumbnail=thumb, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = i ))

        if not all_epis:
            if len(itemlist) >= perpage:
                break

    tmdb.set_infoLabels(itemlist)

    if not all_epis:
        if len(matches) > ((item.page + 1) * perpage):
            itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    if not all_epis:
        return itemlist
    else:
        return sorted(itemlist, key=lambda x: x.contentEpisodeNumber, reverse=True)


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = re.compile(r'<li role="presentation" data-video="([^"]+)" title="([^"]+)">\s*<a href="[^"]+', re.DOTALL).findall(data)

    if not matches:
        new_url = scrapertools.find_single_match(data, '<ul class="ListCaps" id="episodeList".*?a href="(.*?)"')
        if new_url:
            if not new_url.startswith('http'):
                new_url = host[:-1] + new_url

                data = httptools.downloadpage(new_url).data
                matches = re.compile(r'<li role="presentation" data-video="([^"]+)" title="([^"]+)">\s*<a href="[^"]+', re.DOTALL).findall(data)

    for url, server in matches:
        if not url: continue

        if '/hqq.' in url or '/waaw.' in url: continue

        if not url.startswith('http'):
            url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    servidor = item.server
    url = item.url

    if "/v/" in item.url:
        data = httptools.downloadpage(item.url).data
        if 'yandex.ru' in data:
            url = item.url.split('/v/')[0]
            item.url = item.url.replace(url, 'https://fembed.com')
            url = item.url

            servidor = servertools.get_server_from_url(url)
            url = servertools.normalize_url(servidor, url)

    if '/hqq.' in url or '/waaw.' in url: url = ''

    if url:
        if not url.startswith("http"):
            url = "https:" + url

        url = url.replace("\\/", "/")

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'browse?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

