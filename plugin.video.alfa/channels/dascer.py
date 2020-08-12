# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido

import re
import time
import traceback

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import tmdb
from core import servertools
from core.item import Item
from platformcode import config, logger
from lib import generictools
from channels import filtertools
from channels import autoplay


IDIOMAS = {'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['torrent']

host = 'https://dascer.com/'
domain = 'dascer.com'
channel = 'dascer'
categoria = channel.capitalize()

event = 'tvshow'
session = 'episode'
null = None
thumb_sports = 'https://dascer.com/wp-content/uploads/2019/11/vettel_victory.jpg'
enlace_void = ['Indycar', 'Nascar', 'Dakar', 'WEC']

timeout = config.get_setting('timeout_downloadpage', channel)
filter_languages = config.get_setting('filter_languages', channel)              # Filtrado de idiomas?


def mainlist(item):
    logger.info()
    
    itemlist = []

    
    thumb_novedades = get_thumb("on_the_air.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    # obtenemos el bloque con las cabeceras de deportes
    patron = '<nav role="navigation"\s*class="[^"]+">\s*<ul\s*id="[^"]+"\s*class="elementor-nav-menu">(.*?)<\/ul>\s*<\/nav>'
    data, success, code, item, itemlist = generictools.downloadpage(host, timeout=timeout,  s2=False, 
                                          patron=patron, item=item, itemlist=[])    # Descargamos la página
    data = scrapertools.find_single_match(data, patron)
    
    if success and data:
        # Ponemos el enlace para Novedades
        itemlist.append(Item(channel=item.channel, title="Novedades", action="listado", 
                        url=host, thumbnail=thumb_novedades, extra="deportes", extra2="novedades"))
        
        # Obtenemos el enlace para cada Deporte
        patron = '<li\s*class="[^"]+">\s*<a\s*href="([^"]+)".*?>(.*?)<\s*\/a><\/li>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        
        #logger.debug(patron)
        #logger.debug(matches)
        #logger.debug(data)
        
        for url, sport in matches:
            if sport in enlace_void:
                continue
            itemlist.append(Item(channel=item.channel, title=sport, action="listado", 
                        url=url, thumbnail=thumb_sports, extra="deportes"))
                        
        # Configuración del Canal y de Autoplay
        itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", 
                        folder=False, thumbnail=thumb_separador))
        itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", 
                        thumbnail=thumb_settings))

        autoplay.show_option(item.channel, itemlist)                            #Activamos Autoplay

    return itemlist
    
    
def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return


