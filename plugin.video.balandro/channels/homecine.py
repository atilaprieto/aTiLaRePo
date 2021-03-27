# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools, recaptcha
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://homecine.tv'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release-year/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Buscar intérprete ...', action = 'search', group = 'stars', search_type = 'person',
                       plot = 'Debe indicarse el nombre y apellido/s del intérprete.'))
    itemlist.append(item.clone( title = 'Buscar dirección ...', action = 'search', group = 'director', search_type = 'person',
                       plot = 'Debe indicarse el nombre y apellido/s del director.'))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + '/top-imdb/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_episodes', url = host + '/ver/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por estudio', action = 'estudios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    matches = [
        ['/animacion/', 'Animación'],
        ['/comedia/', 'Comedia'],
        ['/crimen/', 'Crimen'],
        ['/documental/', 'Documental'],
        ['/drama/', 'Drama'],
        ['/familia/', 'Familia'],
        ['/kids/', 'Kids'],
        ['/misterio/', 'Misterio'],
        ['/news/', 'News'],
        ['/reality/', 'Reality'],
        ['/soap/', 'Soap'],
        ['/talk/', 'Talk'],
        ['/western/', 'Western']
        ]

    if item.search_type == 'movie':
        data = do_downloadpage(host)

        matches = scrapertools.find_multiple_matches(data, '><a href="/genre([^"]+)">(.*?)</a>')

    for url, title in matches:
        url = host + '/genre' + url

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    itemlist.append(item.clone( action = "list_all", title = 'Documentales', url = host + '/genre/documentales/' ))

    return sorted(itemlist, key = lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1939, -1):
        url = host + '/release-year/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    web_paises = [
	   ['argentina', ''],
	   ['australia', ''],
	   ['austria', ''],
	   ['belgium', 'Belgica'],
	   ['bolivia', ''],
	   ['brazil', 'Brasil'],
	   ['bulgaria', ''],
	   ['canada', ''],
	   ['chile', ''],
	   ['china', ''],
	   ['colombia', ''],
	   ['costa-rica', 'Costa Rica'],
	   ['cuba', ''],
	   ['czech-republic', 'Republica Checa'],
	   ['denmark', 'Dinamarca'],
	   ['euador', ''],
	   ['finland', 'Finlandia'],
	   ['france', 'Francia'],
	   ['germany', 'Alemania'],
	   ['greece', 'Grecia'],
	   ['honduras', ''],
	   ['Hong-kong', 'Hong Kong'],
	   ['hungary', 'Hungria'],
	   ['iceland', 'Islandia'],
	   ['india', ''],
	   ['ireland', 'Irlanda'],
	   ['israel', ''],
	   ['italy', 'Italia'],
	   ['japan', 'Japon'],
	   ['lithuania', 'Lituania'],
	   ['malaysia', 'Malasia'],
	   ['mexico', ''],
	   ['netherlands', 'Paises Bajos'],
	   ['new-zealand', 'Nueva Zelanda'],
	   ['norway', 'Noruega'],
	   ['panama', ''],
	   ['paraguay', ''],
	   ['peru', ''],
	   ['poland', 'Polonia'],
	   ['portugal', ''],
	   ['puerto-rico', 'Puerto Rico'],
	   ['romania', 'Rumania'],
	   ['russia', 'Rusia'],
	   ['serbia', ''],
	   ['singapore', 'Singapur'],
	   ['spain', 'España'],
	   ['sweden', 'Suecia'],
	   ['switzerland', 'Suiza'],
	   ['thailand', 'Tailandia'],
	   ['turkey', 'Turquía'],
	   ['ukraine', 'Ucrania'],
	   ['uk', 'Reino Unido'],
	   ['usa', 'Estados Unidos'],
	   ['uruguay', ''],
	   ['venezuela', '']
	   ]

    for x in web_paises:
        title = x[1]
        pais = x[0]

        if title == '': title = pais.capitalize()

        url = url = host + '/country/' + pais + '/'

        results_for = pais

        if results_for == 'costa-rica': results_for = 'Costa-Rica'
        elif results_for == 'czech-republic': results_for = 'Czech-Republic'
        elif results_for == 'hong-kong': results_for = 'Hong-kong'
        elif results_for == 'new-zealand': results_for = 'New-Zealand'
        elif results_for == 'puerto-rico': results_for = 'Puerto-Rico'
        elif results_for == 'uk': results_for = 'UK'
        elif results_for == 'usa': results_for = 'USA'

        itemlist.append(item.clone( title = title, url = url, action ='list_all' ))

    return sorted(itemlist, key = lambda it: it.title)


