# -*- coding: utf-8 -*-

import os
import re
import sys
import urllib
import time

from core import channeltools
from core import httptools
from core import scrapertools
from core import servertools
from core import tmdb
from core.item import Item
from platformcode import config, logger

host = "http://tv-vip.com"

httptools.downloadpage(host)
httptools.downloadpage('%s/video2-prod/s/c' % host, headers={'Referer': host})

def mainlist(item):
    logger.info()
    item.viewmode = "movie"
    itemlist = []

    data = httptools.downloadpage(host + "/json/playlist/home/index.json")

    itemlist.append(Item(channel=item.channel, title="Películas", action="submenu",
                         thumbnail=host+"/json/playlist/peliculas/thumbnail.jpg",
                         fanart=host+"/json/playlist/peliculas/background.jpg"))
    itemlist.append(Item(channel=item.channel, title="Series", action="submenu",
                         thumbnail=host+"/json/playlist/series/poster.jpg",
                         fanart=host+"/json/playlist/series/background.jpg"))
    itemlist.append(Item(channel=item.channel, title="Versión Original", action="entradasconlistas",
                         url=host+"/json/playlist/version-original/index.json",
                         thumbnail=host+"/json/playlist/version-original/thumbnail.jpg",
                         fanart=host+"/json/playlist/version-original/background.jpg"))
    itemlist.append(Item(channel=item.channel, title="Documentales", action="entradasconlistas",
                         url=host+"/json/playlist/documentales/index.json",
                         thumbnail=host+"/json/playlist/documentales/thumbnail.jpg",
                         fanart=host+"/json/playlist/documentales/background.jpg"))
    itemlist.append(Item(channel=item.channel, title="Películas Infantiles", action="entradasconlistas",
                         url=host+"/json/playlist/peliculas-infantiles/index.json",
                         thumbnail=host+"/json/playlist/peliculas-infantiles/thumbnail.jpg",
                         fanart=host+"/json/playlist/peliculas-infantiles/background.jpg"))
    itemlist.append(Item(channel=item.channel, title="Series Infantiles", action="entradasconlistas",
                         url=host+"/json/playlist/series-infantiles/index.json",
                         thumbnail=host+"/json/playlist/series-infantiles/thumbnail.jpg",
                         fanart=host+"/json/playlist/series-infantiles/background.jpg"))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search",
                         thumbnail="http://i.imgur.com/gNHVlI4.png", fanart="http://i.imgur.com/9loVksV.png"))

    return itemlist

