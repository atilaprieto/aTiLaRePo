# -*- coding: utf-8 -*-

import re, urllib

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


CHANNEL_HOST = "https://www.cinetux.to/"

IDIOMAS = {'Latino': 'Lat', 'Subtitulado': 'VOSE', 'Español': 'Esp', 'Espa%C3%B1ol':'Esp', 'SUB': 'VO' }


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + CHANNEL_HOST + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, CHANNEL_HOST)

def do_downloadpage(url, post=None, headers=None):
    url = url.replace('http://', 'https://')
    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('cinetux', url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []
    
    itemlist.append(item.clone( title='Actualizadas', action='peliculas', url=CHANNEL_HOST + 'pelicula/' ))
    itemlist.append(item.clone( title='Destacadas', action='peliculas', url=CHANNEL_HOST + 'mas-vistos/?get=movies' ))
    itemlist.append(item.clone( title='Estrenos', action='peliculas', url=CHANNEL_HOST + 'genero/estrenos/' ))
    itemlist.append(item.clone( title='Por Idioma', action='idiomas' ))
    itemlist.append(item.clone( title='Por Género', action='generos' ))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie' ))

    itemlist.append(item_configurar_proxies(item))
    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='peliculas', title='Español', url= CHANNEL_HOST + 'idioma/espanol/' ))
    itemlist.append(item.clone( action='peliculas', title='Latino', url= CHANNEL_HOST + 'idioma/latino/' ))
    itemlist.append(item.clone( action='peliculas', title='VOSE', url= CHANNEL_HOST + 'idioma/subtitulado/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = do_downloadpage(CHANNEL_HOST)
    bloque = scrapertools.find_single_match(data, '(?s)dos_columnas">(.*?)</ul>')

    patron = ' href="/([^"]+)">([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)
    for scrapedurl, scrapedtitle in matches:
        if '/estrenos/' in scrapedurl: continue # se muestra en el menú principal
        if descartar_xxx and scrapertools.es_genero_xxx(scrapedtitle): continue

        itemlist.append(item.clone( action='peliculas', title=scrapedtitle.strip(), url=CHANNEL_HOST + scrapedurl ))

    if 'genero/belica/' not in bloque:
        itemlist.append(item.clone( action='peliculas', title='Bélica', url=CHANNEL_HOST + 'genero/belica/' ))

    return sorted(itemlist, key=lambda it: it.title)


# A partir de un título detectar si contiene una versión alternativa y devolver ambos
def extraer_show_showalt(title):
    if ' / ' in title: # pueden ser varios títulos traducidos ej: Lat / Cast, Cast / Lat / Eng, ...
        aux = title.split(' / ')
        show = aux[0].strip()
        showalt = aux[-1].strip()
    else:
        show = title.strip()
        showalt = scrapertools.find_single_match(show, '\((.*)\)$') # si acaba en (...) puede ser el título traducido ej: Lat (Cast)
        if showalt != '':
            show = show.replace('(%s)' % showalt, '').strip()
            if showalt.isdigit(): showalt = '' # si sólo hay dígitos no es un título alternativo

    return show, showalt

def peliculas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    patron = '<article id="[^"]*" class="item movies">(.*?)</article>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for article in matches:

        thumb, title = scrapertools.find_single_match(article, ' src="([^"]+)" alt="([^"]+)')
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        year = scrapertools.find_single_match(article, '/ano/(\d{4})/')
        plot = scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>')
        
        langs = []
        if 'class="espanol"' in article: langs.append('Esp')
        if 'class="latino"' in article: langs.append('Lat')
        if 'class="subtitulado"' in article: langs.append('VOSE')
        
        quality = scrapertools.find_single_match(article, '/beta/([^\.]+)\.png')
        if 'calidad' in quality: # ej: calidad-hd.png, nueva-calidad.png
            quality = quality.replace('-', ' ').replace('calidad', '').strip().capitalize()
        else:
            quality = '' # ej: estreno-sub.png, estreno.png
        
        show, showalt = extraer_show_showalt(title)

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    languages=', '.join(langs), qualities=quality,
                                    contentType='movie', contentTitle=show, contentTitleAlt=showalt, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)')
    if next_page_link == '':
        next_page_link = scrapertools.find_single_match(data, '<div class=\'resppages\'><a href="([^"]+)')
    if next_page_link != '':
        itemlist.append(item.clone( title='>> Página siguiente', url=next_page_link ))

    return itemlist


# Asignar un numérico según las calidades del canal, para poder ordenar por este valor
def puntuar_calidad(txt):
    orden = ['CAM', 'WEB-SCR', 'TS-SCR', 'BLURAY-SCR', 'HD', 'HD-RIP', 'DVD-RIP', 'BLURAY-RIP', 'HD 720p', 'HD 1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1

def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'fcom': return 'fembed'
    elif servidor in ['mp4', 'api', 'drive']: return 'gvideo'
    else: return servidor

def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    matches = scrapertools.find_multiple_matches(data, "<tr id='link-[^']+'>(.*?)</tr>")
    for enlace in matches:
        if 'Obtener</a>' in enlace: continue
        # ~ logger.debug(enlace)

        url = scrapertools.find_single_match(enlace, " href='([^']+)")
        servidor = scrapertools.find_single_match(enlace, " alt='([^'.]+)")
        if not servidor: servidor = scrapertools.find_single_match(enlace, "domain=([^'.]+)")
        servidor = corregir_servidor(servidor.strip().lower())
        uploader = scrapertools.find_single_match(enlace, "author/[^/]+/'>([^<]+)</a>")
        tds = scrapertools.find_multiple_matches(enlace.replace('https://static.cinetux.to/', '/'), 'data-lazy-src="/assets/img/([^\.]*)')
        if tds:
            quality = tds[1]
            lang = tds[2]
        else:
            quality = scrapertools.find_single_match(enlace, "<strong class='quality'>([^<]+)")
            lang = scrapertools.find_single_match(enlace, "<td>([^<]+)")

        if not servidor: continue
        if 'Descargar</a>' in enlace and servidor not in ['mega', 'gvideo']: continue # descartar descargas directas menos Mega y Gvideo
        # ~ logger.debug('%s %s %s %s' % (servidor, quality, lang, enlace))
        
        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, 
                              title = '', url = url,
                              language = IDIOMAS.get(lang,lang), quality = quality, quality_num = puntuar_calidad(quality), other = uploader
                       ))


    matches = scrapertools.find_multiple_matches(data, '<li id="player-option-\d+"(.*?)</li>')
    if matches:
        entrecomillado = '"([^"]+)'
    else:
        matches = scrapertools.find_multiple_matches(data, "<li id='player-option-\d+'(.*?)</li>")
        entrecomillado = "'([^']+)"
    for enlace in matches:
        # ~ logger.debug(enlace)

        dtype = scrapertools.find_single_match(enlace, 'data-type=%s' % entrecomillado)
        dpost = scrapertools.find_single_match(enlace, 'data-post=%s' % entrecomillado)
        dnume = scrapertools.find_single_match(enlace, 'data-nume=%s' % entrecomillado)
        tds = scrapertools.find_multiple_matches(enlace, 'data-lazy-src=".*?/assets/img/([^\.]+)')
        if len(tds) != 2 or not dtype or not dpost or not dnume: continue
        lang = tds[0].replace('3', '')
        servidor = tds[1]
        if servidor == 'cinetux': continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = corregir_servidor(servidor.strip().lower()),
                              title = '', dtype = dtype, dpost = dpost, dnume = dnume, referer = item.url,
                              language = IDIOMAS.get(lang, lang) #, other = tds[1]
                       ))

    # ~ if len(itemlist) > 0: itemlist = servertools.get_servers_itemlist(itemlist) # para corregir la url con los patrones del server

    return itemlist

