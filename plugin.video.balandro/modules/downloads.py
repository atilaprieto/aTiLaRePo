# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Balandro - Descargas
# ------------------------------------------------------------

import os, time, glob

from platformcode import config, logger, platformtools
from core.item import Item
from core import filetools, jsontools

STATUS_CODES = type("StatusCode", (), {"stopped": 0, "canceled": 1, "completed": 2, "error": 3})

# Ruta para las descargas
download_path = config.get_setting('downloadpath', default='')
if download_path == '':
    download_path = filetools.join(config.get_data_path(), 'downloads')

if not filetools.exists(download_path):
    filetools.mkdir(download_path)



def mainlist(item):
    logger.info()
    item.category = 'Descargas'
    
    itemlist = []
    
    if download_path.startswith('smb://'):
        fichs = sorted(filetools.listdir(download_path))
        ficheros = [filetools.join(download_path, fit) for fit in fichs if fit.endswith('.json')]
    else:
        path = filetools.join(download_path, '*.json')
        ficheros = glob.glob(path)
        ficheros.sort(key=os.path.getmtime, reverse=False)

    for down_path in ficheros:

        # ~ it = Item().fromjson(path=down_path) # falla con smb://
        it = Item().fromjson(filetools.read(down_path))

        it.from_channel = it.channel
        it.from_action = it.action
        it.channel = item.channel
        it.action = 'acciones_enlace'
        it.jsonfile = down_path
        it.folder = False

        if it.downloadStatus == STATUS_CODES.completed:
            it.title = '[B][COLOR gold][Ok] %s [%s][/COLOR][/B]' % (it.downloadFilename, config.format_bytes(it.downloadSize))

        elif it.downloadStatus == STATUS_CODES.canceled:
            it.title = '[COLOR red][%s%%] %s [%s de %s][/COLOR]' % (int(it.downloadProgress), it.downloadFilename, config.format_bytes(it.downloadCompleted), config.format_bytes(it.downloadSize))

        elif it.downloadStatus == STATUS_CODES.error:
            it.title = '[I][COLOR gray][Error] %s[/COLOR][/I]' % it.downloadFilename

        else:
            it.title = '[I][COLOR gray][???] %s[/COLOR][/I]' % it.downloadFilename
            
        itemlist.append(it)

    return itemlist


def acciones_enlace(item):
    logger.info()

    item.__dict__['channel'] = item.__dict__.pop('from_channel')
    item.__dict__['action'] = item.__dict__.pop('from_action')

    if item.downloadStatus == STATUS_CODES.completed:
        acciones = ['Reproducir vídeo', 'Eliminar descarga', 'Guardar una copia']

    elif item.downloadStatus == STATUS_CODES.canceled:
        acciones = ['Continuar descarga', 'Eliminar descarga']

    # ~ elif item.downloadStatus == STATUS_CODES.error:
    else:
        acciones = ['Eliminar descarga']

    ret = platformtools.dialog_select('¿Qué hacer con esta descarga?', acciones)
    if ret == -1: 
        return False # pedido cancel

    elif acciones[ret] == 'Eliminar descarga':
        if not platformtools.dialog_yesno('Eliminar descarga', '¿ Confirmas el borrado de la descarga %s ?' % item.title, 'Se eliminará el fichero %s y su json con la información.' % item.downloadFilename): 
            return False

        path_video = filetools.join(download_path, item.downloadFilename)
        if item.downloadFilename and filetools.exists(path_video):
            filetools.remove(path_video)

        if item.jsonfile and filetools.exists(item.jsonfile):
            filetools.remove(item.jsonfile)
        
        platformtools.itemlist_refresh()
        return True

    elif acciones[ret] == 'Continuar descarga':
        item.__dict__.pop('jsonfile')
        server_item = Item().fromjson(item.__dict__.pop('server_item'))
        return download_video(server_item, item)

    elif acciones[ret] == 'Reproducir vídeo':
        import xbmcgui, xbmc
        mediaurl = filetools.join(download_path, item.downloadFilename)
        
        xlistitem = xbmcgui.ListItem(path=mediaurl)
        platformtools.set_infolabels(xlistitem, item, True)

        # se lanza el reproductor (no funciona si el play es desde el diálogo info !?)
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        playlist.add(mediaurl, xlistitem)
        xbmc.Player().play(playlist, xlistitem)
        return True

    elif acciones[ret] == 'Guardar una copia':
        import xbmcgui
        destino_path = xbmcgui.Dialog().browseSingle(3, 'Seleccionar carpeta dónde copiar', 'files', '', False, False, '')
        if not destino_path: return False
        origen = filetools.join(download_path, item.downloadFilename)
        destino = filetools.join(destino_path, item.downloadFilename)
        if not filetools.copy(origen, destino, silent=False):
            platformtools.dialog_ok(config.__addon_name, 'Error, no se ha podido copiar el fichero!', origen, destino)
            return False
        platformtools.dialog_notification('Fichero copiado', destino_path)
        return True


# Llamada desde menú contextual para una peli/episodio (parecido a platformtools.play_from_itemlist)
def save_download(item):
    logger.info()

    # Si se llega aquí mediante el menú contextual, hay que recuperar los parámetros action y channel
    if item.from_action: item.__dict__["action"] = item.__dict__.pop("from_action")
    if item.from_channel: item.__dict__["channel"] = item.__dict__.pop("from_channel")

    try:
        if item.action == 'findvideos':
            if item.channel == 'tracking': canal = __import__('modules.' + item.channel, fromlist=[''])
            else: canal = __import__('channels.' + item.channel, fromlist=[''])
            itemlist = canal.findvideos(item)

            # Para algunos servers (ej: gamovideo) se necesita la url para usar como referer
            if item.channel == 'tracking' and len(itemlist) > 0: item.url = itemlist[0].parent_item_url
            
            # Reordenar/Filtrar enlaces
            itemlist = filter(lambda it: it.action == 'play', itemlist) # aunque por ahora no se usan action != 'play' en los findvideos
            from core import servertools
            itemlist = servertools.filter_and_sort_by_quality(itemlist)
            itemlist = servertools.filter_and_sort_by_server(itemlist)
            itemlist = servertools.filter_and_sort_by_language(itemlist)

            if len(itemlist) == 0:
                platformtools.dialog_ok(config.__addon_name, 'No hay enlaces disponibles')

            itemlist = platformtools.formatear_enlaces_servidores(itemlist)
            
            import xbmc
            erroneos = []
            # Bucle hasta cancelar o descargar
            while not xbmc.Monitor().abortRequested():
                opciones = []
                for i, it in enumerate(itemlist):
                    if i in erroneos:
                        opciones.append('[I][COLOR gray]%s[/COLOR][/I]' % config.quitar_colores(it.title))
                    else:
                        opciones.append(it.title)

                seleccion = platformtools.dialog_select('Enlaces disponibles en %s' % itemlist[0].channel, opciones)
                if seleccion == -1:
                    # ~ platformtools.dialog_notification(config.__addon_name, 'Descarga cancelada')
                    break
                else:
                    # Si el canal tiene play propio
                    canal_play = __import__('channels.' + itemlist[seleccion].channel, fromlist=[''])
                    if hasattr(canal_play, 'play'):
                        itemlist_play = canal_play.play(itemlist[seleccion])

                        if len(itemlist_play) > 0 and isinstance(itemlist_play[0], Item):
                            ok_play = download_video(itemlist_play[0], item)

                        elif len(itemlist_play) > 0 and isinstance(itemlist_play[0], list):
                            itemlist[seleccion].video_urls = itemlist_play
                            ok_play = download_video(itemlist[seleccion], item)

                        elif isinstance(itemlist_play, basestring):
                            ok_play = False
                            dialog_ok(config.__addon_name, itemlist_play)

                        else:
                            ok_play = False
                            platformtools.dialog_ok(config.__addon_name, 'No se puede descargar')

                    else:
                        ok_play = download_video(itemlist[seleccion], item)
                    
                    if ok_play: break
                    else: erroneos.append(seleccion)

        else:
            platformtools.dialog_ok(config.__addon_name, 'Nada a descargar!')

    except:
        import traceback
        logger.error(traceback.format_exc())

        platformtools.dialog_ok(config.__addon_name, 'Error al descargar!')



# (parecido a platformtools.play_video pero para descargar)
def download_video(item, parent_item):
    logger.info(item)
    logger.info(parent_item)
    
    if item.video_urls:
        video_urls, puedes, motivo = item.video_urls, True, ""
    else:
        from core import servertools
        url_referer = item.url_referer if item.url_referer else parent_item.url
        video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing(item.server, item.url, url_referer=url_referer)
    
    if not puedes:
        platformtools.dialog_ok("No puedes descargar este vídeo porque...", motivo, item.url)
        return False

    opciones = []
    for video_url in video_urls:
        opciones.append("Descargar " + video_url[0])

    # Si hay varias opciones dar a elegir, si sólo hay una reproducir directamente
    if len(opciones) > 1:
        seleccion = platformtools.dialog_select("Elige una opción", opciones)
    else:
        seleccion = 0

    if seleccion == -1:
        return True
    else:
        mediaurl, view, mpd = platformtools.get_video_seleccionado(item, seleccion, video_urls)
        if mediaurl == '':
            platformtools.dialog_ok(config.__addon_name, 'No se encuentra el vídeo!')
            return False
        if mediaurl.endswith('.m3u8') or 'm3u8' in video_urls[seleccion][0].lower():
            platformtools.dialog_ok(config.__addon_name, 'No se puede descargar en formato m3u8')
            return False

        if parent_item.contentType == 'movie':
            file_name = '%s' % parent_item.contentTitle # config.text_clean(...)
        else:
            file_name = '%s - S%02dE%02d' % (parent_item.contentSerieName, parent_item.contentSeason, parent_item.contentEpisodeNumber)

        ch_name = parent_item.channel if parent_item.channel != 'tracking' else item.channel
        file_name += ' [%s][%s]' % (ch_name, item.server)

        return do_download(mediaurl, file_name, parent_item, item)


def do_download(mediaurl, file_name, parent_item, server_item):
    from core import downloadtools

    # Limpiar caracteres para nombre de fichero válido
    file_name = config.text_clean(file_name)

    # Guardar info del vídeo en json
    path_down_json = filetools.join(download_path, file_name + '.json')
    parent_item.server_item = server_item.tojson() # Guardar info del server por si hay que continuar la descarga
    write_download_json(path_down_json, parent_item)

    # Lanzamos la descarga
    down_stats = downloadtools.do_download(mediaurl, download_path, file_name)
    
    # Actualizar info de la descarga en json
    update_download_json(path_down_json, down_stats)

    if down_stats['downloadStatus'] == STATUS_CODES.error:
        return False
    else:
        if down_stats['downloadStatus'] == STATUS_CODES.completed:
            platformtools.dialog_ok(config.__addon_name, 'Descarga finalizada correctamente', file_name, config.format_bytes(down_stats['downloadSize']))

        platformtools.itemlist_refresh()
        return True


def write_download_json(path, item):
    if item.__dict__.has_key('context'): item.__dict__.pop('context')
    item.downloadStatus = STATUS_CODES.stopped
    item.downloadProgress = 0
    item.downloadSize = 0
    item.downloadCompleted = 0

    filetools.write(path, item.tojson())
    time.sleep(0.1)

def update_download_json(path, params):
    item = Item().fromjson(filetools.read(path))
    item.__dict__.update(params)
    filetools.write(path, item.tojson())
