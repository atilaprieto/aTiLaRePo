# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools


host = 'https://anibox.tv/'

perpage = 30


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []


    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'pelicula/estrenos/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Mejor valoradas', action = 'list_all', url = host + 'pelicula/mejor-valoradas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_episodes', url = host + 'series/novedades/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'series/mejor-valoradas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<article id="post-\d+" class="item ([^"]+)".*?><a href="([^"]+)"'
    patron += '.*?data-srcset="([^"]+)" class="lazyload" alt="([^"]+)".*?<p>(\d+)'

    matches = re.compile(patron).findall(data)

    num_matches = len(matches)

    for cat, url, thumb, title, year in matches[item.page * perpage:]:
        if not url or not title: continue

        if not item.search_type == "all":
            if item.search_type == "movie":
                if '/series/' in url: continue
            else:
                if '/pelicula/' in url: continue

        if '/pelicula/' in url:
            sufijo = '' if item.search_type != 'all' else 'movie'

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            sufijo = '' if item.search_type != 'all' else 'tvshow'

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year':year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
            buscar_next = False

    if buscar_next:
        if itemlist:
            next_url = scrapertools.find_single_match(data, '<div class="pagMovidy">\s*<a href="([^"]+)')
            if next_url:
                itemlist.append(item.clone( title = '>> Página siguiente', url = next_url, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie':
        url_generos = host + 'pelicula/'
    else:
        url_generos = host + 'series/'

    data = httptools.downloadpage(url_generos).data

    matches = re.compile('<li class="cfilter" data-type="genre" data-value="([^"]+)">.*?<b>([^<]+)').findall(data)

    url_generos = url_generos  + "/filtro/?genre="

    for genre_id, title in matches:
        url = url_generos + genre_id + "&year="

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    tope_year = 1985

    if item.search_type == 'movie':
        url_anios = host + 'pelicula/'
    else:
        url_anios = host + 'series/'

    url_anios = url_anios + '/filtro/?genre=&year='

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        itemlist.append(item.clone( title = str(x), url = url_anios + str(x), action = 'list_all' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    temporadas = re.compile('<div class="clickSeason[^"]+" data-season="(\d+)"', re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = int(tempo)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = int(tempo), page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda x: x.contentSeason)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, "<div class='se-c' data-season='%d'(.*?)<\/div><\/div>" % (item.contentSeason))

    patron = "<a href='([^']+)'><div class='imagen'>"
    patron += "<img src='([^']+)'><\/div>.*?<div class='epst'>([^<]+)"
    patron += "<\/div><div class='numerando'>([^<]+)"

    matches = re.compile(patron, re.DOTALL).findall(data)

    tot_epis = len(matches)

    all_epis = False

    if item.page == 0:
        if tot_epis > 100:
            if platformtools.dialog_yesno(config.__addon_name, 'La serie  ' + '[COLOR tan]' + item.contentSerieName + '[/COLOR] tiene [COLOR yellow]' + str(tot_epis) + '[/COLOR] episodios ¿ Desea cargarlos Todos de una sola vez ?'):
                color_infor = config.get_setting('notification_infor_color', default='pink')
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Cargando episodios[/B][/COLOR]' % color_infor)
                all_epis = True

    for url, thumb, titulo, name in matches[item.page * perpage:]:
        s_e = scrapertools.get_season_and_episode(name)
        season = int(s_e.split("x")[0])
        episode = s_e.split("x")[1]

        title = str(season) + 'x' + str(episode) + ' ' + titulo

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber=episode ))

        if not all_epis:
            if len(itemlist) >= perpage:
                break

    tmdb.set_infoLabels(itemlist)

    if not all_epis:
        if len(matches) > ((item.page + 1) * perpage):
            itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def last_episodes(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = httptools.downloadpage(item.url).data

    patron = '<article class="item se episodes" id="post-\d+" data-id="\d+">'
    patron += '<a href="([^"]+)"><div class="poster"><img src="[^"]+" data-srcset="([^"]+)" class="lazyload" alt="([^"]+)"'
    patron += '><div class="data"><h3><span>(\d+)\s*-\s*(\d+)</span>\s*([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)

    num_matches = len(matches)

    for url, thumb, titulo, season, episode, contentTitle in matches[item.page * perpage:]:
        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSerieName = contentTitle, contentSeason = season, contentEpisodeNumber=episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    # Subpaginación interna y/o paginación de la web
    buscar_next = True
    if num_matches > perpage: # subpaginación interna dentro de la página si hay demasiados items
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
            buscar_next = False

    if buscar_next:
        if itemlist:
            next_url = scrapertools.find_single_match(data, '<div class="pagMovidy">\s*<a href="([^"]+)')
            if next_url:
                itemlist.append(item.clone( title = '>> Página siguiente', url = next_url, action = 'last_episodes', page = 0, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'0': 'Lat', '1': 'Esp', '2': 'Vose'}

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    items_patron = "<li class=\"dooplay_player_option\" data-type='([^']+)' data-post='(\d+)' data-nume='(\d+)'"
    items_matches = re.compile(items_patron, re.DOTALL).findall(data)

    for datatype, datapost, datanume in items_matches:
        if not datatype or not datapost or not datanume: continue

        post = {'action': 'doo_player_ajax', 'post': datapost, 'nume': datanume, 'type': datatype}
        data = httptools.downloadpage("%swp-admin/admin-ajax.php" % host, post = post, headers = {'Referer': item.url}).data

        url = scrapertools.find_single_match(data, "src='([^']+)")
        if not url: url = scrapertools.find_single_match(data, 'src="(.*?)"')
        if not url: continue

        serversdata = httptools.downloadpage(url, headers = {"referer": item.url}).data
        if not serversdata: continue

        matches = re.compile(r'<li onclick=.*?data-lang="(.*?)".*?data-r="(.*?)"').findall(serversdata)

        if not matches:
            if '/hqq.' in url or '/waaw.' in url: url = ''

            if url:
                other = ''
                if '.animekao.club/embed' in url: other = 'kplayer'
                elif 'kaodrive/embed.php' in url: other = 'amazon'
                elif 'hydrax.com' in url: other = 'hydrax'
                elif '.xyz/v/' in url: other = 'fembed'

                if other == '':
                    other = servertools.get_server_from_url(url)
                    other = servertools.corregir_servidor(other)

                itemlist.append(Item( channel = item.channel, action = 'play', server = '', title = '', url = url, other = other.capitalize() ))
                return itemlist

        for lang, b64url in matches:
            url = base64.b64decode(b64url)
            if isinstance(url, bytes):
                url = url.decode('utf-8')

            if '/hqq.' in url or '/waaw.' in url: url = ''

            if url:
                other = ''
                if '.animekao.club/embed' in url: other = 'kplayer'
                elif 'kaodrive/embed.php' in url: other = 'amazon'
                elif 'hydrax.com' in url: other = 'hydrax'
                elif '.xyz/v/' in url: other = 'fembed'

                if other == '':
                    other = servertools.get_server_from_url(url)
                    other = servertools.corregir_servidor(other)

                itemlist.append(Item( channel = item.channel, action = 'play', server = '', title = '', url = url,
                                      language = IDIOMAS.get(lang, lang), other = other.capitalize() ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '.animekao.club/embed' in url:
        from lib import jsunpack
        sdata = httptools.downloadpage(url).data

        d = scrapertools.find_single_match(sdata, '(?s)<script type="text\/javascript">(eval.*?)<\/script>')
        pack = jsunpack.unpack(d)

        file = scrapertools.find_single_match(pack, '"file":"([^"]+)"')
        urlserver = 'https://kplayer.animekao.club/' + file

        url = file

        if not 'https://' in file:
            try:
               url = httptools.downloadpage(urlserver, follow_redirects=False).headers['location']
            except:
               pass

    elif 'kaodrive/embed.php' in url:
         data = httptools.downloadpage(url).data
         shareId = scrapertools.find_single_match(data, 'var shareId = "([^"]+)')
         url = 'https://www.amazon.com/drive/v1/shares/%s?resourceVersion=V2&ContentType=JSON&asset=ALL' %(shareId)

    elif 'hydrax.com' in url:
         slug = url.split('v=')[1]
         post = "slug=%s&dataType=mp4" % slug
         try:
            data = httptools.downloadpage("https://ping.iamcdn.net/", post=post).data
         except:
            url = ''

    elif '.xyz/v/' in url:
         url = url.replace('serieskao.xyz/v/', 'femax20.com/v/').replace('animekao.xyz/v/', 'femax20.com/v/').replace('sypl.xyz/v/', 'femax20.com/v/')
         if '#' in url:
             url = url.split('#')[0]

    if '/hqq.' in url or '/waaw.' in url: url = ''

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)
        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