def extraer_video(item, data):
    itemlist = []
    # ~ logger.debug(data)
    idvideo = scrapertools.find_single_match(data, 'src="([^"]+)').split('#')
    if len(idvideo) == 2:
        if 'ok.ru/videoembed/' in data:
            itemlist.append(item.clone( url='https://ok.ru/videoembed/' + idvideo[1], server='okru' ))
        elif 'drive.google.com' in data:
            # ~ itemlist.append(item.clone( url='https://drive.google.com/file/d/' + idvideo[1] + '/preview', server='gvideo' ))
            itemlist.append(item.clone( url='https://docs.google.com/get_video_info?docid=' + idvideo[1], server='gvideo' ))
        else:
            itemlist.append(item.clone( url='https://' + idvideo[1], server='gvideo' ))
    return itemlist

def play(item):
    logger.info("play: %s" % item.url)
    itemlist = []

    if item.url:
        data = do_downloadpage(item.url)
        # ~ logger.debug(data)
        new_url = scrapertools.find_single_match(data, '<a id="link"[^>]* href="([^"]+)')
        if new_url: 
            if '&url=' in new_url: new_url = new_url.split('&url=')[1]
            if 'cinetux.me' in new_url:
                data = do_downloadpage(new_url)
                # ~ logger.debug(data)
                new_url = scrapertools.find_single_match(data, "<a class='cta' href='([^']+)")
                if new_url: 
                    itemlist.append(item.clone( server='', url=new_url ))
                    itemlist = servertools.get_servers_itemlist(itemlist) # para corregir la url con los patrones del server
                else:
                    itemlist = extraer_video(item, data)
            else:
                new_url = servertools.normalize_url(item.server, new_url)
                itemlist.append(item.clone( url=new_url ))

    else:
        post = urllib.urlencode( {'action': 'doo_player_ajax', 'post': item.dpost, 'nume': item.dnume, 'type': item.dtype} )
        data = do_downloadpage(CHANNEL_HOST + 'wp-admin/admin-ajax.php', post=post, headers={'Referer':item.referer})
        # ~ logger.debug(data)
        new_url = scrapertools.find_single_match(data, "src='([^']+)'")
        if new_url: 
            if 'cinetux.me' in new_url:
                data = do_downloadpage(new_url)
                # ~ logger.debug(data)
                itemlist = extraer_video(item, data)
            else:
                itemlist.append(item.clone( url=new_url, server=servertools.get_server_from_url(new_url) ))

    return itemlist



def busqueda(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    # ~ logger.debug(data)

    patron = '<article>(.*?)</article>'
    matches = scrapertools.find_multiple_matches(data, patron)
    for article in matches:

        thumb, title = scrapertools.find_single_match(article, ' src="([^"]+)" alt="([^"]+)')
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        year = scrapertools.find_single_match(article, '<span class="year">(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="contenido">(.*?)</div>'))
        
        show, showalt = extraer_show_showalt(title)

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=show, contentTitleAlt=showalt, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)')
    if next_page_link != '':
        itemlist.append(item.clone( action='busqueda', title='>> Página siguiente', url=next_page_link ))

    return itemlist

def search(item, texto):
    logger.info()

    item.url = CHANNEL_HOST + "?s=" + texto.replace(" ", "+")
    try:
        return busqueda(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
