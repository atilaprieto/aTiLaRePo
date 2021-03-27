# -*- coding: utf-8 -*-


import re


from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

host = 'https://inkapelis.me/'


def do_downloadpage(url, post=None, headers=None):
    raise_weberror = False if '/fecha/' in url else True

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


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

    itemlist.append(item.clone( title = 'Estrenos en HD', action = 'list_all', url = host + 'genero/estrenos-hd/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = host + 'genero/destacadas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'calidad/hd/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En cines', action = 'list_all', url = host + 'genero/cine/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos capítulos', action = 'last_episodes', url = host + 'episodio/' ))
    itemlist.append(item.clone( title = 'Últimas temporadas', action = 'last_seasons', url = host + 'temporada/' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/castellano/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/subtituladas/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'pelicula/')
    # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, '<ul class="genres scrolling">(.*?)</ul>')

    # ~ matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)</a>\s*<i>([^<]+)')
    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)<i>([^<]+)')
    for url, title, num in matches:
        if num == '0': continue
        if '/cine/' in url or '/destacadas/' in url or '/estrenos-hd/' in url: continue # ya están en el listado principal y no son géneros

        itemlist.append(item.clone( action='list_all', title='%s (%s)' % (title, num), url=url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        itemlist.append(item.clone( title=str(x), url= host + '/fecha/' + str(x) + '/', action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        title_alt = title.split('(')[0].strip() if ' (' in title else '' # para mejorar detección en tmdb

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if tipo != item.search_type: continue

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>'))

        if tipo == 'movie':
            qlty = scrapertools.find_single_match(article, '<span class="quality">([^<]+)')
            langs = []
            if '<div class="castellano">' in article: langs.append('Esp')
            if '<div class="latino">' in article: langs.append('Lat')
            if '<div class="subtitulado">' in article: langs.append('Vose')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, languages = ', '.join(langs), 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))

            
    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, ' href="([^"]+)"*><span class="icon-chevron-right">')

    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = "<span class='se-t[^']*'>(\d+)</span>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


# Si una misma url devuelve los episodios de todas las temporadas, definir rutina tracking_all_episodes para acelerar el scrap en trackingtools.
def tracking_all_episodes(item):
    return episodios(item)

def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)

    patron = "<li class='mark-\d+'>(.*?)</li>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for datos in matches[item.page * perpage:]:
        try:
            url, title = scrapertools.find_single_match(datos, " href='([^']+)'>([^<]+)</a>")
            season, episode = scrapertools.find_single_match(datos, "<div class='numerando'>(\d+) - (\d+)")
        except:
            continue

        if not item.contentSeason: continue
        elif not str(item.contentSeason) == season: continue

        thumb = scrapertools.find_single_match(datos, " src='([^']+)")
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def last_episodes(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = r'data-src="([^"]+)".*?<div class="data"><h3><a href="([^"]+)">([^<]+)</a></h3> ' \
             r'<span>([^/]+).*?<span class="serie">([^<]+)'

    matches = scrapertools.find_multiple_matches(data, patron)

    for thumb, url, title, season_episode, tvshow_title in matches:
        if not url or not title: continue

        season = scrapertools.find_single_match(season_episode, 'T(.*?) E')
        episode = scrapertools.find_single_match(season_episode, 'E(.*?)$')
        if not season or not episode: continue

        if thumb.startswith('//') == True: thumb = 'https:' + thumb

        titulo = season + 'x' + episode + ' ' + title.strip() + '  ' + tvshow_title.strip()

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail = thumb, url = url,
                                    contentType = 'episode', contentSerieName = tvshow_title, contentSeason = season, contentEpisodeNumber = episode ))

    if itemlist:
        next_url = scrapertools.find_multiple_matches(data, """<span class="current">.*?<a href='([^']+)""")
        if next_url:
            url = next_url[-1]
            itemlist.append(item.clone( title=">> Página siguiente", action="last_episodes", url = url, text_color='coral' ))

    return itemlist