def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    if item.title == "Buscar...": item.extra = "local"
    item.url = host + "/video-prod/s/search?q=%s&n=100" % texto
    try:
        return busqueda(item, texto)
        # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def busqueda(item, texto):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).json
    for child in data["objectList"]:
        infolabels = {}
        infolabels['year'] = child['year']
        if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',', '.')
        infolabels['votes'] = child['rateCount']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        if 'playListChilds' not in child:
            infolabels['plot'] = child['description']
            type = "repo"
            fulltitle = child['name']
            title = child['name']
            infolabels['duration'] = child['duration']
            if child['height'] < 720:
               quality = "[B]  [SD][/B]"
            elif child['height'] < 1080:
               quality = "[B]  [720p][/B]"
            elif child['height'] < 2160:
               quality = "[B]  [1080p][/B]"
            elif child['height'] >= 2160:
               quality = "[B]  [4k][/B]"
            if child['name'] == "":
               title = child['id'].rsplit(".", 1)[0]
            else:
               title = child['name']
            if child['year']:
                title += " (" + child['year'] + ")"
            title += quality
        else:
            type = "playlist"
            infolabels['plot'] = "Contiene:\n" + "\n".join(child['playListChilds']) + "\n".join(child['repoChilds'])
            fulltitle = child['id']
            title = "[COLOR red][LISTA][/COLOR] " + child['id'].replace('-', ' ').capitalize() + " ([COLOR gold]" + \
                    str(child['number']) + "[/COLOR])"
        # En caso de búsqueda global se filtran los resultados
        if item.extra != "local":
            if "+" in texto: texto = "|".join(texto.split("+"))
            if not re.search(r'(?i)' + texto, title, flags=re.DOTALL): continue
        url = host + "/json/%s/%s/index.json" % (type, child["id"])
        # Fanart
        if child['hashBackground']:
            fanart = host + "/json/%s/%s/background.jpg" % (type, child["id"])
        else:
            fanart = host + "/json/%s/%s/thumbnail.jpg" % (type, child["id"])
        # Thumbnail
        if child['hasPoster']:
            thumbnail = host + "/json/%s/%s/poster.jpg" % (type, child["id"])
        else:
            thumbnail = fanart
        if type == 'playlist':
            itemlist.insert(0, Item(channel=item.channel, action="entradasconlistas", title=title,
                                    url=url, thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle,
                                    infoLabels=infolabels, viewmode="movie_with_plot", folder=True))
        else:
            itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url,
                                thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, contentTitle=fulltitle,
                                context="05", infoLabels=infolabels, viewmode="movie_with_plot", folder=True))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    if item.title == "Series":
        itemlist.append(Item(channel=item.channel, title="Nuevos Capítulos", action="episodios",
                             url=host+"/json/playlist/nuevos-capitulos/index.json",
                             thumbnail=host+"/json/playlist/nuevos-capitulos/background.jpg",
                             fanart=host+"/json/playlist/nuevos-capitulos/background.jpg"))
        itemlist.append(Item(channel=item.channel, title="Más Vistas", action="series",
                             url=host+"/json/playlist/top-series/index.json",
                             thumbnail=host+"/playlist/top-series/thumbnail.jpg",
                             fanart=host+"/json/playlist/top-series/background.jpg",
                             extra1="Series"))
        itemlist.append(Item(channel=item.channel, title="Últimas Series", action="series",
                             url=host+"/json/playlist/series/index.json",
                             thumbnail=item.thumbnail, fanart=item.fanart, extra1="Series"))
        itemlist.append(Item(channel=item.channel, title="Lista de Series A-Z", action="series",
                             url=host+"/json/playlist/series/index.json", thumbnail=item.thumbnail,
                             fanart=item.fanart, extra1="Series"))
    else:
        itemlist.append(Item(channel=item.channel, title="Novedades", action="entradas",
                             url=host+"/json/playlist/000-novedades/index.json",
                             thumbnail=host+"/json/playlist/ultimas-peliculas/thumbnail.jpg",
                             fanart=host+"/json/playlist/ultimas-peliculas/background.jpg"))
        itemlist.append(Item(channel=item.channel, title="Más vistas", action="entradas",
                             url=host+"/json/playlist/peliculas-mas-vistas/index.json",
                             thumbnail=host+"/json/playlist/peliculas-mas-vistas/thumbnail.jpg",
                             fanart=host+"/json/playlist/peliculas-mas-vistas/background.jpg"))
        itemlist.append(Item(channel=item.channel, title="Categorías", action="cat",
                             url=host+"/json/playlist/peliculas/index.json",
                             thumbnail=item.thumbnail, fanart=item.fanart))
        itemlist.append(Item(channel=item.channel, title="Películas 3D", action="entradasconlistas",
                             url=host+"/json/playlist/3D/index.json",
                             thumbnail=host+"/json/playlist/3D/thumbnail.jpg",
                             fanart=host+"/json/playlist/3D/background.jpg"))
    return itemlist