def listado(item):                                                              # Listado principal
    logger.info()
    
    itemlist = []
    matches = []
    logos = {'Fórmula 1': '/f1-logo', 'Fórmula 2': '/f2-', 'Fórmula E': '/fe-', 'MotoGP': '/moto-gp', 'Moto2': '/moto2', 'Moto3': '/moto3'}
    item.category = categoria

    #logger.debug(item)
    
    cnt_tot = 30                                                                # Poner el num. máximo de items por página
    cnt_title = 0                                                               # Contador de líneas insertadas en Itemlist
    cnt_offset = 0                                                              # offset para cnt_title en searchs
    curr_page = 1
    last_page = 999
    
    inicio = time.time()                                    # Controlaremos que el proceso no exceda de un tiempo razonable
    fin = inicio + 5                                                            # Después de este tiempo pintamos (segundos)
    timeout_search = timeout * 2                                                # Timeout para descargas

    next_page_url = item.url
    # Máximo num. de líneas permitidas por TMDB. Máx de 5 segundos por Itemlist para no degradar el rendimiento
    while (next_page_url and cnt_title < cnt_tot and curr_page <= last_page and fin > time.time()) or item.matches:
    
        # Descarga la página
        data = ''
        cnt_match = 0                                                           # Contador de líneas procesadas de matches
        
        if item.extra2 == 'novedades':
            patron = '<div\s*class="elementor-widget-container">\s*<div\s*class='
            patron += '"elementor-image">\s*<a\s*href="([^"]+)">\s*<img\s*(?:width="[^"]+"\s*'
            patron += 'height="[^"]+"\s*)?src="([^"]+)"\s*class="attachment-medium_large\s*'
            patron += 'size-medium_large"\s*alt="[^"]*"\s*srcset=.*?<h4\s*class='
            patron += '"elementor-heading[^>]+>\s*<a\s*href="[^"]+">\s*(.*?)\s*<\/a>\s*<\/h4>'
        else:
            patron = '<article\s*class="[^>]+>\s*<div\s*class="elementor-post__card">\s*'
            patron += '<a\s*class="[^"]+"\s*href="([^"]+)"\s*>\s*<div\s*class='
            patron += '"elementor-post__thumbnail"\s*>\s*<\s*img.*?src="([^"]+)".*?'
            patron += '<h3\s*class="elementor-post__title"\s*>\s*<a href="[^"]+"\s*>'
            patron += '\s*(.*?)\s*<\/a>\s*<\/h3>\s*<\/div>\s*<\/div>\s*<\/article>'
        
        if not item.matches:                                                    # si no viene de una pasada anterior, descargamos
            data, success, code, item, itemlist = generictools.downloadpage(next_page_url, 
                                          timeout=timeout_search, s2=False, patron=patron, 
                                          item=item, itemlist=itemlist)         # Descargamos la página)
            
            # Verificamos si se ha cargado una página correcta
            curr_page += 1                                                      # Apunto ya a la página siguiente
            if not data or not success:                                         # Si la web está caída salimos sin dar error
                if len(itemlist) > 1:                                           # Si hay algo que pintar lo pintamos 
                    last_page = 0
                    break
                return itemlist                                                 # Si no hay nada más, salimos directamente
        
        # Comprobar si hay más páginas
        patron_page = '<a\s*class="page-numbers[^"]+"\s*href="([^"]+)">Siguiente'
        if scrapertools.find_single_match(data, patron_page):
            next_page_url = scrapertools.find_single_match(data, patron_page)
        else:
            next_page_url = ''

        if not item.matches:                                                    # De pasada anterior?
            matches = re.compile(patron, re.DOTALL).findall(data)
        else:
            matches = item.matches
            del item.matches
            
        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)
        
        # Iniciamos el Plot y marcamos TMDB como no usable
        item.contentPlot = '[COLOR gold][B]%s[/B][/COLOR]%s\n\n' % (item.title, item.channel_sufix)     #iniciamos el Plot con el Deporte
        item.from_title = '%s - ' % item.title
        item.infoLabels['tmdb_id'] = null

        #Empezamos el procesado de matches
        for scrapedurl, scrapedthumb, scrapedtitle in matches:
            #Generamos una copia de Item para trabajar sobre ella
            item_local = item.clone()
            
            cnt_match += 1
            
            title = scrapedtitle
            title = scrapertools.remove_htmltags(title).rstrip('.')             # Removemos Tags del título
            title = title.replace("á", "a").replace("é", "e").replace("í", "i")\
                    .replace("ó", "o").replace("ú", "u").replace("ü", "u")\
                    .replace("ï¿½", "ñ").replace("Ã±", "ñ").replace("&#8217;", "'")\
                    .replace("&amp;", "&")
            
            cnt_title += 1                                                      # Incrementamos el contador de entradas válidas
           
            # Procesamos idiomas
            item_local.language = []                                            #creamos lista para los idiomas
            if not item_local.language:
                item_local.language = ['CAST']                                  # [CAST] por defecto
                
            # Procesamos Calidad
            if not item_local.quality:
                item_local.quality = 'HDTV'
                
            item_local.thumbnail = scrapedthumb                                 #iniciamos thumbnail
            item_local.contentThumbnail = scrapedthumb                          #iniciamos thumbnail
            item_local.infoLabels['fanart'] = scrapedthumb                      #iniciamos Fanart
            
            # Para Novedades buscamos el Deporte en los thumbs
            if item_local.extra2 == 'novedades':
                for sport, logo in list(logos.items()):
                    if logo in item_local.thumbnail.lower():
                        item_local.contentPlot = '[COLOR gold][B]%s[/B][/COLOR]%s\n\n' % (sport, item.channel_sufix)
                        item_local.from_title = '%s - ' % sport
                        break
            
            item_local.url = scrapedurl                                         #iniciamos la url
            item_local.url_tvshow = item_local.url

            # Guardamos los formatos para películas
            item_local.contentType = event
            item_local.action = "episodios"

            year = scrapertools.find_single_match(title, '\d{4}')
            if year:
                item_local.infoLabels['year'] = int(year)
                item_local.infoLabels['aired'] = str(year)

            title = re.sub(r'(?i)TV|Online|(4k-hdr)|(fullbluray)|4k| - 4k|(3d)|miniserie|\d{4}', '', title).strip()
            item_local.title = title.strip().lower().title()
            item_local.contentTitle = item_local.title
            item_local.from_title += item_local.title

            #Ahora se filtra por idioma, si procede, y se pinta lo que vale
            if filter_languages > 0:                                            #Si hay idioma seleccionado, se filtra
                itemlist = filtertools.get_link(itemlist, item_local, list_language)
            else:
                itemlist.append(item_local.clone())                             #Si no, pintar pantalla
            
            cnt_title = len(itemlist) - cnt_offset                              # Recalculamos los items después del filtrado
            if cnt_title >= cnt_tot and (len(matches) - cnt_match) + cnt_title > cnt_tot * 1.3:     #Contador de líneas añadidas
                break
            
            #logger.debug(item_local)
    
        matches = matches[cnt_match:]                                           # Salvamos la entradas no procesadas

    # Enlace a Temporadas anteriores
    if item.extra2 != 'novedades':
        patron = '<h2\s*class=".*?<a\s*href="([^"]+)"\s*class="'
        url_temp_anteriores = scrapertools.find_single_match(data, patron)
        itemlist.insert(0,item.clone(title="Temporadas anteriores", url=url_temp_anteriores, 
                        action="temporadas_anteriores", thumbnail=thumb_sports, url_tvshow = url_temp_anteriores, 
                        language=['CAST'], quality = 'HDTV'))

    return itemlist

    
