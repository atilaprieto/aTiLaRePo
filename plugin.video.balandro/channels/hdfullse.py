# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, servertools, tmdb

host = "https://hdfull.se"

perpage = 20


def do_downloadpage(url, post = None, referer = None):
    if not referer: referer = host
    headers = {'Referer': referer}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series' ))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all' ))

    itemlist.append(item.clone( title = 'Buscar intérprete ...', action = 'search', group = 'star', search_type = 'person', 
                       plot = 'Debe indicarse el nombre y apellido/s del intérprete.'))
    itemlist.append(item.clone( title = 'Buscar dirección ...', action = 'search', group = 'director', search_type = 'person',
                       plot = 'Debe indicarse el nombre y apellido/s del director.'))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action = 'list_all', title = 'Catálogo', url= host + '/movies', search_type = 'movie' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Estrenos', url = host + '/new-movies', search_type = 'movie' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Actualizadas', url = host + '/updated-movies', search_type = 'movie' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Más valoradas', url = host + '/movies/imdb_rating', search_type = 'movie' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Por alfabético', url = host + '/movies/abc', search_type = 'movie' ))
    itemlist.append(item.clone( action ='generos', title = 'Por género', search_type = 'movie' ))
    itemlist.append(item.clone( action ='anios', title = 'Por año', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action = 'list_all', title = 'Catálogo', url= host + '/tv-shows', search_type = 'tvshow' ))

    itemlist.append(item.clone( action = 'list_all', title = 'Más valoradas', url= host + '/tv-shows/imdb_rating', search_type = 'tvshow' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Por alfabético', url = host + '/tv-shows/abc', search_type = 'tvshow' ))

    itemlist.append(item.clone( action = 'generos', title = 'Por género', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    # ~ logger.debug(data)

    tipo = 'TV' if item.search_type == 'tvshow' else 'Películas'
    bloque = scrapertools.find_single_match(data, '<b class="caret"></b>&nbsp;&nbsp;%s</a>\s*<ul class="dropdown-menu">(.*?)</ul>' % tipo)

    matches = re.compile('<li><a href="([^"]+)">([^<]+)', re.DOTALL).findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title, url = host + url, action = 'list_all' ))

    return sorted(itemlist, key = lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1919, -1):
        itemlist.append(item.clone( title = str(x), url = host + '/search/year/' + str(x) + '/', action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.search_post: data = do_downloadpage(item.url, post=item.search_post)
    else: data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    patron = '<div class="item"[^>]*">'
    patron += '\s*<a href="([^"]+)"[^>]*>\s*<img class="[^"]*"\s+src="([^"]+)"[^>]*>'
    patron += '\s*</a>\s*</div>\s*<div class="rating-pod">\s*<div class="left">(.*?)</div>'
    patron += '.*? title="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)
    if item.search_post != '' and item.search_type != 'all':
        matches = filter(lambda x: ('/movie/' in x[0] and item.search_type == 'movie') or \
                                   ('/show/' in x[0] and item.search_type == 'tvshow'), matches)
    num_matches = len(matches)

    for url, thumb, langs, title in matches[item.page * perpage:]:
        title = title.strip()
        languages = detectar_idiomas(langs)
        tipo = 'movie' if '/movie/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = host + thumb
        url = host + url

        if tipo == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, 
                                        languages = ', '.join(languages), fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))
        else:
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                        languages = ', '.join(languages), fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    # ~ al no tener year no se cooresponde caratula con el titulo peg. peli wolf no es el lobo de wall street
    # ~ tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        next_page_link = scrapertools.find_single_match(data, '<a class="current">.*?href="(.*?)">')
        if next_page_link:
            url = host + next_page_link
            itemlist.append(item.clone( title = '>> Página siguiente', url = url, page = 0, action = 'list_all', text_color='coral' ))

    return itemlist


def detectar_idiomas(txt):
    languages = []
    if '/spa.png' in txt: languages.append('Esp')
    if '/lat.png' in txt: languages.append('Lat')
    if '/sub.png' in txt: languages.append('Vose')
    if '/eng.png' in txt: languages.append('Eng')
    return languages


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    patron = 'itemprop="season".*?'
    patron += "<a href='(.*?)'.*?"
    patron += '<img class=.*?original-title="(.*?)".*?'
    patron += 'src="(.*?)".*?'
    patron += '<h5.*?>(.*?)</h5>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, thumb, retitle in matches:
        numtempo = scrapertools.find_single_match(title, 'Temporadas (\d+)')
        if numtempo == '': numtempo = scrapertools.find_single_match(url, '-(\d+)$')
        if numtempo == '': continue

        titulo = title
        if retitle != title: 
           if not 'Temporadas' in retitle: titulo += ' - ' + retitle

        titulo = titulo.replace('Season', 'Temporada').replace('Temporadas', 'Temporada')

        url = host + url
        thumb = host + thumb

        if len(matches) == 1:
            title = title.replace('Season', 'Temporada').replace('Temporadas', 'Temporada')

            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.referer = item.url
            item.url = url
            item.thumbnail = thumb

            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', url = url, title = titulo, thumbnail = thumb, referer = item.url,
                                    contentType = 'season', contentSeason = numtempo, page = 0 ))

    if len(itemlist) == 0:
        itemlist.append(item.clone( action = 'episodios', url = item.url + '/season-1', title = 'Temporada 1', referer = item.url,
                                    contentType = 'season', contentSeason = 1, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    color_lang = config.get_setting('list_languages_color', default='red')

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    patron = '<div class="item center">.*?'
    patron += '<a href="(.*?)".*?'
    patron += 'src="(.*?)".*?'
    patron += 'title="(.*?)".*?'
    patron += '<div class="item-flag(.*?)'
    patron += '<div class="rating">(.*?)<.*?'
    patron += '</b>(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title, idio, tempo, epis in matches[item.page * perpage:]:
        titulo = title.replace(item.contentSerieName, '').strip()

        if ' - ' in titulo: titulo = titulo.split(' - ')[1]
        titulo = tempo + 'x' + epis + ' ' + titulo

        idio = idio.replace('ESPSUB', 'Vose').replace('ENG', 'Eng').replace('ESP', 'Esp').replace('LAT', 'Lat').replace('EngSUB', 'EngSub')

        langs = scrapertools.find_multiple_matches(idio, 'item-flag-(.*?)">')
        if str(langs) == "['']": langs = ''
        if langs: titulo += ' [COLOR %s][%s][/COLOR]' % (color_lang, ', '.join(langs))

        thumb = host + thumb
        url = host + url

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = tempo, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['CAM', 'TS', 'DVDSCR', 'DVDRIP', 'HDTV', 'RHDTV', 'HD720', 'HD1080']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    data_js = do_downloadpage(host + '/static/style/js/jquery.hdfull.view.min.js')
    # ~ logger.debug(data_js)

    keys = scrapertools.find_multiple_matches(data_js, 'JSON.parse\(atob.*?substrings\((.*?)\)')
    if not keys: 
        keys = scrapertools.find_multiple_matches(data_js, 'JSON.*?\]\((0x[0-9a-f]+)\)\);')
        if keys: 
            for i, key in enumerate(keys): keys[i] = int(key, 16)
        else: keys = scrapertools.find_multiple_matches(data_js, 'JSON.*?\]\(([0-9]+)\)\);')

    data_js = do_downloadpage(host + '/static/js/providers.js')
    from lib import balandroresolver
    try:
        provs = balandroresolver.hdfull_providers(data_js)
        if provs == '': return []
    except:
        return []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    data_obf = scrapertools.find_single_match(data, "var ad\s*=\s*'(.*?)'")

    for key in keys:
        data_decrypt = jsontools.load(balandroresolver.obfs(base64.b64decode(data_obf), 126 - int(key)))
        if data_decrypt: break

    matches = []
    for match in data_decrypt:
        if match['provider'] in provs:
            try:
                embed = provs[match['provider']][0]
                url = eval(provs[match['provider']][1].replace('_code_', "match['code']"))
                matches.append([match['lang'], match['quality'], url, embed])
            except:
                pass

    for idioma, calidad, url, embed in matches:
        # ~ logger.info('%s %s' % (embed, url))
        if embed == 'd' and 'uptobox' not in url: continue
        try:
            calidad = unicode(calidad, 'utf8').upper().encode('utf8')
        except: 
            try:
                calidad = str(calidad, 'utf8').upper()
            except: calidad  = calidad.upper()                
        idioma = idioma.capitalize() if idioma != 'ESPSUB' else 'Vose'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, 
                              language = idioma, quality = calidad, quality_num = puntuar_calidad(calidad)
                       ))

    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.group:
            item.url = host + '/search' + '/' + item.group + '/' + texto
            item.search_type = ''
        else:
            texto = texto.replace(' ', '+')
            item.search_post = {'menu': 'search', 'query': texto}
            item.url = host + '/search'
			
        if item.search_type == '': item.search_type = 'all'
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