def last_seasons(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(item.url)

    matches = re.compile(' class="item se seasons"(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, '<span class="c">(.*?)</span>')
        numtempo = scrapertools.find_single_match(article, '<span class="b">(\d+)</span>')
        if not url or not title or not numtempo: continue

        itemlist.append(item.clone( action='episodios', title='%s - Temporada %s' % (title, numtempo), thumbnail=thumb, url = url,
                                    contentType='season', contentSeason=numtempo, contentSerieName=title ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, ' href="([^"]+)"*><span class="icon-chevron-right">')

    if next_page_link:
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link, action='last_seasons', text_color='coral' ))

    return itemlist


def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'drive': return 'gvideo'
    elif servidor == 'drive [vip]': return 'gvideo'
    elif servidor == 'playstp': return 'streamtape'
    elif servidor == 'descargar': return 'mega' # !? 1fichier
    elif servidor == 'vip': return 'directo'
    elif servidor == 'premium': return 'digiload'
    elif servidor == 'goplay': return 'gounlimited'
    elif servidor in ['meplay', 'megaplay']: return 'netutv'
    elif servidor == 'playerv': return 'directo' # storage.googleapis.com
    elif servidor == 'stream': return 'mystream'
    else: return servidor

def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, "<li id='player-option-\d+'(.*?)</li>")
    for enlace in matches:
        # ~ logger.debug(enlace)
        dtype = scrapertools.find_single_match(enlace, "data-type='([^']+)")
        dpost = scrapertools.find_single_match(enlace, "data-post='([^']+)")
        dnume = scrapertools.find_single_match(enlace, "data-nume='([^']+)")
        if dnume == 'trailer': continue
        if not dtype or not dpost or not dnume: continue

        lang = scrapertools.find_single_match(enlace, "/img/flags/([^.']+)").lower()

        post = {'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype}
        data2 = do_downloadpage(host + 'wp-admin/admin-ajax.php', post=post, headers={'Referer':item.url})
        url = scrapertools.find_single_match(data2, "src='([^']+)")
        if not url: continue
        # ~ logger.info(url)

        # ~ src='//playerd.xyz/play.php?v=//jplayer.club/v/11g5xij6ryq2-wr'
        if 'play.php?v=' in url:
            vurl = url.split('play.php?v=')[1]
            if vurl.startswith('//'): vurl = 'https:' + vurl
            servidor = servertools.get_server_from_url(vurl)
            # ~ logger.info(servidor)
            if servidor and servidor != 'directo':
                vurl = servertools.normalize_url(servidor, vurl)
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = vurl,
                                      language = IDIOMAS.get(lang, 'VO') ))

        # ~ https://embed.playerd.xyz/players/...
        # ~ https://players.inkapelis.me/players/
        # ~ https://is.playerd.xyz/embed/...
        # ~ https://pbgzqk.inkapelis.me/embed/...
        # ~ https://play.megaplay.cc/players/...
        else:
            data2 = do_downloadpage(url, headers={'Referer':host})
            # ~ logger.debug(data2)
            dom = '/'.join(url.split('/')[:3])

            # ~ https://play.megaplay.cc/players/id5facb5f29ab755.47167764&bg=//image.tmdb.org/t/p/w780/BVgXyHfMxyS1Xu8n48YTpyTpPM.jpg
            links = scrapertools.find_multiple_matches(data2, '<li(?: id="servers"|) onclick(.*?)</li>')
            for lnk in links:
                vurl = scrapertools.find_single_match(lnk, "go_to_player\('([^']+)")
                if not vurl: continue

                vurl = vurl.replace('https://go.megaplay.cc/index.php?h=', '/playerdir/')
                if '/playerdir/' in vurl: vurl = '/playdir/' + scrapertools.find_single_match(vurl, "/playerdir/([^&]+)")
                if vurl.startswith('/'): vurl = dom + vurl
                    
                servidor = scrapertools.find_single_match(lnk, 'player/server/([^."]+)').lower()
                if not servidor: servidor = scrapertools.find_single_match(lnk, '<span class="serverx">([^<]+)').lower()
                if servidor == 'descargar': continue # 1fichier?
                # ~ logger.info(servidor)

                # ~ lang = 'Esp' if '<p>Castellano' in lnk else 'Lat' if '<p>Latino' in lnk else 'Vose' if '<p>Subtitulado' in lnk else 'VO'
                lang = scrapertools.find_single_match(lnk, "<p>([A-z]+)").lower()

                itemlist.append(Item( channel = item.channel, action = 'play', server = corregir_servidor(servidor), title = '', url = vurl,
                                      language = IDIOMAS.get(lang, 'VO') ))

            if not links:
                links = scrapertools.find_multiple_matches(data2, '<a id="servers"(.*?)</a>')
                for lnk in links:
                    lembed = scrapertools.find_single_match(lnk, 'data-embed="([^"]+)')
                    ltype = scrapertools.find_single_match(lnk, 'data-type="([^"]+)')
                    servidor = scrapertools.find_single_match(lnk, 'title="([^".]+)').lower()
                    if not servidor: servidor = scrapertools.find_single_match(lnk, '<span class="serverx">([^<]+)').lower()
                    # ~ logger.info(servidor)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = corregir_servidor(servidor), referer = url,
                                          title = '', lembed = lembed, ltype = ltype, lurl = '/'.join(url.split('/')[:3]), #other=servidor,
                                          language = IDIOMAS.get(lang, 'VO') ))

            if not links:
                dom = '/'.join(url.split('/')[:3])
                links = get_sources(data2)
                for lnk in links:
                    if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
                    itemlist.append(Item( channel = item.channel, action = 'play', server = '', # directo !?
                                          title = '', url = lnk[0], referer = url, language = IDIOMAS.get(lang, 'VO') ))

    return itemlist


# ~ https://players.inkapelis.me/edge-data/
# ~ https://players.inkapelis.me/archive?url=amJQMGdFa0lISzF3eHNBY1ZMa29Cdz09
# ~ https://hls.playerd.xyz/player.php?id=MTI3OQ