def plataformas(item):
    logger.info()
    itemlist = []

    web_plataformas = [
	   ['ae', 'A&E'],
	   ['abc', 'ABC'],
	   ['abc-fox', 'ABC, FOX'],
	   ['acorn-tv', 'Acorn TV'],
	   ['adult-swim', 'Adult Swim'],
	   ['amazon', 'Amazon'],
	   ['amc', 'AMC'],
	   ['antena-3', 'Antena 3'],
	   ['apple-tv', 'Apple TV+'],
	   ['axn', 'AXN'],
	   ['bbc-america', 'BBC America'],
	   ['bbc-iplayer', 'BBC iPlayer'],
	   ['bbc-one', 'BBC One'],
	   ['bbc-two', 'BBC Two'],
	   ['caracol-tv', 'Caracol TV'],
	   ['cartoon-network', 'Cartoon Network'],
	   ['cartoon-network-teletoon-tv-tokyo', 'Cartoon Network, Teletoon, TV Tokyo'],
	   ['cbc-television', 'CBC Television'],
	   ['cbs', 'CBS'],
	   ['cbs-all-access', 'CBS All Access'],
	   ['channel-4', 'Channel 4'],
	   ['comedy-central', 'Comedy Central'],
	   ['ctv', 'CTV'],
	   ['cuatro', 'Cuatro'],
	   ['disney-channel', 'Disney Channel'],
	   ['disney-xd', 'Disney XD'],
	   ['disney', 'Disney+'],
	   ['dmax', 'DMax'],
	   ['epix', 'Epix'],
	   ['espn-netflix', 'ESPN Netflix'],
	   ['flooxer', 'Flooxer'],
	   ['fox', 'FOX'],
	   ['fox-espana', 'FOX España'],
	   ['france-3', 'France 3'],
	   ['freeform', 'Freeform'],
	   ['fx', 'FX'],
	   ['hbo', 'HBO'],
	   ['hbo-europe', 'HBO Europe'],
	   ['history', 'History'],
	   ['hulu', 'Hulu'],
	   ['itv', 'ITV'],
	   ['la-1', 'La 1'],
	   ['la-une', 'La Une'],
	   ['lifetime', 'Lifetime'],
	   ['movistar', 'Movistar+'],
	   ['mtv', 'MTV'],
	   ['nbc', 'NBC'],
	   ['netflix', 'Netflix'],
	   ['nickelodeon', 'Nickelodeon'],
	   ['orf', 'ORF'],
	   ['paramount-network', 'Paramount Network'],
	   ['rai-1', 'Rai 1'],
	   ['rai-2', 'Rai 2'],
	   ['ruv', 'RÚV'],
	   ['shudder', 'Shudder'],
	   ['showcase', 'Showcase'],
	   ['showtime', 'Showtime'],
	   ['sky-atlantic', 'Sky Atlantic'],
	   ['sky-one', 'Sky One'],
	   ['syfy', 'Syfy'],
	   ['star-tv', 'Star TV'],
	   ['starz', 'Starz'],
	   ['tbs', 'TBS'],
	   ['the-cw', 'The CW'],
	   ['the-wb', 'The WB'],
	   ['telecinco', 'Telecinco'],
	   ['telemundo', 'Telemundo'],
	   ['televisa', 'Televisa'],
	   ['tnt', 'TNT'],
	   ['tv3', 'TV3'],
	   ['tvn', 'TVN'],
	   ['univision', 'Univision'],
	   ['usa-network', 'USA Network'],
	   ['vh1', 'VH1'],
	   ['viaplay', 'Viaplay'],
	   ['zdf', 'ZDF']
	   ]

    for x in web_plataformas:
        title = x[1]
        title = title.replace('-', ' ')

        url = host + '/networks/' + x[0] + '/'

        itemlist.append(item.clone( title = title, url = url, action ='list_all' ))

    return itemlist

def estudios(item):
    logger.info()
    itemlist = []

    web_estudios = [
	   ['26-keys-productions', '26 Keys Productions'],
	   ['abc-studios', 'ABC Studios'],
	   ['amazon-studios', 'Amazon Studios'],
	   ['amblin-television', 'Amblin Television'],
	   ['amc-studios', 'AMC Studios'],
	   ['alloy-entertainment', 'Alloy Entertainment'],
	   ['atlas-entertainment', 'Atlas Entertainment'],
	   ['awesomenesstv', 'AwesomenessTV'],
	   ['bad-robot', 'Bad Robot'],
	   ['bbc', 'BBC'],
	   ['blumhouse-television', 'Blumhouse Television'],
	   ['bonanza-productions', 'Bonanza Productions'],
	   ['cbs-television-studios', 'CBS Television Studios'],
	   ['fox-21', 'Fox 21'],
	   ['fox-21-television-studios', 'Fox 21 Television Studios'],
	   ['fox-television-studios', 'Fox Television Studios'],
	   ['freeform', 'Freeform Studios'],
	   ['fx-productions', 'FX Productions'],
	   ['genre-films', 'Genre Films'],
	   ['hanna-barbera-productions', 'Hanna-Barbera Productions'],
	   ['itv', 'ITV Studios'],
	   ['marvel-entertainment', 'Marvel Entertainment'],
	   ['marvel-television', 'Marvel Television'],
	   ['mgm-television', 'MGM Television'],
	   ['monkeypaw-productions', 'Monkeypaw Productions'],
	   ['movistar', 'Movistar+'],
	   ['neal-street-productions', 'Neal Street Productions'],
	   ['nelvana-limited', 'Nelvana Limited'],
	   ['netflix', 'Netflix'],
	   ['paramount-television', 'Paramount Television'],
	   ['platinum-dunes', 'Platinum Dunes'],
	   ['secret-hideout', 'Secret Hideout'],
	   ['showtime-networks', 'Showtime Networks'],
	   ['sky', 'Sky'],
	   ['syfy', 'Syfy'],
	   ['skydance-television', 'Skydance Television'],
	   ['televisa', 'Televisa'],
	   ['universal-cable-productions', 'Universal Cable Productions'],
	   ['universal-television', 'Universal Television'],
	   ['usa-network', 'USA Network'],
	   ['vertigo-films', 'Vertigo Films'],
	   ['viaplay', 'Viaplay'],
	   ['walt-disney-television', 'Walt Disney Television'],
	   ['warner-bros-animation', 'Warner Bros. Animation'],
	   ['warner-bros-television', 'Warner Bros. Television'],
	   ['zdf', 'ZDF']
	   ]

    for x in web_estudios:
        title = x[1]
        title = title.replace('-', ' ')

        url = host + '/studio/' + x[0] + '/'

        itemlist.append(item.clone( title = title, url = url, action ='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('movie-id="\d+".*?<a href="([^"]+)".*?<.*?original="([^"]+)".*?<h2>([^<]+)</h2>.*?jtip(.*?)clearfix', re.DOTALL).findall(data)

    for url, thumb, title, info in matches:
        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        url = host + url

        if thumb.startswith('//'): thumb = 'https:' + thumb
        elif thumb.startswith('/'): thumb = host + thumb

        title = title

        year = scrapertools.find_single_match(info, 'rel="tag">(\d{4})<')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(info, '-quality">(.*?)</div>')

        if '/series/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))
        else:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    url_next_page = scrapertools.find_single_match(data, "<li class='active'>.*?class='page larger' href='([^']+)'")

    if url_next_page:
        url_next_page = host + url_next_page

        itemlist.append(item.clone( title = '>> Página siguiente', action = 'list_all', url = url_next_page, text_color='coral' ))

    return itemlist


def list_episodes(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = re.compile('movie-id="\d+".*?<a href="([^"]+)".*?<.*?original="([^"]+)".*?<h2>([^<]+)</h2>.*?jtip(.*?)clearfix', re.DOTALL).findall(data)

    for url, thumb, title, info in matches:
        serie_name = scrapertools.find_single_match(title, '(.*?) Temporada').strip()

        season = scrapertools.find_single_match(info, '-quality">Season(.*?)</div>').strip()
        episode = scrapertools.find_single_match(info, '<div class="jt-info jt-imdb">Episode(.*?)</div>').strip()
        if not season or not episode: continue

        url = host + url

        titulo = title

        fecha = scrapertools.find_single_match(info, '<span class="ep_airdate">(.*?)</span>').strip()
        if fecha:
           titulo = titulo + '  (' + fecha + ')'

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url, thumbnail = thumb,
                                    contentType = 'episode', contentSerieName=serie_name, contentSeason = season, contentEpisodeNumber = episode ))

    url_next_page = scrapertools.find_single_match(data, "<li class='active'>.*?class='page larger' href='([^']+)'")

    if url_next_page:
        url_next_page = host + url_next_page

        itemlist.append(item.clone( title = '>> Página siguiente', action = 'list_episodes', url = url_next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = r'<strong>(?:Season|Temporada) (\d+)</strong>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for season in matches:
        title = 'Temporada ' + season

        url = item.url

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.url = url
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, contentType = 'season', contentSeason = season, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    season = item.contentSeason

    data = do_downloadpage(item.url)

    patron_season = '<strong>(?:Season|Temporada) %s</strong>.*?class="les-content"(.*?)</div>' % season
    data = scrapertools.find_single_match(data, patron_season)

    matches = re.compile('<a href="([^"]+)">(?:Episode|Capitulo) (\d+)', re.DOTALL).findall(data)

    for url, epis in matches[item.page * perpage:]:
        url = host + url

        try: titulo = '%sx%s - Capítulo %s' % (season, epis, epis)
        except: titulo = 'Episodio ' + epis

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose', 'Ingles': 'VO', 'Español Latino': 'Lat', 'Español Castellano': 'Esp'}

    data = do_downloadpage(item.url)

    matches = re.compile('<div id="tab(\d+)".*?(?i)<iframe.*?src="([^"]+)"', re.DOTALL).findall(data)

    for option, url in matches:
        info = scrapertools.find_single_match(data, '<a href="#tab%s">(.*?)<' % option)
        if '-' in info:
            qlty, lang = scrapertools.find_single_match(info, '(.*?) - (.*)')
            if " / " in lang: lang = lang.split(" / ")[1]
        else:
            lang = ''
            qlty = info

        if url.startswith('//'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        if not servidor: servidor = 'directo'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                              quality = qlty, language = IDIOMAS.get(lang, lang) ))

    if 'href="#list-dl">Descargar</a>' in data:
        bloque = scrapertools.find_single_match(data, 'href="#list-dl">Descargar</a>(.*?)<span>Te podría interesar:</span>')

        matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)".*?class="flag flag-.*?<span class="lang_tit">(.*?)</span>.*?<span class="lnk lnk-dl" >(.*?)</span>')

        for url, lang, qlty in matches:
            if url.startswith('//'): url = 'https:' + url

            url = url.replace('?download=1', '')

            servidor = servertools.get_server_from_url(url)
            if not servidor: servidor = 'directo'

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                  quality = qlty, language = IDIOMAS.get(lang, lang), other = 'D' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server and item.server != 'directo':
        url = servertools.normalize_url(item.server, item.url)
        itemlist.append(item.clone( url = item.url, server = item.server ))
        return itemlist

    if '/cinemaupload.com/' in item.url or '/pastea.me/ ':
        if '/cinemaupload.com/' in item.url:
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


    referer = host + '/'
    headers = {'Referer': referer}

    url = httptools.downloadpage(item.url, headers = headers, follow_redirects = False, only_headers = True).headers.get('location', '')

    if url:
        data = do_downloadpage(url, headers = headers, raise_weberror = False)
        url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')

    if url:
        if '/manifest.mpd' in url:
            if platformtools.is_mpd_enabled(): itemlist.append(['mpd', url, 0, '', True])
            itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
        else: itemlist.append(['mp4', url])

        return itemlist

    if 'embed.cload' in item.url:
        data = do_downloadpage(item.url, headers = headers, raise_weberror = False)
        # ~ logger.debug(data)

        if '<div class="g-recaptcha"' in data or 'Solo los humanos pueden ver' in data:
            headers = {'Referer': referer, 'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)'}
            data = do_downloadpage(item.url, headers = headers, raise_weberror = False)
            # ~ logger.debug(data)

            new_url = scrapertools.find_single_match(data, '<div id="option-players".*?src="([^"]+)"')
            if new_url:
                new_url = new_url.replace('/cinemaupload.com/', '/embed.cload.video/')
                data = do_downloadpage(new_url, raise_weberror = False)
                # ~ logger.debug(data)

            url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')

            if url:
                if '/manifest.mpd' in url:
                    if platformtools.is_mpd_enabled(): itemlist.append(['mpd', url, 0, '', True])
                    itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
                else: itemlist.append(['m3u8', url])

                return itemlist

    if url:
        servidor = servertools.get_server_from_url(url)
        if servidor and servidor != 'directo':
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info("texto: %s" % texto)
    try:
        if item.group:
            item.url = host + '/' + item.group + '/' + texto.replace(" ", "-")
            item.search_type = ''
        else:
            item.url = host + '/?s=' + texto.replace(" ", "+")

        if item.search_type == '': item.search_type = 'all'
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

