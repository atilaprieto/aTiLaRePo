# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = "https://caricaturashd.net/"


# ~ def item_configurar_proxies(item):
    # ~ plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    # ~ plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    # ~ return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

# ~ def configurar_proxies(item):
    # ~ from core import proxytools
    # ~ return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data
    # ~ data = httptools.downloadpage_proxy('caricaturashd', url, post=post, headers=headers, follow_redirects=follow_redirects).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    # ~ itemlist.append(item_configurar_proxies(item))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Catálogo', action = 'list_all', url = host + 'ultimas-peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_proxies(item))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Catálogo', action = 'list_all', url = host + 'ultimas-caricaturas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    # ~ itemlist.append(item_configurar_proxies(item))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(host)

    matches = scrapertools.find_multiple_matches(data, 'menu-item-object-category.*?<a href="(.*?)".*?>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url, genre = title ))

    itemlist.append(item.clone( action = 'list_all', title = 'Terror', url = host + 'terror/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Western', url = host + 'western/' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if item.genre:
        if not '?type=' in item.url:
            if item.search_type == 'movie':
                item.url = item.url + '?type=movies'
            else:
                item.url = item.url + '?type=series'

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article class="post dfx fcl movies">(.*?)</article>')

    for match in matches:
        title =  scrapertools.find_single_match(match, '<h2 class="entry-title text-center">(.*?)</h2>')
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')
        thumb if thumb.startswith('http') else "https:" + thumb

        tipo = 'movie' if '>Ver Película<' in match else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, genre = item.genre, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title,  infoLabels = {'year': '-'} ))

        if tipo == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, genre = item.genre, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if '>NEXT<' in data:
        next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?<a class="page-link".*?href="([^"]+)')

        if next_page:
            itemlist.append(item.clone( title = '>> Página siguiente', action='list_all', url = next_page, genre = item.genre, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    id_obj = scrapertools.find_single_match(data, ' data-object = "(.*?)"')
    if not id_obj: id_obj = scrapertools.find_single_match(data, ' data-object ="(.*?)"')
    if not id_obj: id_obj = scrapertools.find_single_match(data, ' data-object="(.*?)"')

    id_post = scrapertools.find_single_match(data, ' data-post="(.*?)"')

    if not id_obj or not id_post:
        return itemlist

    matches = scrapertools.find_multiple_matches(data, '<li class="sel-temp"><a data-post=".*?data-season="(.*?)"')

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.id_obj = id_obj
            item.id_post = id_post
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = season,
                                    id_obj = id_obj, id_post = id_post, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda i: i.contentSeason)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    url_post =  host + 'wp-admin/admin-ajax.php'
    season = item.contentSeason

    post = {"action": "action_select_season", "season": season, "post": item.id_post, "object": item.id_obj}
    data = do_downloadpage(url_post, post = post)

    matches = scrapertools.find_multiple_matches(data, '<article class="post dfx fcl movies">(.*?)</article>')

    if '<a class="page-numbers"' in data:
        pages = scrapertools.find_multiple_matches(data, '<a class="page-numbers".*?>(.*?)</a>')

        for page in pages:
            post = {"action": "action_pagination_ep", "page": page, "season": season, "object": item.id_obj}
            data = do_downloadpage(url_post, post = post)

            matches_page = scrapertools.find_multiple_matches(data, '<article class="post dfx fcl movies">(.*?)</article>')
            if matches_page:
                matches += matches_page

    for match in matches[item.page * perpage:]:
        title =  scrapertools.find_single_match(match, '<h2 class="entry-title text-center">(.*?)</h2>')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')
        thumb if thumb.startswith('http') else "https:" + thumb

        epis =  scrapertools.find_single_match(match, '<span class="year">' + str(item.contentSeason) + 'x(.*?)</span>').strip()

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb, 
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title = ">> Página siguiente", action = "episodios", page = item.page + 1, text_color='coral' ))

    return sorted(itemlist, key=lambda i: i.contentEpisodeNumber)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es': 'Esp', 'lat': 'Lat', 'sub': 'Vose', 'Latino': 'Lat', 'Castellano': 'Esp', 'Español': 'Esp', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    options = scrapertools.find_multiple_matches(data, 'data-opt=".*?options-(.*?)">.*?<span class="option">(.*?)</span>')

    for option, lang in options:
        lang = lang.split(" - ")[1]
        lang = lang.strip()

        url = scrapertools.find_single_match(data, '<div id="options-' + option + '.*?<iframe.*?src="(.*?)"')

        if url:
           url = url.replace('&#038;', '&').replace('&amp;', '&')

           if '&lt;IFRAME SRC=&quot;' in url:
               url = scrapertools.find_single_match(url, '&lt;IFRAME SRC=&quot;(.*?)&quot;')
           elif '/cinemaupload.com/' in url:
               url = scrapertools.find_single_match(url, 'src=&quot;(.*?)&quot;')

           servidor = servertools.get_server_from_url(url)
           servidor = servertools.corregir_servidor(servidor)

           # ~ los servidores casi siempre son falsos pone cinemaupload
           if host in url: servidor = ''
           elif '/cinemaupload.com/' in url: servidor = ''

           itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                language = IDIOMAS.get(lang,lang) ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server:
        itemlist.append(item.clone(server = item.server, url = item.url))

    elif item.url.startswith(host):
        resp = httptools.downloadpage(item.url, follow_redirects=False)

        if 'location' in resp.headers: 
            url = resp.headers['location']
        else:
            url = scrapertools.find_single_match(resp.data, '<div class="Video">.*?src="(.*?)"')
            if not url: url = scrapertools.find_single_match(resp.data, '<IFRAME SRC="(.*?)"')

        if url:
            if '/cinemaupload.com/' in url:
                url = url.replace('/cinemaupload.com/', '/embed.cload.video/')

                data = do_downloadpage(url)

                sitekey = scrapertools.find_single_match(data, 'data-sitekey="([^"]+)')
                if not sitekey:
                    url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
                    if url:
                        if '/download/' in url:
                           url = url.replace('//download/', '/files/').replace('/download/', '/files/')
                           itemlist.append(item.clone( url = url, server = 'directo' ))
                           return itemlist

                        elif '/manifest.mpd' in url:
                           if platformtools.is_mpd_enabled():
                              itemlist.append(['mpd', url, 0, '', True])
                           itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
                        else:
                           itemlist.append(['m3u8', url])
                        return itemlist

                # ~ return 'Opción aún sin desarrollar'
                response = recaptcha.get_recaptcha_response(sitekey, item.url)
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone(server = servidor, url = url))
    elif item.url.startswith('https://cinemaupload.com/'):
        item.url = item.url.replace('/cinemaupload.com/', '/embed.cload.video/')

        data = do_downloadpage(item.url)

        sitekey = scrapertools.find_single_match(data, 'data-sitekey="([^"]+)')
        if not sitekey:
            url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
            if url:
                if '/download/' in url:
                   url = url.replace('//download/', '/files/').replace('/download/', '/files/')
                   itemlist.append(item.clone( url = url, server = 'directo' ))
                   return itemlist

                elif '/manifest.mpd' in url:
                   if platformtools.is_mpd_enabled():
                       itemlist.append(['mpd', url, 0, '', True])
                   itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
                else:
                   itemlist.append(['m3u8', url])
                   return itemlist

        # ~ return 'Opción aún sin desarrollar'
        response = recaptcha.get_recaptcha_response(sitekey, item.url)
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    else:
        data = do_downloadpage(item.url)
        # ~ logger.debug(data)

        new_url = scrapertools.find_single_match(data, "location.href='([^']+)")
        if new_url:
            servidor = servertools.get_server_from_url(new_url)
            servidor = servertools.corregir_servidor(servidor)
            itemlist.append(item.clone(url = new_url, server = servidor))

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