def play(item):
    logger.info()
    itemlist = []

    if item.lembed and item.ltype and item.lurl:
        post = {'type': item.ltype, 'streaming': item.lembed}
        data = do_downloadpage(item.lurl + '/edge-data/', post=post, headers={'Referer':item.referer})
        # ~ logger.debug(data)

        item.url = scrapertools.find_single_match(data, '"url": "([^"]+)')
        if not item.url:
            if data.startswith('http'): item.url = data
            elif data.startswith('/'): item.url = item.lurl + data
        if not item.url: return itemlist
        # ~ https://players.inkapelis.me/direct?dir=YH2lM9qloac09o6hbm.html

        item.url = item.url.replace('inkapelis.me/player?url=', 'inkapelis.me/player/?url=')
        item.url = item.url.replace('inkapelis.me/fplayer?url=', 'inkapelis.me/redirector.php?url=')

    if 'playerd.xyz/' in item.url or 'inkapelis.me/' in item.url:
        resp = httptools.downloadpage(item.url, headers={'Referer':item.referer if item.referer else item.url}, follow_redirects=False)
        # ~ /playdir?dir=...

        if 'refresh' in resp.headers:
            vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
        elif 'location' in resp.headers:
            vurl = resp.headers['location']
        else:
            # ~ logger.debug(resp.data)
            url = scrapertools.find_single_match(resp.data, '<iframe src="([^"]+)')
            if not url: url = scrapertools.find_single_match(resp.data, "window\.open\('([^']+)")
            if not url: url = scrapertools.find_single_match(resp.data, 'location\.href = "([^"]+)')
            if url and url.startswith('/'): url = '/'.join(item.url.split('/')[:3]) + url

            if 'playerd.xyz/' in url or 'inkapelis.me/' in url:
                url = url.replace('iframe?url=', 'redirect?url=')
                resp = httptools.downloadpage(url, headers={'Referer':item.url}, follow_redirects=False)

                if 'refresh' in resp.headers:
                    vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
                elif 'location' in resp.headers:
                    vurl = resp.headers['location']
                else:
                    # ~ logger.debug(resp.data)
                    vurl = scrapertools.find_single_match(resp.data, 'downloadurl = "([^"]+)')
                    if not vurl and 'player.php?id=' in url: vurl = url
            else:
                if url: 
                    vurl = url
                else:
                    gk_link = scrapertools.find_single_match(resp.data, 'config_player\.link = "([^"]+)')
                    if gk_link:
                        post = 'link=' + gk_link
                        data = do_downloadpage('https://players.inkapelis.me/player/plugins/gkpluginsphp.php', post=post)
                        # ~ logger.debug(data)
                        vurl = scrapertools.find_single_match(data, '"link":"([^"]+)').replace('\\/', '/')
                    else:
                        vurl = None
                        dom = '/'.join(item.url.split('/')[:3])
                        links = get_sources(resp.data)
                        for lnk in links:
                            if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
                            if lnk[1] == 'hls':
                                itemlist.append(item.clone(url = lnk[0], server = 'm3u8hls'))
                            else:
                                itemlist.append([lnk[2], lnk[0]])

        if vurl and vurl.startswith('/'): vurl = '/'.join(item.url.split('/')[:3]) + vurl

    elif item.url.startswith('http'):
        vurl = item.url

    if vurl and '/playdir' in vurl:
        resp = httptools.downloadpage(vurl, headers={'Referer':item.url}, follow_redirects=False)
        # ~ logger.debug(resp.data)
        if 'refresh' in resp.headers:
            vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
        elif 'location' in resp.headers:
            vurl = resp.headers['location']
        else:
            vurl = None
            # ~ logger.debug(resp.data)

    if vurl and 'player.php?id=' in vurl:
        resp = httptools.downloadpage(vurl, headers={'Referer':item.url}, follow_redirects=False)
        # ~ logger.debug(resp.data)
        dom = '/'.join(vurl.split('/')[:3])
        links = get_sources(resp.data)
        for lnk in links:
            if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
            if lnk[1] == 'hls':
                itemlist.append(item.clone(url = lnk[0], server = 'm3u8hls'))
            else:
                itemlist.append([lnk[2], lnk[0]])
        vurl = None

    if vurl:
        # ~ logger.info(vurl)
        servidor = servertools.get_server_from_url(vurl)
        if servidor and (servidor != 'directo' or 'googleapis.com' in vurl):
            url = servertools.normalize_url(servidor, vurl)
            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def get_sources(data):
    srcs = []
    bloque = scrapertools.find_single_match(data, '(?:"|)sources(?:"|):\s*\[(.*?)\]')
    for enlace in scrapertools.find_multiple_matches(bloque, "\{(.*?)\}"):
        v_url = scrapertools.find_single_match(enlace, '(?:"|)file(?:"|):\s*"([^"]+)')
        if not v_url: continue
        v_type = scrapertools.find_single_match(enlace, '(?:"|)type(?:"|):\s*"([^"]+)')
        v_lbl = scrapertools.find_single_match(enlace, '(?:"|)label(?:"|):\s*"([^"]+)')
        if not v_lbl: v_lbl = 'mp4'
        srcs.append([v_url, v_type, v_lbl])

    return srcs


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