def cat(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).json
    exception = ["peliculas-mas-vistas", "ultimas-peliculas"]
    for child in data["sortedPlaylistChilds"]:
        if child["id"] not in exception:
            url = host + "/json/playlist/%s/index.json" % child["id"]
            # Fanart
            if child['hashBackground']:
                fanart = host + "/json/playlist/%s/background.jpg" % child["id"]
            else:
                fanart = host + "/json/playlist/%s/thumbnail.jpg" % child["id"]
            # Thumbnail
            thumbnail = host + "/json/playlist/%s/thumbnail.jpg" % child["id"]
            title = child['id'].replace('-', ' ').capitalize().replace("Manga", "Animación/Cine Oriental")
            title += " ([COLOR gold]" + str(child['number']) + "[/COLOR])"
            itemlist.append(
                     Item(channel=item.channel, action="entradasconlistas", title=title, url=url,
                          thumbnail=thumbnail, fanart=fanart, folder=True))
    return itemlist


def entradas(item):
    logger.info()
    itemlist = []
    infolabels = {}
    if item.title == "Nuevos Capítulos":
        context = "5"
    else:
        context = "05"
    data = httptools.downloadpage(item.url).json
    for child in data["sortedRepoChilds"]:
        infolabels['year'] = child['year']
        url = host + "/json/repo/%s/index.json" % child["id"]
        thumbnail = ""
        if child['hasPoster']:
            thumbnail = host + "/json/repo/%s/poster.jpg" % child["id"]
        if child['height'] < 720:
            quality = "[B]  [SD][/B]"
        elif child['height'] < 1080:
            quality = "[B]  [720p][/B]"
        elif child['height'] < 2160:
            quality = "[B]  [1080p][/B]"
        elif child['height'] >= 2160:
            quality = "[B]  [4k][/B]"
        fulltitle = child['name']
        title = child['name']
        if child['year']:
            title += " (" + child['year'] + ")"
        title += quality
        itemlist.append(Item(channel=item.channel, action="findvideos", server="", title=title, url=url,
                             thumbnail=thumbnail, infoLabels=infolabels,
                             contentTitle=fulltitle, context=context, quality=quality))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    return itemlist


def entradasconlistas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).json
    # Si hay alguna lista
    contentSerie = False
    contentList = False
    if data['playListChilds']:
        itemlist.append(Item(channel=item.channel, title="**LISTAS**", action="", text_color="red", text_blod=True,
                             folder=False))
        for child in data['sortedPlaylistChilds']:
            infolabels = {}
            infolabels['plot'] = "Contiene:\n" + "\n".join(child['playListChilds']) + "\n".join(child['repoChilds'])
            if child['seasonNumber'] and not contentList and re.search(r'(?i)temporada', child['id']):
                infolabels['season'] = child['seasonNumber']
                contentSerie = True
            else:
                contentSerie = False
                contentList = True
            title = child['id'].replace('-', ' ').capitalize() + " ([COLOR gold]" + str(child['number']) + "[/COLOR])"
            url = host + "/json/playlist/%s/index.json" % child["id"]
            thumbnail = host + "/json/playlist/%s/thumbnail.jpg" % child["id"]
            if child['hashBackground']:
                fanart = host + "/json/playlist/%s/background.jpg" % child["id"]
            else:
                fanart = host + "/json/playlist/%s/thumbnail.jpg" % child["id"]
            itemlist.append(Item(channel=item.channel, action="entradasconlistas", title=title,
                                 url=url, thumbnail=thumbnail, fanart=fanart, fulltitle=child['id'],
                                 infoLabels=infolabels, viewmode="movie_with_plot"))
    else:
        contentList = True

    if data["sortedRepoChilds"] and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="**VÍDEOS**", action="", text_color="blue", text_blod=True,
                             folder=False))

    for child in data["sortedRepoChilds"]:
        infolabels = {}
        infolabels['plot'] = child['description']
        infolabels['year'] = data['year']
        if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',', '.')
        infolabels['votes'] = child['rateCount']
        infolabels['duration'] = child['duration']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        url = host + "/json/repo/%s/index.json" % child["id"]
        # Fanart
        if child['hashBackground']:
            fanart = host + "/json/repo/%s/background.jpg" % child["id"]
        else:
            fanart = host + "/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']:
            thumbnail = host + "/json/repo/%s/poster.jpg" % child["id"]
        else:
            thumbnail = fanart
        if child['height'] < 720:
            quality = "[B]  [SD][/B]"
        elif child['height'] < 1080:
            quality = "[B]  [720p][/B]"
        elif child['height'] < 2160:
            quality = "[B]  [1080p][/B]"
        elif child['height'] >= 2160:
            quality = "[B]  [4k][/B]"
        fulltitle = child['name']
        if child['name'] == "":
            title = child['id'].rsplit(".", 1)[0]
        else:
            title = child['name']
        if child['year']:
            title += " (" + child['year'] + ")"
        title += quality
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url,
                             thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                             contentTitle=fulltitle, context="05", viewmode="movie_with_plot", folder=True))
    # Se añade item para añadir la lista de vídeos a la videoteca
    if data['sortedRepoChilds'] and len(itemlist) > 0 and contentList:
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, text_color="green", title="Añadir esta lista a la videoteca",
                                 url=item.url, action="listas"))
    elif contentSerie:
        if config.get_videolibrary_support():
            itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", url=item.url,
                                 action="series_library", fulltitle=data['name'], show=data['name'],
                                 text_color="green"))

    return itemlist


