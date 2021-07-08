# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    PY3 = False
else:
    PY3 = True

	
import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = "https://seriespapaya.xyz/"


notification_d_ok = config.get_setting('notification_d_ok', default=True)

color_alert = config.get_setting('notification_alert_color', default='red')


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
    # ~ data = httptools.downloadpage_proxy('seriespapayaxyz', url, post=post, headers=headers, follow_redirects=follow_redirects).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                # ~ logger.debug('Cookies: %s %s' % (ck_name, ck_value))
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                data = httptools.downloadpage(url, post=post, headers=headers).data
                # ~ data = httptools.downloadpage_proxy('seriespapayaxyz', url, post=post, headers=headers).data
                # ~ logger.debug(data)
        except:
            pass

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

    itemlist.append(item.clone( title='Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    # ~ itemlist.append(item_configurar_proxies(item))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow' ))

    # ~ itemlist.append(item_configurar_proxies(item))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    opciones = [
        ('Acción', 'accion'),
        ('Aventura', 'aventura'),
        ('Animación', 'animacion'),
        ('Bélica', 'belica'),
        ('Comedia', 'comedia'),
        ('Crimen', 'crimen'),
        ('Documental', 'documental'),
        ('Drama', 'drama'),
        ('Familia', 'familia'),
        ('Fantasía', 'fantasia'),
        ('Historia', 'historia'),
        ('Kids', 'kids'),
        ('Música', 'musica'),
        ('Misterio', 'misterio'),
        ('Reality', 'reality'),
        ('Romance', 'romance'),
        ('Suspense', 'suspense'),
        ('Western', 'western')
        ]


    for tit, opc in opciones:
        url = host + 'category/' + opc + '/'

        if item.search_type == 'tvshow':
            url = url + '?tr_post_type=2'
        else:
            url = url + '?tr_post_type=1'

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'tvshow':
       tope = 1999
    else:
       tope = 1999

    for x in range(current_year, tope, -1):
        url = host + '?s=trfilter&trfilter=1&years%5B%5D=' + str(x)

        if item.search_type == 'tvshow':
            url = url + '&tr_post_type=2'
        else:
            url = url + '&tr_post_type=1'

        itemlist.append(item.clone( title = str(x), action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&')

    if not 'tr_post_type=' in item.url:
        if item.search_type == 'tvshow':
            item.url = item.url + '?tr_post_type=2'
        elif item.search_type == 'movie':
           item.url = item.url + '?tr_post_type='

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = 'class="TPost C">.*?<a href="([^"]+)".*?src="([^"]+)".*?class="Title">([^<]+)</h3>.*?<span class="Year">([^<]+)</span>(.*?)</article>'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, year, info in matches:
        tipo = 'movie' if item.search_type == 'movie' else 'tvshow'

        if item.search_type == 'all':
            if '<span class="TpTv BgA">TV</span>' in info: tipo = 'tvshow'
            else: tipo = 'movie'

        sufijo = '' if item.search_type != 'all' else tipo

        thumb if thumb.startswith('http') else "https:" + thumb

        if tipo == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title,  infoLabels = {'year': year} ))

        if tipo == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')
    if itemlist and next_page:
        itemlist.append(item.clone( title = '>> Página siguiente', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in '0ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        title = '0-9' if letra == '0' else letra

        url = host + 'letter/' + title  + '/'

        if item.search_type == 'tvshow':
            url = url + '?tr_post_type=2'
        else:
            url = url + '?tr_post_type=1'

        itemlist.append(item.clone( action='por_letra', title = title, url = url ))

    return itemlist


def por_letra(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&')

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<td><span class="Num">(.*?)</tr>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<strong>(.*?)</strong>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')
        thumb if thumb.startswith('http') else "https:" + thumb

        year = scrapertools.find_single_match(match, '</strong>.*?<td>(.*?)</td>')

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))
        else:
            itemlist.append(item.clone( action = 'temporadas', url= url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = title,  infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')
    if itemlist and next_page:
        itemlist.append(item.clone( title = '>> Página siguiente', action = 'por_letra', url = next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&')

    data = do_downloadpage(item.url)

    if not PY3:
        if not data:
            if notification_d_ok:
                platformtools.dialog_ok(config.__addon_name, '[COLOR yellow]Probable incompatibilidad con la versión de su Media Center.[/COLOR]', 'El canal no da respuesta a las temporadas en esta serie.')
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Media Center Incompatible[/COLOR][/B]' % color_alert)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="Title AA-Season.*?data-tab="(.*?)">(.*?)<i class(.*?)</tbody>')

    for season, title, episodes in matches:
        sin_epis = ''
        if '<td>Episodios no disponibles</td>' in episodes:
            sin_epis = 's'

        title = re.sub('<.?span>','',title)
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.sin_epis = sin_epis
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = season, sin_epis = sin_epis, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if item.sin_epis == 's':
        color_avis  = config.get_setting('notification_avis_color', default='yellow')
        platformtools.dialog_notification(item.title, '[B][COLOR %s]Aún sin episodios[/COLOR][/B]' % color_avis)
        return itemlist

    item.url = item.url.replace('&#038;', '&')

    if not item.page: item.page = 0

    perpage = 50

    data = do_downloadpage(item.url)

    if not PY3:
        if not data:
            if notification_d_ok:
                platformtools.dialog_ok(config.__addon_name, '[COLOR yellow]Probable incompatibilidad con la versión de su Media Center.[/COLOR]', 'El canal no da respuesta a los episodios de la temporada dn esta serie.')
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Media Center Incompatible[/COLOR][/B]' % color_alert)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="Title AA-Season.*?data-tab="%s">.*?<tbody>(.*?)</tbody>' % str(item.contentSeason))

    if 'src=&quot;' in bloque:
         bloque = bloque.replace('src=&quot;', 'src="').replace('&quot;', '"')

    matches = scrapertools.find_multiple_matches(bloque, '<td><span class="Num">(\d+)</span></td>.*?src="([^"]+).*?href="([^"]+)">([^<]*)')

    for epis, thumb, url, title in matches[item.page * perpage:]:
        thumb if thumb.startswith('http') else "https:" + thumb

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb, 
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title = ">> Página siguiente", action = "episodios", page = item.page + 1, text_color='coral' ))

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    orden = ['ts-scr', '240-p', '360-p', '480-p', 'w-rip', 'hd-rip', '720-p', '1080-p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es': 'Esp', 'lat': 'Lat', 'sub': 'Vose', 'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose'}

    item.url = item.url.replace('&#038;', '&')

    data = do_downloadpage(item.url)

    if not PY3:
        if not data:
            if notification_d_ok:
                platformtools.dialog_ok(config.__addon_name, '[COLOR yellow]Probable incompatibilidad con la versión de su Media Center.[/COLOR]', 'El canal no da respuesta a los enlaces de reproducción.')
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Media Center Incompatible[/COLOR][/B]' % color_alert)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<td><span class="Num">.*?href="([^"]+)".*?class="Button STPb">([^<]+)</a></td><td><span><.*?>\s*([^<]+)' \
             '</span></td><td><span><img.*?>([^<]+)</span></td><td><span>([^<]+)'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, tipo, servidor, lang, qlty in matches:
        if url.startswith('https://acortar24.xyz/'): continue

        lang = IDIOMAS.get(lang)

        quality = qlty.lower()
        if quality == 'desconocido': quality = ''

        servidor = servidor.strip().lower()
        if servidor == 'ok': servidor = 'okru'

        server = servertools.corregir_servidor(servidor)
        # ~ logger.debug('%s %s' % (server, url))

        itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                             language = IDIOMAS.get(lang,lang), quality = quality.upper(), quality_num = puntuar_calidad(quality) ))

    if 'data-tplayernv="Opt' in data:
        options = scrapertools.find_multiple_matches(data, 'data-tplayernv="Opt(.*?)"><span>(.*?)</span><span>(.*?) - (.*?)</span>')

        for opt, servidor, lang, qlty in options:
            lang = IDIOMAS.get(lang)

            quality = qlty.lower()
            if quality == 'desconocido': quality = ''

            servidor = servidor.strip().lower()
            if servidor == 'ok': servidor = 'okru'

            server = servertools.corregir_servidor(servidor)

            if 'src=&quot;' in data:
                data = data.replace('src=&quot;', 'src="').replace('&quot;', '"')

            url = scrapertools.find_single_match(data, 'id="Opt' + opt + '".*?src="(.*?)"')

            if url:
                url= url.replace('&amp;#038;', '&').replace('&amp;', '&')

                itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                     language = IDIOMAS.get(lang,lang), quality = quality.upper(), quality_num = puntuar_calidad(quality) ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&#038;', '&')

    if item.url.startswith(host):
        headers = {'Referer': host}

        url = ''

        resp = httptools.downloadpage(item.url, follow_redirects=False, headers=headers)
        if 'location' in resp.headers: 
            url = resp.headers['location']

        if not url:
            headers = {'Referer': host, 'Connection': 'keep-alive'}
            data = httptools.downloadpage(item.url, headers=headers).data
            # ~ logger.debug(data)

            url = scrapertools.find_single_match(data, 'src="(.*?)"')
            if not url: url = scrapertools.find_single_match(data, 'SRC="(.*?)"')

        if url:
            itemlist.append(item.clone(server = item.server, url = url))

    elif item.url.startswith('https://ouo.io/'):
        if not '/go/' in item.url:
            item.url = item.url.replace('https://ouo.io/', 'https://ouo.io/go/')

        ouo_code = item.url.replace('https://ouo.io/go/', '')
        headers = {'Referer': item.url.replace('/go/', '/')}

        data = httptools.downloadpage(item.url).data

        _action, _id, _token = scrapertools.find_single_match(data, '<form method="POST" action="(.*?)".*?id="(.*?)".*?name="_token" type="hidden" value="(.*?)"')
        post = {'action': _action, 'id': _id, '_token': _token }
        datos_post = httptools.downloadpage(item.url, post = post, headers = headers).data

        try:
           _action2, _id2, _token2 = scrapertools.find_single_match(datos_post, '<form method="POST" action="(.*?)".*?id="(.*?)".*?name="_token" type="hidden" value="(.*?)"')
           if _action2:
               if not _action2 == _action:
                   headers = {'Referer': item.url}
                   if ouo_code in _action2: item.url = _action2
                   _action = _action2
                   _id = _id2
                   _token = _token2
        except:
           pass
 
        post = {'action': _action, 'id': _id, '_token': _token }

        url = httptools.downloadpage(item.url, post = post, headers = headers, follow_redirects=False, only_headers=True).headers.get('location', '')

        if url:
            if url.startswith('//') == True: url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            if servidor:
                url = servertools.normalize_url(servidor, url)
                itemlist.append(item.clone(url = url, server = servidor))

    else:
        data = httptools.downloadpage(item.url).data
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

       if item.search_type == 'movie':
           item.url = item.url + '&tr_post_type=1'
       elif item.search_type == 'tvshow':
           item.url = item.url + '&tr_post_type=2'
       else:
           item.url = item.url + '&tr_post_type='

       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []

