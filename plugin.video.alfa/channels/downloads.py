# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Gestor de descargas
# ------------------------------------------------------------

from __future__ import division
#from builtins import str
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int
from builtins import filter
from past.utils import old_div

import re
import time
import unicodedata
import traceback


from core import filetools
from core import jsontools
from core import scraper
from core import scrapertools
from core import servertools
from core import videolibrarytools
from core import channeltools
from core.downloader import Downloader
from core.item import Item
from platformcode import config, logger
from platformcode import platformtools
from servers import torrent

STATUS_COLORS = {0: "orange", 1: "orange", 2: "green", 3: "red", 4: "magenta", 5: "gray"}
STATUS_CODES = type("StatusCode", (), {"stoped": 0, "canceled": 1, "completed": 2, "error": 3, "auto": 4, "control": 5})
DOWNLOAD_LIST_PATH = config.get_setting("downloadlistpath")
DOWNLOAD_PATH = config.get_setting("downloadpath")
STATS_FILE = filetools.join(config.get_data_path(), "servers.json")

TITLE_FILE = "[COLOR %s][%i%%][/COLOR] %s"
TITLE_TVSHOW = "[COLOR %s][%i%%][/COLOR] %s [%s]"


def mainlist(item):
    logger.info()
    itemlist = []

    # Lista de archivos
    for file in sorted(filetools.listdir(DOWNLOAD_LIST_PATH)):
        # Saltamos todos los que no sean JSON
        if not file.endswith(".json"): continue

        # cargamos el item
        file = filetools.join(DOWNLOAD_LIST_PATH, file)
        i = Item(path=file).fromjson(filetools.read(file))
        i.thumbnail = i.contentThumbnail
        i.unify = True
        del i.unify
        i.folder = True
        del i.folder

        # Listado principal
        if not item.contentType == "tvshow":
            # Series
            if i.contentType == "episode":
                # Comprobamos que la serie no este ya en el itemlist
                if not [x for x in itemlist if x.contentSerieName == i.contentSerieName and x.contentChannel == i.contentChannel]:

                    i_bis = Item.clone(i)
                    title = TITLE_FILE % (
                        STATUS_COLORS[i.downloadStatus], i.downloadProgress, i.contentSerieName)
                    if i_bis.infoLabels['season']: del i_bis.infoLabels['season']
                    if i_bis.infoLabels['episode']: del i_bis.infoLabels['episode']
                    if i_bis.infoLabels['title']: del i_bis.infoLabels['title']
                    itemlist.append(i_bis.clone(channel="downloads", action="mainlist", title=title, 
                                                contentType="tvshow", downloadProgress=[i.downloadProgress]))

                    """
                    itemlist.append(Item(title=title, channel="downloads", action="mainlist", contentType="tvshow",
                                         contentSerieName=i.contentSerieName, contentChannel=i.contentChannel,
                                         downloadStatus=i.downloadStatus, downloadProgress=[i.downloadProgress],
                                         fanart=i.fanart, thumbnail=i.thumbnail))
                    """

                else:
                    s = [x for x in itemlist if x.contentSerieName == i.contentSerieName and x.contentChannel == i.contentChannel][0]
                    s.downloadProgress.append(i.downloadProgress)
                    downloadProgress = old_div(sum(s.downloadProgress), len(s.downloadProgress))

                    if not s.downloadStatus in [STATUS_CODES.error, STATUS_CODES.canceled] and not i.downloadStatus in [
                        STATUS_CODES.completed, STATUS_CODES.stoped]:
                        s.downloadStatus = i.downloadStatus

                    s.title = TITLE_FILE % (
                        STATUS_COLORS[s.downloadStatus], downloadProgress, i.contentSerieName)

            # Peliculas
            elif i.contentType == "movie" or i.contentType == "video":
                i.title = TITLE_FILE % (STATUS_COLORS[i.downloadStatus], i.downloadProgress, i.contentTitle)
                itemlist.append(i)

        # Listado dentro de una serie
        else:
            if i.contentType == "episode" and i.contentSerieName == item.contentSerieName and i.contentChannel == item.contentChannel:
                i.title = TITLE_FILE % (STATUS_COLORS[i.downloadStatus], i.downloadProgress,
                                        "%dx%0.2d: %s [%s] [%s]" % (i.contentSeason, i.contentEpisodeNumber, 
                                        i.contentTitle, scrapertools.find_single_match(i.infoLabels['aired'], '\d{4}'), 
                                        str(i.infoLabels['rating']).zfill(1)))
                itemlist.append(i)

    estados = [i.downloadStatus for i in itemlist]

    # Si hay alguno completado
    if 2 in estados:
        itemlist.insert(0, Item(channel=item.channel, action="clean_ready", title=config.get_localized_string(70218),
                                contentType=item.contentType, contentChannel=item.contentChannel,
                                contentSerieName=item.contentSerieName, text_color="sandybrown"))

    # Si hay alguno con error
    if 3 in estados:
        itemlist.insert(0, Item(channel=item.channel, action="restart_error", title=config.get_localized_string(70219),
                                contentType=item.contentType, contentChannel=item.contentChannel,
                                contentSerieName=item.contentSerieName, text_color="orange"))

    # Reiniciar todos
    if len(itemlist):
        itemlist.insert(0, Item(channel=item.channel, action="restart_all", title=config.get_localized_string(70227),
                                contentType=item.contentType, contentChannel=item.contentChannel,
                                contentSerieName=item.contentSerieName, text_color="orange"))
    
    # Si hay alguno pendiente
    if 1 in estados or 0 in estados or 4 in estados or 5 in estados or (2 in estados and item.downloadProgress != 100):
        itemlist.insert(0, Item(channel=item.channel, action="download_all", title=config.get_localized_string(70220),
                                contentType=item.contentType, contentChannel=item.contentChannel,
                                contentSerieName=item.contentSerieName, text_color="green"))

    if len(itemlist):
        itemlist.insert(0, Item(channel=item.channel, action="clean_all", title=config.get_localized_string(70221),
                                contentType=item.contentType, contentChannel=item.contentChannel,
                                contentSerieName=item.contentSerieName, text_color="red"))

    if not item.contentType == "tvshow" and config.get_setting("browser", "downloads") == True:
        itemlist.insert(0, Item(channel=item.channel, action="browser", title=config.get_localized_string(70222),
                                url=DOWNLOAD_PATH, text_color="yellow"))

    if not item.contentType == "tvshow":
        itemlist.insert(0, Item(channel=item.channel, action="settings", title=config.get_localized_string(70223),
                                text_color="blue"))

    return itemlist


def settings(item):
    ret = platformtools.show_channel_settings(caption=config.get_localized_string(70224))
    platformtools.itemlist_refresh()
    return ret


def browser(item):
    logger.info()
    itemlist = []
    extensions_list = ['.aaf', '.3gp', '.asf', '.avi', '.flv', '.mpeg',
                       '.m1v', '.m2v', '.m4v', '.mkv', '.mov', '.mpg',
                       '.mpe', '.mp4', '.ogg', '.wmv']
    
    torrent_paths = torrent.torrent_dirs()

    for file in filetools.listdir(item.url):
        if file == "list": continue
        if filetools.isdir(filetools.join(item.url, file)):
            if not file.endswith(']'): continue
            itemlist.append(
                Item(channel=item.channel, title=file, action=item.action, url=filetools.join(item.url, file)))
        else:
            if scrapertools.find_single_match(file, '(\.\w+)$') in extensions_list:
                itemlist.append(Item(channel=item.channel, title=file, action="play", url=filetools.join(item.url, file)))
            
    if item.title == 'Ver archivos descargados':
        for file in sorted(filetools.listdir(DOWNLOAD_LIST_PATH)):
            if file.endswith(".json"):
                download_item = Item().fromjson(filetools.read(filetools.join(DOWNLOAD_LIST_PATH, file)))
                if download_item.downloadFilename.startswith(':'):
                    torr_client = scrapertools.find_single_match(download_item.downloadFilename, '^\:(\w+)\:').upper()
                    if not torr_client or not torrent_paths[torr_client]:
                        continue
                    path = re.sub('^\:\w+\:\s*', '', download_item.downloadFilename)
                    if download_item.infoLabels['mediatype'] == 'movie':
                        title = download_item.infoLabels['title']
                    else:
                         title = download_item.infoLabels['tvshowtitle']
                    title = title + ' [%s]' % download_item.category.lower()
                    if filetools.isdir(filetools.join(torrent_paths[torr_client], filetools.dirname(path))):
                        itemlist.append(
                            Item(channel=item.channel, title=title, action=item.action, 
                                        url=filetools.join(torrent_paths[torr_client], filetools.dirname(path))))
                    else:
                        if scrapertools.find_single_match(file, '(\.\w+)$') in extensions_list:
                            itemlist.append(Item(channel=item.channel, title=file, action="play", 
                                        url=filetools.join(torrent_paths[torr_client], path)))

    return itemlist


def clean_all(item):
    logger.info()

    for fichero in sorted(filetools.listdir(DOWNLOAD_LIST_PATH)):
        if fichero.endswith(".json"):
            download_item = Item().fromjson(filetools.read(filetools.join(DOWNLOAD_LIST_PATH, fichero)))

            if not item.contentType == "tvshow" or (
                            item.contentSerieName == download_item.contentSerieName and item.contentChannel == download_item.contentChannel):
                if download_item.server == 'torrent':
                    delete_torrent_session(download_item)
                filetools.remove(filetools.join(DOWNLOAD_LIST_PATH, fichero))

    platformtools.itemlist_refresh()


def clean_ready(item):
    logger.info()
    for fichero in sorted(filetools.listdir(DOWNLOAD_LIST_PATH)):
        if fichero.endswith(".json"):
            download_item = Item().fromjson(filetools.read(filetools.join(DOWNLOAD_LIST_PATH, fichero)))
            if not item.contentType == "tvshow" or (
                            item.contentSerieName == download_item.contentSerieName and item.contentChannel == download_item.contentChannel):
                if download_item.downloadStatus == STATUS_CODES.completed and download_item.downloadProgress not in [1, 2, 3]:
                    filetools.remove(filetools.join(DOWNLOAD_LIST_PATH, fichero))

    platformtools.itemlist_refresh()


def restart_error(item):
    logger.info()
    for fichero in sorted(filetools.listdir(DOWNLOAD_LIST_PATH)):
        if fichero.endswith(".json"):
            download_item = Item().fromjson(filetools.read(filetools.join(DOWNLOAD_LIST_PATH, fichero)))

            if not item.contentType == "tvshow" or (
                            item.contentSerieName == download_item.contentSerieName and item.contentChannel == download_item.contentChannel):
                if download_item.downloadStatus == STATUS_CODES.error:
                    if download_item.server == 'torrent':
                        delete_torrent_session(download_item)
                        download_item.downloadServer = {}
                    
                    else:
                        if filetools.isfile(filetools.join(config.get_setting("downloadpath"), download_item.downloadFilename)):
                            filetools.remove(filetools.join(config.get_setting("downloadpath"), download_item.downloadFilename), silent=True)
                            if filetools.isdir(filetools.join(config.get_setting("downloadpath"), \
                                        filetools.dirname(download_item.downloadFilename))) and len(filetools.listdir\
                                        (filetools.join(config.get_setting("downloadpath"), \
                                        filetools.dirname(download_item.downloadFilename)))) == 0:
                                filetools.rmdirtree(filetools.join(config.get_setting("downloadpath"), \
                                        filetools.dirname(download_item.downloadFilename)), silent=True)

                    contentAction = download_item.contentAction
                    if download_item.contentAction == 'play' and not download_item.downloadServer and not download_item.torr_folder:
                        contentAction = 'findvideos'
                    update_json(fichero,
                                {"downloadStatus": STATUS_CODES.stoped, "downloadCompleted": 0, \
                                            "downloadProgress": 0, "downloadQueued": download_item.downloadQueued, \
                                            "contentAction": contentAction})

    platformtools.itemlist_refresh()


def restart_all(item):
    logger.info()
    for fichero in sorted(filetools.listdir(DOWNLOAD_LIST_PATH)):
        if fichero.endswith(".json"):
            download_item = Item().fromjson(filetools.read(filetools.join(DOWNLOAD_LIST_PATH, fichero)))

            if not item.contentType == "tvshow" or (
                            item.contentSerieName == download_item.contentSerieName and item.contentChannel == download_item.contentChannel):

                if download_item.server == 'torrent':
                    delete_torrent_session(download_item)
                    download_item.downloadServer = {}
                
                else:
                    if filetools.isfile(filetools.join(config.get_setting("downloadpath"), download_item.downloadFilename)):
                        filetools.remove(filetools.join(config.get_setting("downloadpath"), download_item.downloadFilename), silent=True)
                        if filetools.isdir(filetools.join(config.get_setting("downloadpath"), \
                                    filetools.dirname(download_item.downloadFilename))) and len(filetools.listdir\
                                    (filetools.join(config.get_setting("downloadpath"), \
                                    filetools.dirname(download_item.downloadFilename)))) == 0:
                            filetools.rmdirtree(filetools.join(config.get_setting("downloadpath"), \
                                    filetools.dirname(download_item.downloadFilename)), silent=True)

                contentAction = download_item.contentAction
                if download_item.contentAction == 'play' and not download_item.downloadServer and not download_item.torr_folder:
                    contentAction = 'findvideos'
                update_json(fichero,
                            {"downloadStatus": STATUS_CODES.stoped, "downloadCompleted": 0, \
                                        "downloadProgress": 0, "downloadQueued": download_item.downloadQueued, \
                                        "contentAction": contentAction})

    platformtools.itemlist_refresh()


def download_all(item):
    time.sleep(0.5)
    second_pass = False
    filelist = sorted(filetools.listdir(DOWNLOAD_LIST_PATH))
    
    for fichero in filelist:
        if fichero.endswith(".json") and filetools.exists(filetools.join(DOWNLOAD_LIST_PATH, fichero)):
            download_item = Item(path=filetools.join(DOWNLOAD_LIST_PATH, fichero)).fromjson(
                filetools.read(filetools.join(DOWNLOAD_LIST_PATH, fichero)))

            if not item.contentType == "tvshow" or (
                            item.contentSerieName == download_item.contentSerieName and item.contentChannel == download_item.contentChannel):
                if download_item.downloadStatus in [STATUS_CODES.stoped, STATUS_CODES.canceled] \
                            or (download_item.downloadStatus in [STATUS_CODES.completed, STATUS_CODES.auto, \
                            STATUS_CODES.control] and (download_item.downloadProgress == 0 \
                            or download_item.downloadQueued > 0)):
                    
                    if download_item.downloadQueued == 0 and download_item.downloadProgress != 100:
                        download_item.downloadQueued = 1
                        res = filetools.write(filetools.join(DOWNLOAD_LIST_PATH, fichero), download_item.tojson())
                        if res: second_pass = True
                    
                    elif not second_pass:
                        res = start_download(download_item)
                        platformtools.itemlist_refresh()
                        # Si se ha cancelado paramos y desencolamos
                        if res == STATUS_CODES.canceled:
                            for file in filelist:
                                download_item = Item(path=filetools.join(DOWNLOAD_LIST_PATH, file)).fromjson(
                                        filetools.read(filetools.join(DOWNLOAD_LIST_PATH, file)))
                                if download_item.downloadQueued != 0:
                                    download_item.downloadQueued = 0
                                    res = filetools.write(filetools.join(DOWNLOAD_LIST_PATH, file), download_item.tojson())
                                    second_pass = False
                            break
    
    if second_pass:
        download_all(item)
                        
                        
def download_auto(item, start_up=False):
    logger.info()
    
    second_pass = False
    move_to_remote = config.get_setting("move_to_remote", "downloads", default=[])
    filelist = sorted(filetools.listdir(DOWNLOAD_LIST_PATH))
    
    for fichero in filelist:
        time.sleep(0.5)
        if fichero.endswith(".json") and filetools.exists(filetools.join(DOWNLOAD_LIST_PATH, fichero)):
            download_item = Item(path=filetools.join(DOWNLOAD_LIST_PATH, fichero)).fromjson(
                filetools.read(filetools.join(DOWNLOAD_LIST_PATH, fichero)))
            if download_item.contentType == 'movie':
                PATH = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_movies"))
            else:
                PATH = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_tvshows"))

            if download_item.downloadStatus in [STATUS_CODES.auto]:
                if download_item.downloadQueued == 0 and download_item.downloadProgress != 100:
                    download_item.downloadQueued = 1
                    res = filetools.write(filetools.join(DOWNLOAD_LIST_PATH, fichero), download_item.tojson())
                    if res: second_pass = True
                    
                    # Si el usuario desea descargar esta Serie en otro servidor Kodi, copia el fichero a la dirección aportada
                    if res and move_to_remote:
                        for serie, address in move_to_remote:
                            if serie.lower() in download_item.contentSerieName.lower():     # Si está en la lista es que es remoto
                                if download_item.nfo:
                                    download_item.nfo = download_item.nfo.replace(PATH, '')
                                if download_item.strm_path:
                                    download_item.strm_path = download_item.strm_path.replace(PATH, '')
                                res = filetools.write(filetools.join(address, fichero), download_item.tojson(), silent=True)
                                if res:
                                    res = filetools.remove(filetools.join(DOWNLOAD_LIST_PATH, fichero), silent=True)
                                    if res: second_pass = False
                                    break

                elif not second_pass and not start_up and download_item.downloadProgress != 100:
                    res = start_download(download_item)
                    if res == STATUS_CODES.canceled: break
    
    if second_pass and not start_up:
        download_auto(item)


def menu(item):
    logger.info()
    if item.downloadServer:
        servidor = item.downloadServer.get("server", "Auto")
    else:
        servidor = "Auto"
        
    if item.server == 'torrent' and item.path.endswith('.json'):
        item = Item(path=filetools.join(DOWNLOAD_LIST_PATH, item.path)).fromjson(
                filetools.read(filetools.join(DOWNLOAD_LIST_PATH, item.path)))
    # Opciones disponibles para el menu
    op = [config.get_localized_string(70225), config.get_localized_string(70226), config.get_localized_string(70227),
          "Modificar servidor: %s" % (servidor.capitalize()), config.get_localized_string(70221)]

    opciones = []

    # Opciones para el menu
    if item.downloadStatus in [0]:  # Sin descargar
        opciones.append(op[0])  # Descargar
        if not item.server: opciones.append(op[3])  # Elegir Servidor
        opciones.append(op[1])  # Eliminar de la lista
        opciones.append(op[4])  # Eliminar todo

    if item.downloadStatus == 1:  # descarga parcial
        opciones.append(op[0])  # Descargar
        if not item.server: opciones.append(op[3])  # Elegir Servidor
        opciones.append(op[2])  # Reiniciar descarga
        opciones.append(op[1])  # Eliminar de la lista
        opciones.append(op[4])  # Eliminar todo

    if item.downloadStatus in [2 ,4, 5]:  # descarga completada o archivo de control o auto
        if item.downloadProgress == 0:
            opciones.append(op[0])  # Descargar
        opciones.append(op[2])  # Reiniciar descarga
        opciones.append(op[1])  # Eliminar de la lista
        opciones.append(op[4])  # Eliminar todo

    if item.downloadStatus == 3:  # descarga con error
        opciones.append(op[2])  # Reiniciar descarga
        opciones.append(op[1])  # Eliminar de la lista
        opciones.append(op[4])  # Eliminar todo
    
    # Mostramos el dialogo
    seleccion = platformtools.dialog_select(config.get_localized_string(30163), opciones)

    # -1 es cancelar
    if seleccion == -1: return

    logger.info("opcion=%s" % (opciones[seleccion]))
    # Opcion Eliminar
    if opciones[seleccion] == op[1]:
        filetools.remove(filetools.join(config.get_setting("downloadlistpath"), item.path))

    # Opcion iniciar descarga
    if opciones[seleccion] == op[0]:
        if item.server == 'torrent':
            item.downloadProgress = 0
            item.downloadQueued = 1
            update_json(item.path, {"downloadProgress": 0, "downloadQueued": 1})
        res = start_download(item)

    # Elegir Servidor
    if opciones[seleccion] == op[3]:
        select_server(item)

    # Reiniciar descarga y Eliminar TODO
    if opciones[seleccion] == op[2] or opciones[seleccion] == op[4]:

        if item.server == 'torrent':
            delete_RAR = True
            if opciones[seleccion] == op[2]: delete_RAR = False
            delete_torrent_session(item, delete_RAR)
        
        else:
            if filetools.isfile(filetools.join(config.get_setting("downloadpath"), item.downloadFilename)):
                filetools.remove(filetools.join(config.get_setting("downloadpath"), item.downloadFilename), silent=True)
                if filetools.isdir(filetools.join(config.get_setting("downloadpath"), \
                            filetools.dirname(item.downloadFilename))) and len(filetools.listdir\
                            (filetools.join(config.get_setting("downloadpath"), \
                            filetools.dirname(item.downloadFilename)))) == 0:
                    filetools.rmdirtree(filetools.join(config.get_setting("downloadpath"), \
                            filetools.dirname(item.downloadFilename)), silent=True)

            update_json(item.path, {"downloadStatus": STATUS_CODES.stoped, "downloadCompleted": 0, "downloadProgress": 0,
                                "downloadQueued": 0, "downloadServer": {}})
        item.downloadProgress = 0
        item.downloadQueued = 0
    
    # Eliminar TODO
    if opciones[seleccion] == op[4]:
        filetools.remove(filetools.join(DOWNLOAD_LIST_PATH, item.path), silent=True)
    
    platformtools.itemlist_refresh()


def delete_torrent_session(item, delete_RAR=True):
    if not delete_RAR and 'RAR-' not in item.torrent_info:
        delete_RAR = True
    logger.info('delete_RAR: %s' % str(delete_RAR))

    # Detiene y borra la descarga de forma específica al gestor de torrent en uso
    torr_data = ''
    deamon_url = ''
    index = -1
    filebase = ''
    folder_new = ''

    # Obtenemos los datos del gestor de torrents
    torrent_paths = torrent.torrent_dirs()
    torr_client = scrapertools.find_single_match(item.downloadFilename, '^\:(\w+)\:')
    folder_new = scrapertools.find_single_match(item.downloadFilename, '^\:\w+\:\s*(.*?)$')
    if filetools.dirname(folder_new):
        folder_new = filetools.dirname(folder_new)
    if item.torr_folder:
        folder = item.torr_folder
    else:
        folder = folder_new.replace('\\', '').replace('/', '')
    if folder_new:
        if folder_new.startswith('\\') or folder_new.startswith('/'):
            folder_new = folder_new[1:]
        if '\\' in folder_new:
            folder_new = folder_new.split('\\')[0]
        elif '/' in folder_new:
            folder_new = folder_new.split('/')[0]
        if folder_new:
            folder_new = filetools.join(torrent_paths[torr_client.upper()], folder_new)
    
    # Actualiza el .json de control
    if item.downloadStatus in [5]:
        item.downloadStatus = 2                                                 # Pasa de foreground a background
    update_json(item.path, {"downloadStatus": item.downloadStatus, "downloadProgress": 0, "downloadQueued": 0,
                                "downloadServer": {}})

    # Detiene y borra la sesion de los clientes externos Quasar y Elementum
    if torr_client in ['QUASAR', 'ELEMENTUM']:
        if not delete_RAR: folder_new = ''
        torr_data, deamon_url, index = torrent.get_tclient_data(folder, torr_client.lower(), \
                                torrent_paths['ELEMENTUM_port'], delete=True, folder_new=folder_new)
        
    # Detiene y borra la sesion de los clientes Internos
    if torr_client in ['BT', 'MCT']:
        if item.downloadServer and 'url' in str(item.downloadServer) and not item.downloadServer['url'].startswith('http'): 
            filebase = filetools.basename(item.downloadServer['url']).upper()
        elif item.url and not item.url.startswith('http') and not item.url.startswith('magnet:'):
            filebase = filetools.basename(item.url).upper()
        elif item.url_control and not item.url_control.startswith('http'):
            filebase = filetools.basename(item.url_control).upper()
        if filebase:
            file = filetools.join(torrent_paths[torr_client+'_torrents'], filebase)
            if filetools.exists(file):
                filetools.remove(file, silent=True)
        
                #Espera a que el gestor termine de borrar la sesion (timing...)            
                time.sleep(8)
            
        downloadFilename = scrapertools.find_single_match(item.downloadFilename, '\:\w+\:\s*(.*?)$')
        if downloadFilename and delete_RAR:
            if downloadFilename.startswith('\\') or downloadFilename.startswith('/'):
                downloadFilename = downloadFilename[1:]
            downloadFolder = filetools.dirname(downloadFilename)
            if '\\' in downloadFolder:
                downloadFolder = downloadFolder.split('\\')[0]
            elif '/' in downloadFolder:
                downloadFolder = downloadFolder.split('/')[0]
            if downloadFolder:
                if filetools.isdir(filetools.join(torrent_paths[torr_client], downloadFolder)):
                    filetools.rmdirtree(filetools.join(torrent_paths[torr_client], downloadFolder), silent=True)
                else:
                    filetools.remove(filetools.join(torrent_paths[torr_client], downloadFolder), silent=True)
            elif downloadFilename:
                filetools.remove(filetools.join(torrent_paths[torr_client], downloadFilename), silent=True)
                
        config.set_setting("LIBTORRENT_in_use", False, server="torrent")        # Marcamos Libtorrent como disponible

    # Vuelve a  actualiza el .json de control después de que el gestor de torrent termine su función (timing...)
    time.sleep(1)
    if item.url_control:
        item.url = item.url_control
    update_json(item.path, {"downloadStatus": item.downloadStatus, "downloadProgress": 0, "downloadQueued": 0,
                                "downloadServer": {}, "url": item.url})
    
    return torr_data, deamon_url, index


def move_to_libray(item):
    download_path = filetools.join(config.get_setting("downloadpath"), item.downloadFilename)
    library_path = filetools.join(config.get_videolibrary_path(), *filetools.split(item.downloadFilename))
    final_path = download_path

    if config.get_setting("library_add", "downloads") == True and config.get_setting("library_move",
                                                                                     "downloads") == True:
        if not filetools.isdir(filetools.dirname(library_path)):
            filetools.mkdir(filetools.dirname(library_path))

        if filetools.isfile(library_path) and filetools.isfile(download_path):
            filetools.remove(library_path)

        if filetools.isfile(download_path):
            if filetools.move(download_path, library_path):
                final_path = library_path

            if len(filetools.listdir(filetools.dirname(download_path))) == 0:
                filetools.rmdir(filetools.dirname(download_path))

    if config.get_setting("library_add", "downloads") == True:
        if filetools.isfile(final_path):
            if item.contentType == "movie" and item.infoLabels["tmdb_id"]:
                library_item = Item(title=config.get_localized_string(70228) % item.downloadFilename, channel="downloads",
                                    action="findvideos", infoLabels=item.infoLabels, url=final_path)
                videolibrarytools.save_movie(library_item)

            elif item.contentType == "episode" and item.infoLabels["tmdb_id"]:
                library_item = Item(title=config.get_localized_string(70228) % item.downloadFilename, channel="downloads",
                                    action="findvideos", infoLabels=item.infoLabels, url=final_path)
                tvshow = Item(channel="downloads", contentType="tvshow",
                              infoLabels={"tmdb_id": item.infoLabels["tmdb_id"]})
                videolibrarytools.save_tvshow(tvshow, [library_item])


def update_json(path, params):
    logger.info(path + str(params))
    if not path or not params: return
    path = filetools.join(config.get_setting("downloadlistpath"), path)
    if filetools.exists(path):
        item = Item().fromjson(filetools.read(path))
        item.__dict__.update(params)
        filetools.write(path, item.tojson())


def save_server_statistics(server, speed, success):
    if filetools.isfile(STATS_FILE):
        servers = jsontools.load(filetools.read(STATS_FILE))
    else:
        servers = {}

    if not server in servers:
        servers[server] = {"success": [], "count": 0, "speeds": [], "last": 0}

    servers[server]["count"] += 1
    servers[server]["success"].append(bool(success))
    servers[server]["success"] = servers[server]["success"][-5:]
    servers[server]["last"] = time.time()
    if success:
        servers[server]["speeds"].append(speed)
        servers[server]["speeds"] = servers[server]["speeds"][-5:]

    filetools.write(STATS_FILE, jsontools.dump(servers))
    return


def get_server_position(server):
    if filetools.isfile(STATS_FILE):
        servers = jsontools.load(filetools.read(STATS_FILE))
    else:
        servers = {}

    if server in servers:
        pos = [s for s in sorted(servers, key=lambda x: (old_div(sum(servers[x]["speeds"]), (len(servers[x]["speeds"]) or 1)),
                                                         float(sum(servers[x]["success"])) / (
                                                             len(servers[x]["success"]) or 1)), reverse=True)]
        return pos.index(server) + 1
    else:
        return 0


def get_match_list(data, match_list, order_list=None, only_ascii=False, ignorecase=False):
    """
    Busca coincidencias en una cadena de texto, con un diccionario de "ID" / "Listado de cadenas de busqueda":
     { "ID1" : ["Cadena 1", "Cadena 2", "Cadena 3"],
       "ID2" : ["Cadena 4", "Cadena 5", "Cadena 6"]
     }
     
     El diccionario no pude contener una misma cadena de busqueda en varías IDs.
     
     La busqueda se realiza por orden de tamaño de cadena de busqueda (de mas larga a mas corta) si una cadena coincide,
     se elimina de la cadena a buscar para las siguientes, para que no se detecten dos categorias si una cadena es parte de otra:
     por ejemplo: "Idioma Español" y "Español" si la primera aparece en la cadena "Pablo sabe hablar el Idioma Español" 
     coincidira con "Idioma Español" pero no con "Español" ya que la coincidencia mas larga tiene prioridad.
     
    """
    match_dict = dict()
    matches = []

    # Pasamos la cadena a unicode
    if not PY3:
        data = unicode(data, "utf8")

    # Pasamos el diccionario a {"Cadena 1": "ID1", "Cadena 2", "ID1", "Cadena 4", "ID2"} y los pasamos a unicode
    for key in match_list:
        if order_list and not key in order_list:
            raise Exception("key '%s' not in match_list" % key)
        for value in match_list[key]:
            if value in match_dict:
                raise Exception("Duplicate word in list: '%s'" % value)
            if not PY3:
                match_dict[unicode(value, "utf8")] = key
            else:
                match_dict[value] = key

    # Si ignorecase = True, lo pasamos todo a mayusculas
    if ignorecase:
        data = data.upper()
        match_dict = dict((key.upper(), match_dict[key]) for key in match_dict)

    # Si ascii = True, eliminamos todos los accentos y Ñ
    if only_ascii:
        data = ''.join((c for c in unicodedata.normalize('NFD', data) if unicodedata.category(c) != 'Mn'))
        match_dict = dict((''.join((c for c in unicodedata.normalize('NFD', key) if unicodedata.category(c) != 'Mn')),
                           match_dict[key]) for key in match_dict)

    # Ordenamos el listado de mayor tamaño a menor y buscamos.
    for match in sorted(match_dict, key=lambda x: len(x), reverse=True):
        s = data
        for a in matches:
            s = s.replace(a, "")
        if match in s:
            matches.append(match)
    if matches:
        if order_list:
            return type("Mtch_list", (),
                        {"key": match_dict[matches[-1]], "index": order_list.index(match_dict[matches[-1]])})
        else:
            return type("Mtch_list", (), {"key": match_dict[matches[-1]], "index": None})
    else:
        if order_list:
            return type("Mtch_list", (), {"key": None, "index": len(order_list)})
        else:
            return type("Mtch_list", (), {"key": None, "index": None})


def sort_method(item):
    """
    Puntua cada item en funcion de varios parametros:     
    @type item: item
    @param item: elemento que se va a valorar.
    @return:  puntuacion otenida
    @rtype: int
    """
    lang_orders = {}
    lang_orders[0] = ["ES", "LAT", "SUB", "ENG", "VOSE"]
    lang_orders[1] = ["ES", "SUB", "LAT", "ENG", "VOSE"]
    lang_orders[2] = ["ENG", "SUB", "VOSE", "ESP", "LAT"]
    lang_orders[3] = ["VOSE", "ENG", "SUB", "ESP", "LAT"]

    quality_orders = {}
    quality_orders[0] = ["BLURAY", "FULLHD", "HD", "480P", "360P", "240P"]
    quality_orders[1] = ["FULLHD", "HD", "480P", "360P", "240P", "BLURAY"]
    quality_orders[2] = ["HD", "480P", "360P", "240P", "FULLHD", "BLURAY"]
    quality_orders[3] = ["480P", "360P", "240P", "BLURAY", "FULLHD", "HD"]

    order_list_idiomas = lang_orders[int(config.get_setting("language", "downloads"))]
    match_list_idimas = {"ES": ["CAST", "ESP", "Castellano", "Español", "Audio Español"],
                         "LAT": ["LAT", "Latino"],
                         "SUB": ["Subtitulo Español", "Subtitulado", "SUB"],
                         "ENG": ["EN", "ENG", "Inglés", "Ingles", "English"],
                         "VOSE": ["VOSE"]}

    order_list_calidad = ["BLURAY", "FULLHD", "HD", "480P", "360P", "240P"]
    order_list_calidad = quality_orders[int(config.get_setting("quality", "downloads"))]
    match_list_calidad = {"BLURAY": ["BR", "BLURAY"],
                          "FULLHD": ["FULLHD", "FULL HD", "1080", "HD1080", "HD 1080"],
                          "HD": ["HD", "HD REAL", "HD 720", "720", "HDTV"],
                          "480P": ["SD", "480P"],
                          "360P": ["360P"],
                          "240P": ["240P"]}

    value = (get_match_list(item.title, match_list_idimas, order_list_idiomas, ignorecase=True, only_ascii=True).index, \
             get_match_list(item.title, match_list_calidad, order_list_calidad, ignorecase=True, only_ascii=True).index)

    if config.get_setting("server_speed", "downloads"):
        value += tuple([get_server_position(item.server)])

    return value


def download_from_url(url, item):
    logger.info("Intentando descargar: %s" % (url))
    if url.lower().endswith(".m3u8") or url.lower().startswith("rtmp"):
        save_server_statistics(item.server, 0, False)
        return {"downloadStatus": STATUS_CODES.error}

    item.downloadQueued = 0
    config.set_setting("DOWNLOADER_in_use", True, "downloads")                  # Marcamos Downloader en uso
    # Obtenemos la ruta de descarga y el nombre del archivo
    item.downloadFilename = item.downloadFilename.replace('/','-')
    download_path = filetools.dirname(filetools.join(DOWNLOAD_PATH, item.downloadFilename))
    file_name = filetools.basename(filetools.join(DOWNLOAD_PATH, item.downloadFilename))

    # Creamos la carpeta si no existe

    if not filetools.exists(download_path):
        filetools.mkdir(download_path)

    # Lanzamos la descarga
    d = Downloader(url, download_path, file_name,
                   max_connections=1 + int(config.get_setting("max_connections", "downloads")),
                   block_size=2 ** (17 + int(config.get_setting("block_size", "downloads"))),
                   part_size=2 ** (20 + int(config.get_setting("part_size", "downloads"))),
                   max_buffer=2 * int(config.get_setting("max_buffer", "downloads")))
    d.start_dialog('%s: %s' % (config.get_localized_string(60332), item.server.capitalize()))

    # Descarga detenida. Obtenemos el estado:
    # Se ha producido un error en la descarga   
    if d.state == d.states.error:
        logger.info("Error al intentar descargar %s" % (url))
        status = STATUS_CODES.error

    # La descarga se ha detenifdo
    elif d.state == d.states.stopped:
        logger.info("Descarga detenida")
        status = STATUS_CODES.canceled

    # La descarga ha finalizado
    elif d.state == d.states.completed:
        logger.info("Descargado correctamente")
        status = STATUS_CODES.completed

        if item.downloadSize and item.downloadSize != d.size[0]:
            status = STATUS_CODES.error

    save_server_statistics(item.server, d.speed[0], d.state != d.states.error)

    file = filetools.join(filetools.dirname(item.downloadFilename), d.filename)

    if status == STATUS_CODES.completed:
        move_to_libray(item.clone(downloadFilename=file))

    config.set_setting("DOWNLOADER_in_use", False, "downloads")                 # Marcamos Downloader como disponible
    return {"downloadUrl": d.download_url, "downloadStatus": status, "downloadSize": d.size[0], "downloadQueued": 0, 
            "downloadProgress": d.progress, "downloadCompleted": d.downloaded[0], "downloadFilename": file}


def download_from_server(item, silent=False):
    logger.info()
    
    unsupported_servers = ["torrent"]
    result = {}
    CF_BLOCKED = '[B]Pincha para usar con [I]'
    
    if item.contentType == 'movie':
        PATH = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_movies"))
    else:
        PATH = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_tvshows"))

    if not silent: progreso = platformtools.dialog_progress(config.get_localized_string(30101), \
                        config.get_localized_string(70178) % item.server)
    channel = __import__('channels.%s' % item.contentChannel, None, None, ["channels.%s" % item.contentChannel])
    if hasattr(channel, "play") and not item.play_menu and not item.url.startswith('magnet:'):

        if not silent: progreso.update(50, config.get_localized_string(70178) % \
                        item.server + '\n' + config.get_localized_string(60003) % item.contentChannel)
        if item.server == 'torrent': item.url_control = item.url
        try:
            itemlist = getattr(channel, "play")(item.clone(channel=item.contentChannel, action=item.contentAction))
        except:
            logger.error("Error en el canal %s" % item.contentChannel)
        else:
            if len(itemlist) and isinstance(itemlist[0], Item):
                download_item = item.clone(**itemlist[0].__dict__)
                download_item.contentAction = download_item.action
                download_item.infoLabels = item.infoLabels
                item = download_item
            elif len(itemlist) and isinstance(itemlist[0], list):
                item.video_urls = itemlist
                if not item.server: item.server = "directo"
            else:
                logger.info("No hay nada que reproducir")
                return {"downloadStatus": STATUS_CODES.error}
    if not silent: progreso.close()
    logger.info("contentAction: %s | contentChannel: %s | server: %s | url: %s" % (
        item.contentAction, item.contentChannel, item.server, item.url))

    if item.server == 'torrent':
        torrent_paths = torrent.torrent_dirs()
        # Si es .torrent y ha dato error, se intenta usar las urls de emergencia.  Si no, se marca como no error y se pasa al siguiente
        if config.get_videolibrary_path() not in item.url and torrent_paths['TORR_client'] \
                        and torrent_paths[torrent_paths['TORR_client'].upper()] not in item.url \
                        and not item.url.startswith('http') and not item.url.startswith('magnet:'):
            item.url = filetools.join(PATH, item.url)
        if not item.url.startswith('http') and filetools.isfile(item.url):
            if not filetools.exists(item.url):
                item.torrent_info += '[ERROR]'
            else:
                item.torrent_info = item.torrent_info.replace('ERROR', '')
            
        if 'cliente_torrent_Alfa.torrent' in item.url or ('ERROR' in item.torrent_info and not CF_BLOCKED in item.torrent_info):
            try:
                if item.torrent_alt or item.emergency_urls:
                    if item.torrent_alt:
                        item.url = item.torrent_alt
                    elif item.emergency_urls:
                        item.url = item.emergency_urls[0][0]
                    if config.get_videolibrary_path() not in item.url and torrent_paths['TORR_client'] \
                                and torrent_paths[torrent_paths['TORR_client'].upper()] not in item.url \
                                and not item.url.startswith('http') and not item.url.startswith('magnet:'):
                        item.url = filetools.join(PATH, item.url)
                    if not item.url.startswith('http') and not item.url.startswith('magnet:') and not filetools.exists(item.url):
                        PATH = ''
                elif not filetools.exists(item.url):
                    PATH = ''
            except:
                PATH = ''
                logger.error(traceback.format_exc())
        if not PATH:
            result["contentAction"] = item.contentAction
            result["downloadServer"] = {"url": item.url, "server": item.server}
            result["server"] = item.server
            result["downloadQueued"] = 0
            result["downloadProgress"] = 0
            result["downloadStatus"] = STATUS_CODES.error
            item.downloadStatus = result["downloadStatus"]
            result["downloadCompleted"] = 0
            item.downloadCompleted = result["downloadCompleted"]
            return result
        
        import xbmcgui
        # Creamos el listitem
        xlistitem = xbmcgui.ListItem(path=item.url)

        if config.get_platform(True)['num_version'] >= 16.0:
            xlistitem.setArt({'icon': item.thumbnail, 'thumb': item.thumbnail, 'poster': item.thumbnail,
                             'fanart': item.thumbnail})
        else:
            xlistitem.setIconImage(item.thumbnail)
            xlistitem.setThumbnailImage(item.thumbnail)
            xlistitem.setProperty('fanart_image', item.thumbnail)

        if config.get_setting("player_mode"):
            xlistitem.setProperty('IsPlayable', 'true')
        item.folder = False
        
        if item.strm_path:
            item.strm_path = filetools.join(PATH, item.strm_path)
        
        platformtools.set_infolabels(xlistitem, item)

        result["contentAction"] = item.contentAction
        result["downloadServer"] = {"url": item.url, "server": item.server}
        result["server"] = item.server
        result["downloadProgress"] = 1
        result["downloadQueued"] = 1
        if item.downloadStatus == 0:
            result["downloadStatus"] = STATUS_CODES.completed
        else:
            result["downloadStatus"] = item.downloadStatus
        item.downloadStatus = result["downloadStatus"]
        result["downloadCompleted"] = 0
        item.downloadCompleted = result["downloadCompleted"]
        item.downloadStatus = result["downloadStatus"]
        item.downloadProgress = result["downloadProgress"]
        item.downloadQueued = result["downloadQueued"]
        item.downloadServer = result["downloadServer"]
        
        platformtools.play_torrent(item, xlistitem, item.url)
        
        result["contentAction"] = item.contentAction
        result["downloadCompleted"] = item.downloadCompleted
        result["downloadStatus"] = item.downloadStatus
        result["downloadProgress"] = item.downloadProgress
        result["downloadQueued"] = item.downloadQueued
        result["downloadServer"] = item.downloadServer

        return result
    
    if not item.server or not item.url or not item.contentAction == "play" or item.server in unsupported_servers:
        logger.error("El Item no contiene los parametros necesarios.")
        return {"downloadStatus": STATUS_CODES.error}

    if not item.video_urls:
        video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing(item.server, item.url, item.password,
                                                                                True)
    else:
        video_urls, puedes, motivo = item.video_urls, True, ""

        # Si no esta disponible, salimos
    if not puedes:
        logger.info("El vídeo **NO** está disponible")
        return {"downloadStatus": STATUS_CODES.error}

    else:
        logger.info("El vídeo **SI** está disponible")

        # Recorre todas las opciones hasta que consiga descargar una correctamente
        for video_url in reversed(video_urls):

            result = download_from_url(video_url[1], item)

            if result["downloadStatus"] in [STATUS_CODES.canceled, STATUS_CODES.completed]:
                break

            # Error en la descarga, continuamos con la siguiente opcion
            if result["downloadStatus"] == STATUS_CODES.error:
                continue

        # Devolvemos el estado
        return result


def download_from_best_server(item, silent=False):
    logger.info(
        "contentAction: %s | contentChannel: %s | url: %s" % (item.contentAction, item.contentChannel, item.url))

    if item.sub_action in ["auto"]: silent=True
    result = {"downloadStatus": STATUS_CODES.error}

    if not silent: progreso = platformtools.dialog_progress(config.get_localized_string(30101), config.get_localized_string(70179))
    channel = __import__('channels.%s' % item.contentChannel, None, None, ["channels.%s" % item.contentChannel])

    if not silent: progreso.update(50, config.get_localized_string(70184) + '\n' + config.get_localized_string(70180) % item.contentChannel)

    if hasattr(channel, item.contentAction):
        play_items = getattr(channel, item.contentAction)(
            item.clone(action=item.contentAction, channel=item.contentChannel))
    else:
        play_items = servertools.find_video_items(item.clone(action=item.contentAction, channel=item.contentChannel))
    
    play_items = [x for x in play_items if x.action == "play" and not "trailer" in x.title.lower()]

    if not silent: progreso.update(100, config.get_localized_string(70183) + '\n' + config.get_localized_string(70181) % len(play_items) + '\n' + 
                    config.get_localized_string(70182))

    if config.get_setting("server_reorder", "downloads") == 1:
        play_items.sort(key=sort_method)

    if not silent and progreso.iscanceled():
        return {"downloadStatus": STATUS_CODES.canceled}

    if not silent: progreso.close()

    # Recorremos el listado de servers, hasta encontrar uno que funcione
    for play_item in play_items:
        play_item = item.clone(**play_item.__dict__)
        play_item.contentAction = play_item.action
        play_item.infoLabels = item.infoLabels

        result = download_from_server(play_item, silent=silent)

        if not silent and progreso.iscanceled():
            result["downloadStatus"] = STATUS_CODES.canceled

        # Tanto si se cancela la descarga como si se completa dejamos de probar mas opciones
        if result["downloadStatus"] in [STATUS_CODES.canceled, STATUS_CODES.completed, STATUS_CODES.auto, \
                            STATUS_CODES.control]:
            if not "downloadServer" in result:
                result["downloadServer"] = {"url": play_item.url, "server": play_item.server}
            break

    return result


def select_server(item):
    logger.info(
        "contentAction: %s | contentChannel: %s | url: %s" % (item.contentAction, item.contentChannel, item.url))

    progreso = platformtools.dialog_progress(config.get_localized_string(30101), config.get_localized_string(70179))
    channel = __import__('channels.%s' % item.contentChannel, None, None, ["channels.%s" % item.contentChannel])
    progreso.update(50, config.get_localized_string(70184) + '\n' + config.get_localized_string(70180) % item.contentChannel)

    if hasattr(channel, item.contentAction):
        play_items = getattr(channel, item.contentAction)(
            item.clone(action=item.contentAction, channel=item.contentChannel))
    else:
        play_items = servertools.find_video_items(item.clone(action=item.contentAction, channel=item.contentChannel))

    play_items = [x for x in play_items if x.action == "play" and not "trailer" in x.title.lower()]

    progreso.update(100, config.get_localized_string(70183) + '\n' + config.get_localized_string(70181) % len(play_items) + '\n' + 
                    config.get_localized_string(70182))

    for x, i in enumerate(play_items):
        if not i.server and hasattr(channel, "play"):
            play_items[x] = getattr(channel, "play")(i)

    seleccion = platformtools.dialog_select(config.get_localized_string(70192), ["Auto"] + [s.title for s in play_items])
    if seleccion > 1:
        update_json(item.path, {
            "downloadServer": {"url": play_items[seleccion - 1].url, "server": play_items[seleccion - 1].server}})
    elif seleccion == 0:
        update_json(item.path, {"downloadServer": {}})

    platformtools.itemlist_refresh()


def start_download(item):
    logger.info(
        "contentAction: %s | contentChannel: %s | url: %s" % (item.contentAction, item.contentChannel, item.url))

    # Ya tenemnos server, solo falta descargar
    if item.contentAction == "play":
        ret = download_from_server(item)
        update_json(item.path, ret)
        return ret["downloadStatus"]

    elif item.downloadServer and item.downloadServer.get("server"):
        ret = download_from_server(
            item.clone(server=item.downloadServer.get("server"), url=item.downloadServer.get("url"),
                       contentAction="play"))
        update_json(item.path, ret)
        return ret["downloadStatus"]
    # No tenemos server, necesitamos buscar el mejor
    else:
        ret = download_from_best_server(item)
        update_json(item.path, ret)
        return ret["downloadStatus"]


def get_episodes(item):
    logger.info("contentAction: %s | sub_action: %s | contentChannel: %s | contentType: %s | contentSeason: %s | contentEpisodeNumber: %s" % (
        item.contentAction, item.sub_action, item.contentChannel, item.contentType, item.contentSeason, item.contentEpisodeNumber, ))

    from lib import generictools
    
    sub_action = ["tvshow", "season", "unseen", "auto"]                         # Acciones especiales desde Findvideos
    SERIES = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_tvshows"))
    nfo_json = {}
    serie_path = ''
    episode_local = False
    remote = False
    season = item.infoLabels['season']
    sesxepi = []
    
    if not item.nfo and item.path and not item.path.endswith('.json'):
        item.nfo = filetools.join(SERIES, item.path, 'tvshow.nfo')
    if item.nfo:
        head, nfo_json = videolibrarytools.read_nfo(item.nfo)                   #... tratamos de recuperar la info de la Serie

    # Miramos si los episodio se van a mover a un site remoto, con lo que no pueden usar archivos locales
    move_to_remote = config.get_setting("move_to_remote", "downloads", default=[])
    for serie, address in move_to_remote:
        if serie.lower() in item.contentSerieName.lower():                      # Si está en la lista es que es remoto
            remote = True
            break
    
    # El item que pretendemos descargar YA es un episodio
    if item.contentType == "episode" and item.sub_action not in sub_action:
        episodes = [item.clone()]
        if item.strm_path and not remote:
            episode_local = True

    # El item es uma serie o temporada
    elif item.contentType in ["tvshow", "season"] or item.sub_action in sub_action:
        # importamos el canal
        channel = __import__('channels.%s' % item.contentChannel, None, None, ["channels.%s" % item.contentChannel])
        # Obtenemos el listado de episodios
        if item.sub_action in sub_action:                                       # Si viene de Play...
            if item.sub_action in ["unseen", "auto"] and config.is_xbmc() and item.nfo:
                
                from platformcode import xbmc_videolibrary
                import xbmc
                xbmc_videolibrary.update(folder='_scan_series')                 # Se escanea el directorio de series para catalogar en Kodi
                while xbmc.getCondVisibility('Library.IsScanningVideo()'):      # Se espera a que acabe
                    time.sleep(1)
                xbmc_videolibrary.mark_content_as_watched_on_alfa(item.nfo)     # Sincronizamos los Vistos de Kodi con Alfa
                
                head, nfo_json = videolibrarytools.read_nfo(item.nfo)           #... tratamos de recuperar la info de la Serie
            if item.url_tvshow:
                item.url = item.url_tvshow
            elif nfo_json:
                if item.contentChannel != 'newpct1':
                    item.url = nfo_json.library_urls[item.contentChannel]
                else:
                    category = item.category.lower()
                    if item.category_alt:
                        category = item.category_alt.lower()
                    item.url = nfo_json.library_urls[category]
                if not item.url_tvshow:
                    item.url_tvshow = item.url
            
            if item.sub_action in ["auto"]:
                if not nfo_json: return []
                
                # Calculamos la última temporada disponible
                y = []
                patron = 'season (\d+)'
                matches = re.compile(patron, re.DOTALL).findall(str(nfo_json.library_playcounts))
                for x in matches:
                    y += [int(x)]
                max_ses = max(y)
                
                # Verificamos si hay algún episodio no visto de la última temporada
                for ses_epi, visto in list(nfo_json.library_playcounts.items()):
                    ses_num = 0
                    try:
                        if scrapertools.find_single_match(ses_epi, '^(\d+)x\d+'):
                            ses_num = int(scrapertools.find_single_match(ses_epi, '^(\d+)x\d+'))
                        else:
                            continue
                        if max_ses != ses_num:
                            continue
                        if visto == 0:
                            continue
                        break
                    except:
                        logger.error(ses_epi)
                        continue
                else:
                    return []
            
            if not item.from_action: item.from_action = 'episodios'
            if not item.contentAction: item.contentAction = item.from_action
            if item.sub_action in ["tvshow", "unseen", "auto"]:
                item.contentType = "tvshow"
                item.season_colapse = False
                item.ow_force = 1
                if item.infoLabels['season']: del item.infoLabels['season']
            else:
                item.contentType = "season"
                item.season_colapse = True
            if item.infoLabels['episode']: del item.infoLabels['episode']
            if item.from_num_season_colapse: del item.from_num_season_colapse
            if item.password: del item.password
            if item.torrent_info: del item.torrent_info
            if item.torrent_alt: del item.torrent_alt

        if (item.strm_path or item.nfo):                                        # Si viene de Videoteca, usamos los .jsons
            if item.strm_path: serie_path = filetools.dirname(item.strm_path)
            if not serie_path and item.nfo: serie_path = filetools.dirname(item.nfo)
            serie_listdir = sorted(filetools.listdir(serie_path))
            episodes = []
            episode_local = True
            
            for file in serie_listdir:
                if not file.endswith('.json'):
                    continue
                if item.channel not in file and item.category.lower() not in file and item.category_alt.lower() not in file:
                    continue
                if item.sub_action == "season" and scrapertools.find_single_match(file, '^(\d+)x\d+') \
                                != str(item.infoLabels['season']):
                    continue
                episode = Item().fromjson(filetools.read(filetools.join(serie_path, file)))
                if remote:                                                      # Quitamos las referencias locales
                    if episode.emergency_urls: del episode.emergency_urls
                    if episode.torrent_info: del episode.torrent_info
                    if episode.server: del episode.server
                if episode.emergency_urls and not episode.emergency_urls[0][0].startswith('http') \
                                    and episode.emergency_urls[0][0].endswith('.torrent'):
                    episode.server = 'torrent'
                    episode.action = 'play'
                episode.strm_path = filetools.join(serie_path, '%sx%s.strm' % (str(episode.infoLabels['season']), \
                                    str(episode.infoLabels['episode']).zfill(2))).replace(SERIES, '')
                episode.sub_action = item.sub_action
                episode.channel = item.contentChannel
                episode.downloadServer = {}
                
                #logger.debug(episode)
                episodes.append(episode.clone())
        
        else:
            episodes = getattr(channel, item.contentAction)(item)               # Si no viene de Videoteca, descargamos desde la web

    itemlist = []

    # Tenemos las lista, ahora vamos a comprobar
    for episode in episodes:
        if episode.action in ["add_serie_to_library", "actualizar_titulos"] or not episode.action:
            continue

        # Si se ha llamado con la opción de NO Vistos, se comprueba contra el .NFO de la serie
        if item.sub_action in ["unseen", "auto"] and nfo_json.library_playcounts \
                        and episode.contentSeason and episode.contentEpisodeNumber:   # Descargamos solo los episodios NO vistos
            seaxepi = '%sx%s' % (str(episode.contentSeason), str(episode.contentEpisodeNumber).zfill(2))
            try:
                if nfo_json.library_playcounts[seaxepi] == 1:
                    continue
            except:
                pass
        
        # Ajustamos el num. de episodio en episode.strm_path y episode.emergency_urls
        if item.sub_action in ["tvshow", "unseen"] and episode.strm_path:
            episode.strm_path = re.sub(r'x\d{2,}.strm', 'x%s.strm' % str(episode.contentEpisodeNumber).zfill(2), episode.strm_path)
            
        if episode.emergency_urls and not remote:
            for x, emergency_urls in enumerate(episode.emergency_urls[0]):
                if not episode_local:
                    episode.emergency_urls[0][x] = re.sub(r'x\d{2,}\s*\[', 'x%s [' \
                            % str(episode.contentEpisodeNumber).zfill(2), emergency_urls)
                if len(episode.emergency_urls[0][x]) == 0 or not filetools.exists(filetools.join(SERIES, episode.emergency_urls[0][x])):
                    del episode.emergency_urls[0][x]
            if len(episode.emergency_urls) > 1 and not episode_local:
                for x, emergency_urls in enumerate(episode.emergency_urls):
                    if x == 0:
                        continue
                    episode.emergency_urls[x] = []
            if not episode.emergency_urls[0]:
                del episode.emergency_urls
            elif episode_local:
                episode.torrent_alt = episode.url
                episode.url = episode.emergency_urls[0][0]

        # Si partiamos de un item que ya era episodio estos datos ya están bien, no hay que modificarlos
        if item.contentType != "episode":
            episode.contentAction = episode.action
            episode.contentChannel = episode.channel
        episode.contentChannel = generictools.verify_channel(episode.contentChannel)

        # Si es una temporada, descartameos lo que sea de esa temporada
        if item.contentType in ["season"] or item.sub_action in ["season"]:
            if season and episode.infoLabels['season']:
                if season != episode.infoLabels['season']:
                    continue
                sesxepi_now = '%sx%s' % (str(episode.infoLabels['season']), str(episode.infoLabels['episode']).zfill(2))
                if sesxepi_now in str(sesxepi):
                    continue
                sesxepi += [sesxepi_now]

        # Si el resultado es una temporada, no nos vale, tenemos que descargar los episodios de cada temporada
        if episode.contentType == "season":
            itemlist.extend(get_episodes(episode))

        # Si el resultado es un episodio ya es lo que necesitamos, lo preparamos para añadirlo a la descarga
        if episode.contentType == "episode":

            # Pasamos el id al episodio
            if not episode.infoLabels["tmdb_id"]:
                episode.infoLabels["tmdb_id"] = item.infoLabels["tmdb_id"]

            # Episodio, Temporada y Titulo
            if not episode.contentSeason or not episode.contentEpisodeNumber:
                season_and_episode = scrapertools.get_season_and_episode(episode.title)
                if season_and_episode:
                    episode.contentSeason = season_and_episode.split("x")[0]
                    episode.contentEpisodeNumber = season_and_episode.split("x")[1]

            # Buscamos en tmdb
            if item.infoLabels["tmdb_id"]:
                scraper.find_and_set_infoLabels(episode)

            # Episodio, Temporada y Titulo
            if not episode.contentTitle:
                episode.contentTitle = re.sub("\[[^\]]+\]|\([^\)]+\)|\d*x\d*\s*-", "", episode.title).strip()

            if not episode.contentSeason: episode.contentSeason = 1
            if not episode.contentEpisodeNumber: episode.contentEpisodeNumber = 1
            episode.downloadFilename = filetools.validate_path(filetools.join(item.downloadFilename, "%dx%0.2d - %s" % (
                episode.contentSeason, episode.contentEpisodeNumber, episode.contentTitle.strip())))

            itemlist.append(episode)
        # Cualquier otro resultado no nos vale, lo ignoramos
        else:
            logger.info("Omitiendo item no válido: %s" % episode.action)
            
    try:
        from core import tmdb
        if len(itemlist) > 1:
            itemlist = sorted(itemlist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))
        tmdb.set_infoLabels(itemlist, True, idioma_busqueda='es,en')
    except:
        logger.error(traceback.format_exc(1))

    return itemlist


def write_json(item):
    logger.info()

    item.action = "menu"
    item.channel = "downloads"
    item.unify = True
    del item.unify
    item.folder = True
    del item.folder
    if item.sub_action in ["auto"]:
        item.downloadStatus = STATUS_CODES.auto
    else:
        item.downloadStatus = STATUS_CODES.stoped
    item.downloadQueued = 0
    item.downloadProgress = 0
    item.downloadSize = 0
    item.downloadCompleted = 0
    if not item.contentThumbnail:
        item.contentThumbnail = item.thumbnail

    for name in ["text_bold", "text_color", "text_italic", "context", "totalItems", "viewmode", "title", "contentTitle",
                 "thumbnail"]:
        if name in item.__dict__:
            item.__dict__.pop(name)

    item.path = str(time.time()) + ".json"
    
    item_control = item.clone()
    if item_control.strm_path and item.server == 'torrent':
        if item_control.contentType == 'movie':
            PATH = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_movies"))
        else:
            PATH = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_tvshows"))
        item_control.strm_path = item_control.strm_path.replace(PATH, '')
    
    filetools.write(filetools.join(config.get_setting("downloadlistpath"), item.path), item_control.tojson())
    time.sleep(0.1)


def save_download(item, silent=False):
    logger.info()

    # Menu contextual
    if item.from_action and item.from_channel:
        item.channel = item.from_channel
        item.action = item.from_action
        del item.from_action
        del item.from_channel

    item.contentChannel = item.channel
    item.contentAction = item.action
    if item.contentAction in ['get_seasons', 'update_tvshow']:
        item.contentAction = 'episodios'

    if item.contentType in ["tvshow", "episode", "season"]:
        save_download_tvshow(item, silent=silent)

    elif item.contentType == "movie":
        save_download_movie(item)

    else:
        save_download_video(item)


def save_download_video(item):
    logger.info("contentAction: %s | contentChannel: %s | contentTitle: %s" % (
        item.contentAction, item.contentChannel, item.contentTitle))

    set_movie_title(item)

    item.downloadFilename = filetools.validate_path("%s [%s]" % (item.contentTitle.strip(), item.contentChannel))

    write_json(item)

    if not platformtools.dialog_yesno(config.get_localized_string(30101), config.get_localized_string(70189)):
        platformtools.dialog_ok(config.get_localized_string(30101), item.contentTitle,
                                config.get_localized_string(30109))
    else:
        item.downloadCompleted = 0
        if item.server == 'torrent':
            item.downloadCompleted = 1
        item.downloadQueued = 1
        update_json(item.path, {"downloadCompleted": item.downloadCompleted, "downloadQueued": item.downloadQueued})
        start_download(item)


def save_download_movie(item, silent=False):
    logger.info("contentAction: %s | contentChannel: %s | contentTitle: %s" % (
        item.contentAction, item.contentChannel, item.contentTitle))

    if not silent: progreso = platformtools.dialog_progress(config.get_localized_string(30101), config.get_localized_string(70191))

    set_movie_title(item)

    if item.emergency_urls:                                                     # Se intenta usar el .torrent local
        PATH = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_movies"))
        for x, emergency_urls in enumerate(item.emergency_urls[0]):
            if len(item.emergency_urls[0][x]) == 0 or not filetools.exists(filetools.join(PATH, item.emergency_urls[0][x])):
                del item.emergency_urls[0][x]
        if not item.emergency_urls[0]:
            del item.emergency_urls
        else:
            item.torrent_alt = item.url
            item.url = item.emergency_urls[0][0]

    result = ''
    if not item.infoLabels["tmdb_id"] and not channeltools.is_adult(item.channel):
        result = scraper.find_and_set_infoLabels(item)
    if not result:
        if not silent: progreso.close()
        return save_download_video(item)

    if not silent: progreso.update(0, config.get_localized_string(60062))

    item.downloadFilename = filetools.validate_path("%s [%s]" % (item.contentTitle.strip(), item.contentChannel))

    write_json(item)

    if not silent: progreso.close()

    if not silent and not platformtools.dialog_yesno(config.get_localized_string(30101), config.get_localized_string(70189)):
        platformtools.dialog_ok(config.get_localized_string(30101), item.contentTitle,
                                config.get_localized_string(30109))
    elif not silent:
        item.downloadCompleted = 0
        if item.server == 'torrent':
            item.downloadCompleted = 1
        item.downloadQueued = 1
        update_json(item.path, {"downloadCompleted": item.downloadCompleted, "downloadQueued": item.downloadQueued})
        start_download(item)


def save_download_tvshow(item, silent=False):
    logger.info("contentAction: %s | contentChannel: %s | contentType: %s | contentSerieName: %s | sub_action: %s" % (
        item.contentAction, item.contentChannel, item.contentType, item.contentSerieName, item.sub_action))

    if not silent: progreso = platformtools.dialog_progress(config.get_localized_string(30101), config.get_localized_string(70188))

    result = ''
    if not item.infoLabels["tmdb_id"] and not channeltools.is_adult(item.channel):
        result = scraper.find_and_set_infoLabels(item)

    item.downloadFilename = filetools.validate_path("%s [%s]" % (item.contentSerieName, item.contentChannel))

    if not silent: progreso.update(0, config.get_localized_string(70186) + '\n' + config.get_localized_string(70187) % item.contentChannel)

    episodes = get_episodes(item)

    if not silent: progreso.update(0, config.get_localized_string(70190) + '\n' + " ")

    epi_saved = []
    for x, i in enumerate(episodes):
        if not silent: progreso.update(old_div(x * 100, len(episodes)),  
                        "%dx%0.2d: %s" % (i.contentSeason, i.contentEpisodeNumber, i.contentTitle))
        write_json(i)
        epi_saved += ['%sx%s' % (str(i.contentSeason), str(i.contentEpisodeNumber).zfill(2))]
    if not silent: progreso.close()
    logger.info("Serie: %s | Total Saved: %s | Episodes: %s" % (item.contentSerieName, str(len(episodes)), str(sorted(epi_saved))))

    if not silent and not platformtools.dialog_yesno(config.get_localized_string(30101), config.get_localized_string(70189)):
        platformtools.dialog_ok(config.get_localized_string(30101),
                                str(len(episodes)) + " capitulos de: " + item.contentSerieName,
                                config.get_localized_string(30109))
    elif not silent:
        for i in episodes:
            i.downloadCompleted = 0
            if i.server == 'torrent':
                i.downloadCompleted = 1
            i.downloadQueued = 1
            update_json(i.path, {"downloadCompleted": i.downloadCompleted, "downloadQueued": i.downloadQueued})
        for i in episodes:
            time.sleep(0.5)
            if filetools.exists(filetools.join(DOWNLOAD_LIST_PATH, i.path)):
                res = start_download(i)
                if res == STATUS_CODES.canceled:
                    break
            else:
                logger.info("Episodio BORRADO: Serie: %s | Episode: %sx%s | Archivo: %s" % \
                            (i.contentSerieName, str(i.contentSeason), str(i.contentEpisodeNumber).zfill(2), i.path))


def set_movie_title(item):
    if not item.contentTitle:
        item.contentTitle = re.sub("\[[^\]]+\]|\([^\)]+\)", "", item.contentTitle).strip()

    if not item.contentTitle:
        item.contentTitle = re.sub("\[[^\]]+\]|\([^\)]+\)", "", item.title).strip()