def temporadas_anteriores(item):
    patron = '<h2\s*style="[^>]+>\s*<a\s*href="([^"]+)".*?>\s*<span\s*style="[^>]+>\s*'
    patron += '<strong>\s*(.*?)\s*<\/strong>\s*<\/span>\s*<\/a>\s*<\/h2>'
    data, success, code, item, itemlist = generictools.downloadpage(item.url, timeout=timeout,  s2=False, 
                                          patron=patron, item=item, itemlist=[])    # Descargamos la página
    
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        item_local = item.clone()
        item_local.action = "findvideos"
        item_local.contentType = session
        item_local.contentPlot += '[B]%s[/B]\n\n' % scrapedtitle
        item_local.url_enlaces = [(scrapedurl, 'Torrent')]
        
        year = scrapertools.find_single_match(scrapedtitle, '\d{4}')
        if year:
            item_local.infoLabels['year'] = int(year)
            item_local.infoLabels['aired'] = str(year)
        item_local.title = scrapedtitle
        item_local.contentTitle = item_local.title
        item_local.from_title = item_local.title
        
        itemlist.append(item_local.clone())
    
    return itemlist
    
    
def findvideos(item):
    logger.info()
    
    itemlist = []
    itemlist_t = []                                                             #Itemlist total de enlaces
    itemlist_f = []                                                             #Itemlist de enlaces filtrados
    matches = []

    #logger.debug(item)

    #Ahora tratamos los enlaces .torrent con las diferentes calidades
    for scrapedurl, scrapedserver in item.url_enlaces:

        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()

        item_local.url = scrapedurl
        item_local.server = scrapedserver.lower()
        item_local.action = "play" 
        
        #Buscamos tamaño en el archivo .torrent
        size = ''
        if item_local.server == 'torrent' and not size and not item_local.url.startswith('magnet:'):
            size = generictools.get_torrent_size(item_local.url) #              Buscamos el tamaño en el .torrent desde la web

        if size:
            size = size.replace('GB', 'G·B').replace('Gb', 'G·b').replace('MB', 'M·B')\
                        .replace('Mb', 'M·b').replace('.', ',')
            item_local.torrent_info = '%s, ' % size                             #Agregamos size
        if item_local.url.startswith('magnet:') and not 'Magnet' in item_local.torrent_info:
            item_local.torrent_info += ' Magnet'
        if item_local.torrent_info:
            item_local.torrent_info = item_local.torrent_info.strip().strip(',')
            if not item.unify:
                item_local.torrent_info = '[%s]' % item_local.torrent_info

        #Ahora pintamos lo enlaces
        item_local.title = '[[COLOR yellow]?[/COLOR]] [COLOR yellow][%s][/COLOR] ' %item_local.server.capitalize() \
                        + '[COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR] %s' % \
                        (item_local.quality, str(item_local.language), \
                        item_local.torrent_info)

        # Verificamos enlaces
        if item_local.server != 'torrent':
            if config.get_setting("hidepremium"):                               #Si no se aceptan servidore premium, se ignoran
                if not servertools.is_server_enabled(item_local.server):
                    continue
            devuelve = servertools.findvideosbyserver(item_local.url, item_local.server)    #existe el link ?
            if not devuelve:
                continue
            item_local.url = devuelve[0][1]
            item_local.alive = servertools.check_video_link(item_local.url, item_local.server, timeout=timeout)     #activo el link ?
            if 'NO' in item_local.alive:
                continue
        else:
            if not size or 'Magnet' in size:
                item_local.alive = "??"                                         #Calidad del link sin verificar
            elif 'ERROR' in size:
                item_local.alive = "no"                                         #Calidad del link en error?
                continue
            else:
                item_local.alive = "ok"                                         #Calidad del link verificada
        
        itemlist_t.append(item_local.clone())                                   #Pintar pantalla, si no se filtran idiomas
        
        # Requerido para FilterTools
        if config.get_setting('filter_languages', channel) > 0:                 #Si hay idioma seleccionado, se filtra
            itemlist_f = filtertools.get_link(itemlist_f, item_local, list_language)  #Pintar pantalla, si no está vacío

    if len(itemlist_f) > 0:                                                     #Si hay entradas filtradas...
        itemlist.extend(itemlist_f)                                             #Pintamos pantalla filtrada
    else:                                                                       
        if config.get_setting('filter_languages', channel) > 0 and len(itemlist_t) > 0: #Si no hay entradas filtradas ...
            thumb_separador = get_thumb("next.png")                             #... pintamos todo con aviso
            itemlist.append(Item(channel=item.channel, url=host, 
                        title="[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", 
                        thumbnail=thumb_separador, folder=False))
        itemlist.extend(itemlist_t)                                             #Pintar pantalla con todo si no hay filtrado
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)                                              #Lanzamos Autoplay
    
    return itemlist
    