def series(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).json
    exception = ["top-series", "nuevos-capitulos"]
    for child in data["sortedPlaylistChilds"]:
        if child["id"] not in exception:
            infolabels = {}
            infolabels['plot'] = child['description']
            infolabels['year'] = child['year']
            if child['tags']: infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
            infolabels['rating'] = child['rate'].replace(',', '.')
            infolabels['votes'] = child['rateCount']
            if child['cast']: infolabels['cast'] = child['cast'].split(",")
            infolabels['director'] = child['director']
            infolabels['mediatype'] = "episode"
            if child['seasonNumber']: infolabels['season'] = child['seasonNumber']
            url = host + "/json/playlist/%s/index.json" % child["id"]
            # Fanart
            if child['hashBackground']:
                fanart = host + "/json/playlist/%s/background.jpg" % child["id"]
            else:
                fanart = host + "/json/playlist/%s/thumbnail.jpg" % child["id"]
            # Thumbnail
            if child['hasPoster']:
                thumbnail = host + "/json/playlist/%s/poster.jpg" % child["id"]
            else:
                thumbnail = fanart
            if item.extra1 == "Series":
                if child['name'] != "":
                    fulltitle = child['name']
                    fulltitle = fulltitle.replace('-', '')
                    title = child['name'] + " (" + child['year'] + ")"
                else:
                    title = fulltitle = child['id'].capitalize()
                if "Temporada" not in title:
                    title += "     [Temporadas: [COLOR gold]" + str(child['numberOfSeasons']) + "[/COLOR]]"
                elif item.title == "Más Vistas":
                    title = title.replace("- Temporada", "--- Temporada")
            else:
                if data['name'] != "":
                    fulltitle = data['name']
                    if child['seasonNumber']:
                        title = data['name'] + " --- Temporada " + child['seasonNumber'] + \
                               "  [COLOR gold](" + str(child['number']) + ")[/COLOR]"
                    else:
                        title = child['name'] + "  [COLOR gold](" + str(child['number']) + ")[/COLOR]"
                else:
                    fulltitle = data['id']
                    if child['seasonNumber']:
                        title = data['id'].capitalize() + " --- Temporada " + child['seasonNumber'] + \
                              "  [COLOR gold](" + str(child['number']) + ")[/COLOR]"
                    else:
                        title = data['id'].capitalize() + "  [COLOR gold](" + str(child['number']) + ")[/COLOR]"

            if not child['playListChilds']:
                action = "episodios"
            else:
                action = "series"
            itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, server="",
                                 thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                                 contentSerieName=fulltitle, context="25", viewmode="movie_with_plot", folder=True))
            if len(itemlist) == len(data["sortedPlaylistChilds"]) and item.extra1 != "Series":
                itemlist.sort(key=lambda item: item.title, reverse=True)
                if config.get_videolibrary_support():
                    itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", url=item.url,
                                         action="add_serie_to_library", show=data['name'],
                                         text_color="green", extra="series_library"))
    if item.title == "Últimas Series": return itemlist
    if item.title == "Lista de Series A-Z": itemlist.sort(key=lambda item: item.fulltitle)
    if data["sortedRepoChilds"] and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="**VÍDEOS RELACIONADOS/MISMA TEMÁTICA**", text_color="blue",
                             text_blod=True, action="", folder=False))
    for child in data["sortedRepoChilds"]:
        infolabels = {}
        if child['description']:
            infolabels['plot'] = data['description']
        else:
            infolabels['plot'] = child['description']
        infolabels['year'] = data['year']
        if not child['tags']:
            infolabels['genre'] = ', '.join([x.strip() for x in data['tags']])
        else:
            infolabels['genre'] = ', '.join([x.strip() for x in child['tags']])
        infolabels['rating'] = child['rate'].replace(',', '.')
        infolabels['duration'] = child['duration']
        if child['cast']: infolabels['cast'] = child['cast'].split(",")
        infolabels['director'] = child['director']
        url = host + "/json/repo/%s/index.json" % child["id"]
        if child['hashBackground']:
            fanart = host + "/json/repo/%s/background.jpg" % child["id"]
        else:
            fanart = host + "/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']:
            thumbnail = host + "/json/repo/%s/poster.jpg" % child["id"]
        else:
            thumbnail = fanart
        if child['height'] < 720:
            quality = "[B]  [SD][/B]"
        elif child['height'] < 1080:
            quality = "[B]  [720p][/B]"
        elif child['height'] < 2160:
            quality = "[B]  [1080p][/B]"
        elif child['height'] >= 2160:
            quality = "[B]  [1080p][/B]"
        fulltitle = child['name']
        if child['name'] == "":
            title = child['id'].rsplit(".", 1)[0]
        else:
            title = child['name']
        if child['year']:
            title += " (" + child['year'] + ")"
        title += quality
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url,
                             server="", thumbnail=thumbnail, fanart=fanart, fulltitle=fulltitle, infoLabels=infolabels,
                             contentSerieName=fulltitle, context="25", viewmode="movie_with_plot", folder=True))
    if item.extra == "new":
        itemlist.sort(key=lambda item: item.title, reverse=True)
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    # Redirección para actualización de videoteca
    if item.extra == "series_library":
        itemlist = series_library(item)
        return itemlist
    data = httptools.downloadpage(item.url).json
    # Se prueba un método u otro porque algunas series no están bien listadas
    if data["sortedRepoChilds"]:
        for child in data["sortedRepoChilds"]:
            if item.infoLabels:
                item.infoLabels['duration'] = str(child['duration'])
                item.infoLabels['season'] = str(data['seasonNumber'])
                item.infoLabels['episode'] = str(child['episode'])
                item.infoLabels['mediatype'] = "episode"
            #contentTitle = item.fulltitle + "|" + str(data['seasonNumber']) + "|" + str(child['episode'])
            # En caso de venir del apartado nuevos capítulos se redirige a la función series para mostrar los demás
            if item.title == "Nuevos Capítulos":
                url = host + "/json/playlist/%s/index.json" % child["season"]
                action = "series"
                extra = "new"
            else:
                url = host + "/json/repo/%s/index.json" % child["id"]
                action = "findvideos"
                extra = ""
            if child['hasPoster']:
                thumbnail = host + "/json/repo/%s/poster.jpg" % child["id"]
            else:
                thumbnail = host + "/json/repo/%s/thumbnail.jpg" % child["id"]
            try:
                title = fulltitle = child['name'].rsplit(" ", 1)[0] + " - " + child['name'].rsplit(" ", 1)[1]
            except:
                title = fulltitle = child['id']
            itemlist.append(item.clone(action=action, server="", title=title, url=url, thumbnail=thumbnail,
                                       fanart=item.fanart, fulltitle=fulltitle, contentSerieName=fulltitle, context="35",
                                       viewmode="movie", extra=extra, show=item.fulltitle, folder=True))
    else:
        for child in data["repoChilds"]:
            url = host + "/json/repo/%s/index.json" % child
            if data['hasPoster']:
                thumbnail = host + "/json/repo/%s/poster.jpg" % child
            else:
                thumbnail = host + "/json/repo/%s/thumbnail.jpg" % child
            title = fulltitle = child.capitalize().replace('_', ' ')
            itemlist.append(item.clone(action="findvideos", server="", title=title, url=url, thumbnail=thumbnail,
                                       fanart=item.fanart, fulltitle=fulltitle, contentSerieName=item.fulltitle,
                                       context="25", show=item.fulltitle, folder=True))
    # Opción de añadir a la videoteca en casos de series de una única temporada
    if len(itemlist) > 0 and not "---" in item.title and item.title != "Nuevos Capítulos":
        if config.get_videolibrary_support() and item.show == "":
            if "-" in item.title:
                show = item.title.split('-')[0]
            else:
                show = item.title.split('(')[0]
            itemlist.append(Item(channel=item.channel, title="Añadir esta serie a la videoteca", text_color="green",
                                 url=item.url, action="add_serie_to_library", show=show, extra="series_library"))
    return itemlist


def series_library(item):
    logger.info()
    # Funcion unicamente para añadir/actualizar series a la libreria
    lista_episodios = []
    show = item.show.strip()
    data_serie = httptools.downloadpage(item.url).json
    # Para series que en la web se listan divididas por temporadas
    if data_serie["sortedPlaylistChilds"]:
        for season_name in data_serie["sortedPlaylistChilds"]:
            url_season = host + "/json/playlist/%s/index.json" % season_name['id']
            data = httptools.downloadpage(url_season).json
            if data["sortedRepoChilds"]:
                for child in data["sortedRepoChilds"]:
                    url = host + "/json/repo/%s/index.json" % child["id"]
                    fulltitle = child['name'].rsplit(" ", 1)[0] + " - " + child['name'].rsplit(" ", 1)[1]
                    try:
                        check_filename = scrapertools.get_season_and_episode(fulltitle)
                    except:
                        fulltitle += " " + str(data['seasonNumber']) + "x00"
                    lista_episodios.append(Item(channel=item.channel, action="findvideos", server="",
                                                title=fulltitle, extra=url, url=item.url, fulltitle=fulltitle,
                                                contentTitle=fulltitle, show=show))
            else:
                for child in data["repoChilds"]:
                    url = host + "/json/repo/%s/index.json" % child
                    fulltitle = child.capitalize().replace('_', ' ')
                    try:
                        check_filename = scrapertools.get_season_and_episode(fulltitle)
                    except:
                        fulltitle += " " + str(data['seasonNumber']) + "x00"
                    lista_episodios.append(Item(channel=item.channel, action="findvideos", server="",
                                                title=fulltitle, extra=url, url=item.url, contentTitle=fulltitle, 
                                                fulltitle=fulltitle, show=show))
    # Para series directas de una sola temporada
    else:
        data = data_serie
        if data["sortedRepoChilds"]:
            for child in data["sortedRepoChilds"]:
                url = host + "/json/repo/%s/index.json" % child["id"]
                fulltitle = child['name'].rsplit(" ", 1)[0] + " - " + child['name'].rsplit(" ", 1)[1]
                try:
                    check_filename = scrapertools.get_season_and_episode(fulltitle)
                except:
                    fulltitle += " 1x00"
                lista_episodios.append(Item(channel=item.channel, action="findvideos", server="", title=fulltitle,
                                            contentTitle=fulltitle, url=item.url, extra=url, fulltitle=fulltitle,
                                            show=show))
        else:
            for child in data["repoChilds"]:
                url = host + "/json/repo/%s/index.json" % child
                fulltitle = child.capitalize().replace('_', ' ')
                try:
                    check_filename = scrapertools.get_season_and_episode(fulltitle)
                except:
                    fulltitle += " 1x00"
                lista_episodios.append(Item(channel=item.channel, action="findvideos", server="", title=fulltitle,
                                            contentTitle=fulltitle, url=item.url, extra=url, fulltitle=fulltitle,
                                            show=show))
    return lista_episodios



def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, headers={'Referer': 'http://tv-vip.com/section/000-novedades/'}).json
    profiles = data['profiles']
    for id, values in profiles.items():
        for option in values['servers']:
           quality = values['videoResolution']
           itemlist.append(Item(channel=item.channel, title='Directo' + quality, url=item.url, action='play',
                                s_id=option, uri=values['videoUri'], server='Directo', quality=quality,
                                infoLabels=item.infoLabels))

    return itemlist


def play(item):
    import time
    logger.info()
    itemlist = []
    s = item.s_id['id']
    uri = item.uri
    tt = int(time.time()*1000)
    headers = {'Referer':item.url.replace('/json/repo', '/film').replace('index.json', ''),
               'X-Requested-With': 'XMLHttpRequest'}
    uri_1 = 'http://tv-vip.com/video2-prod/s/uri?uri=/transcoder%s&s=%s' % (uri, s)
    data = httptools.downloadpage(uri_1, headers=headers, forced_proxy=True).json
    b = data['b']
    tt = data['a']['tt']
    mm = data['a']['mm']
    bb = data['a']['bb']

    url = 'http://%s.%s/e/transcoder%s?tt=%s&mm=%s&bb=%s' % (s, b, uri, tt, mm, bb)
    url += "|User-Agent=%s" % httptools.get_user_agent()
    itemlist.append(item.clone(url=url))
    return itemlist