def episodios(item):
    logger.info()
    
    itemlist = []
    item.url_enlaces = []
    season = 1
    episode = 1
    download_connector = config.get_setting('download_connector', channel, default=0)
    download_connectors = [
                           "Torrent",
                           "Ok",
                           "Mega",
                           "UpStream"
                          ]
    try:
        download_preference = download_connectors[download_connector]
    except:
        download_preference = download_connectors[0]
        logger.error(traceback.format_exc(1))
    
    #logger.debug(item)

    # Descargamos evento
    data, success, code, item, itemlist = generictools.downloadpage(item.url, timeout=timeout,  s2=False, 
                                          item=item, itemlist=[])               # Descargamos la página

    if not success:
        return itemlist

    item.contentPlot = '%s[B]%s %s[/B]\n\n' % (item.contentPlot, item.title, item.infoLabels['aired'])
    
    # Obtenemos el thumb del evento
    patron = '<div class="elementor-image">\s*<img\s*width="[^"]*"\s*height="[^"]*"\s*src="([^"]+)"'
    if scrapertools.find_single_match(data, patron):
        item.thumbnail = scrapertools.find_single_match(data, patron)
        item.contentThumbnail = item.thumbnail
    
    # Localizamos los datos del Evento
    patron = '(?i)<h2\s*class="elementor-heading-title[^>]+>\s*CIRCUITO\s*DE\s*(.*?)\s*<\/h2>'
    if scrapertools.find_single_match(data, patron):                            # Circuito
        item.contentPlot += '[COLOR yellow][B]%s:[/B][/COLOR]\n' % scrapertools.find_single_match(data, patron).capitalize()
    patron = '<tr><th\s*scope="row">(.*?)<\/th><td colspan[^<]+>(.*?)<\/td><\/tr>'  # Detalles del Circuito
    datos_evento = re.compile(patron, re.DOTALL).findall(data)
    for clave, valor in datos_evento:
        if 'Vuelta' not in clave:
            item.contentPlot += '- %s: %s\n' % (clave, valor)
        else:
            patron = '(.*?)(?:<br\s*\/>\s*)?<span.*?<\/span>(.*?)(?:<br\s*\/>\s*)?<span.*?<\/span>(.*?)(?:<br\s*\/>\s*)?$'
            if scrapertools.find_single_match(valor, patron):
                tiempo, deportista, equipo = scrapertools.find_single_match(valor, patron)
                tiempo = scrapertools.remove_htmltags(tiempo)                   # Removemos Tags del título
                item.contentPlot += '- %s: %s, %s, %s\n' % (clave, tiempo, deportista, equipo)

    # Procesamos los eventos
    patron = '<div[^>]+>(?:\s*<p>)?\s*<iframe\s*[^>]+>\s*<\/iframe>(?:\s*<\/p>)?\s*'
    patron += '<p\s*style[^>]+>\s*<a\s*href="([^"]+)"\s*(?:target[^>]+)?>\s*'
    patron +='(?:Descargar \w+)?\s*(.*?)\s*<\/a><\/p><\/div>'                   # Una sola sesión
    if scrapertools.find_single_match(data, patron):
        item_local = item.clone()
        item_local.url_enlaces = [(scrapertools.find_single_match(data, patron))]
        item_local.action = "findvideos"
        item_local.contentType = session
        return findvideos(item_local)

    patron = '<div\s*id="elementor-tab-title[^>]+>.*?<\/span>\s*<a\s*href="[^"]*"\s*(.*?)\s*<\/div>\s*<\/div>'      # Varias sesiones
    eventos = re.compile(patron, re.DOTALL).findall(data)
    
    #logger.debug("PATRON: " + patron)
    #logger.debug(eventos)
    #logger.debug(data)
    
    for actividad in eventos:
        item_local = item.clone()
        item_local.action = "findvideos"
        item_local.contentType = session
        item_local.url_enlaces = []

        patron = 'class="elementor-toggle-title">(.*?)<\/a>'
        item_local.title = scrapertools.find_single_match(actividad, patron)
        item_local.contentTitle = item_local.title
        
        if not item_local.title:
            return itemlist

        # Enlace por defecto de Okru
        patron = '(?:<p>)?<iframe.*?src="([^"]+)"[^<]+><\/iframe>'
        enlace = scrapertools.find_single_match(actividad, patron)
        if enlace and 'ok.ru' in enlace:
            if not enlace.startswith('http'):
                enlace = 'https:' + enlace
            item_local.url_enlaces.append((enlace, 'Okru'))
        
        # Otros enlaces
        patron = '(?:<p>)?<a\s*href="([^"]+)"[^>]*>(?:\s*Descargar\s*\w+)?\s*(.*?)\s*<\/a>'
        enlaces_descargas = re.compile(patron, re.DOTALL).findall(actividad)
        
        for enlace, server in enlaces_descargas:
            if enlace and server:
                if not enlace.startswith('http'):
                    enlace = 'https:' + enlace
                if server == download_preference:
                    item_local.url_enlaces.insert(0, (enlace, server))
                else:
                    item_local.url_enlaces.append((enlace, server))
        
        item_local.contentSeason = season
        item_local.contentEpisodeNumber = episode
        episode += 1
        itemlist.append(item_local.clone())

    return itemlist

    
def search(item, texto):
    logger.info()
    
    return newest('deportes')
    
    texto = texto.replace(" ", "+")
    
    try:
        item.url = item.url % texto
        item.extra = 'search'

        if texto:
            return listado(item)
        else:
            return []
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))
        return []
 
 
def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()

    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel
    
    try:
        if categoria in ['deportes']:
            item.url = host
            item.extra = "deportes"
            item.extra2 = "novedades"
            item.action = "listado"
            item.channel_sufix = "  [Dascer]"
            itemlist.extend(listado(item))
                
        if ">> Página siguiente" in itemlist[-1].title or "Pagina siguiente >>" in itemlist[-1].title:
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc(1))
        return []

    return itemlist