def listas(item):
    logger.info()
    # Para añadir listas a la videoteca en carpeta CINE
    itemlist = []
    data = httptools.downloadpage(item.url).json
    head = header_string + get_cookie_value()
    for child in data["sortedRepoChilds"]:
        infolabels = {}
        # Fanart
        if child['hashBackground']:
            fanart = host + "/json/repo/%s/background.jpg" % child["id"]
        else:
            fanart = host + "/json/repo/%s/thumbnail.jpg" % child["id"]
        # Thumbnail
        if child['hasPoster']:
            thumbnail = host + "/json/repo/%s/poster.jpg" % child["id"]
        else:
            thumbnail = fanart
        thumbnail += head
        fanart += head
        url = host + "/json/repo/%s/index.json" % child["id"]
        if child['name'] == "":
            title = scrapertools.slugify(child['id'].rsplit(".", 1)[0])
        else:
            title = scrapertools.slugify(child['name'])
        title = title.replace('-', ' ').replace('_', ' ').capitalize()
        infolabels['title'] = title
        try:
            from core import videolibrarytools
            new_item = item.clone(title=title, url=url, fulltitle=title, fanart=fanart, extra="findvideos",
                                  thumbnail=thumbnail, infoLabels=infolabels, category="Cine")
            videolibrarytools.library.add_movie(new_item)
            error = False
        except:
            error = True
            import traceback
            logger.error(traceback.format_exc())
    if not error:
        itemlist.append(Item(channel=item.channel, title='Lista añadida correctamente a la videoteca',
                             action="", folder=False))
    else:
        itemlist.append(Item(channel=item.channel, title='ERROR. Han ocurrido uno o varios errores en el proceso',
                            action="", folder=False))

    return itemlist
