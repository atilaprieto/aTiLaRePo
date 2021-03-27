# -*- coding: utf-8 -*-

import os

from platformcode import config, logger, platformtools
from core.item import Item
from core import filetools


# Abrir ventana de Configuración
def open_settings(item):
    logger.info()

    config.__settings__.openSettings()


# Comprobar nuevos episodios en cualquiera de las series en seguimiento
def comprobar_nuevos_episodios(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, 'Comprobando si existe nuevos episodios', time=2000, sound=False)

    from core import trackingtools
    trackingtools.check_and_scrap_new_episodes()


# Comprobar actualizaciones (llamada desde una opción de la Configuración)
def check_addon_updates(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, 'Comprobando actualizaciones')

    from platformcode import updater
    updater.check_addon_updates(verbose=True)


# Comprobar actualizaciones (llamada desde una opción de la Configuración)
def check_addon_updates_force(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, 'Forzando actualizaciones')

    from platformcode import updater
    updater.check_addon_updates(verbose=True, force=True)


# Borrar caché de TMDB (llamada desde una opción de la Configuración)
def drop_db_cache(item):
    logger.info()

    if platformtools.dialog_yesno('Borrar Caché Tmdb', '[COLOR red]¿ Eliminar Todos los registros de la caché de Tmdb ?[/COLOR]'): 
        from core import tmdb
        if tmdb.drop_bd():
            platformtools.dialog_notification(config.__addon_name, 'Caché Tmdb borrada', time=2000, sound=False)


# Limpiar caché de TMDB (llamada desde una opción de la Configuración)
def clean_db_cache(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, 'Inspeccionado la Caché de Tmdb')

    import sqlite3, time
    from core import filetools

    fecha_caducidad = time.time() - (31 * 24 * 60 * 60) # al cabo de 31 días

    fname = filetools.join(config.get_data_path(), "tmdb.sqlite")
    conn = sqlite3.connect(fname)
    c = conn.cursor()

    c.execute('SELECT COUNT() FROM tmdb_cache')
    numregs = c.fetchone()[0]

    c.execute('SELECT COUNT() FROM tmdb_cache WHERE added < ?', (fecha_caducidad,))
    numregs_expired = c.fetchone()[0]

    txt = 'El caché de Tmdb ocupa [COLOR gold]%s[/COLOR]' % config.format_bytes(filetools.getsize(fname))
    txt += ' y contiene [COLOR gold]%s[/COLOR] registros.' % numregs
    txt += ' ¿ Borrar los [COLOR blue]%s[/COLOR] registros que tienen más de un mes de antiguedad de Tmdb ?' % numregs_expired

    if platformtools.dialog_yesno('Limpiar caché Tmdb', txt): 
        c.execute('DELETE FROM tmdb_cache WHERE added < ?', (fecha_caducidad,))
        conn.commit()
        conn.execute('VACUUM')
        platformtools.dialog_notification(config.__addon_name, 'Limpiado Caché Tmdb', time=2000, sound=False)

    conn.close()


# Mostrar diálogo de información de un item haciendo una nueva llamada a Tmdb para recuperar más datos
def more_info(item):
    logger.info()

    # Si se llega aquí mediante el menú contextual, hay que recuperar los parámetros action y channel
    if item.from_action: item.__dict__['action'] = item.__dict__.pop('from_action')
    if item.from_channel: item.__dict__['channel'] = item.__dict__.pop('from_channel')

    import xbmcgui
    from core import tmdb

    tmdb.set_infoLabels_item(item)

    xlistitem = xbmcgui.ListItem()
    platformtools.set_infolabels(xlistitem, item, True)

    ret = xbmcgui.Dialog().info(xlistitem)


# Mostrar diálogo con los trailers encontrados para un item
def search_trailers(item):
    logger.info()

    import xbmcgui, xbmc
    from core.tmdb import Tmdb

    tipo = 'movie' if item.contentType == 'movie' else 'tv'
    nombre = item.contentTitle if item.contentType == 'movie' else item.contentSerieName
    if item.infoLabels['tmdb_id']:
        tmdb_search = Tmdb(id_Tmdb=item.infoLabels['tmdb_id'], tipo=tipo, idioma_busqueda='es')
    else:
        anyo = item.infoLabels['year'] if item.infoLabels['year'] else '-'
        tmdb_search = Tmdb(texto_buscado=nombre, tipo=tipo, year=anyo, idioma_busqueda='es')

    opciones = []
    resultados = tmdb_search.get_videos()
    for res in resultados:
        # ~ logger.debug(res)
        it = xbmcgui.ListItem(res['name'], '[%sp] (%s)' % (res['size'], res['language']))
        if item.thumbnail: it.setArt({ 'thumb': item.thumbnail })
        opciones.append(it)

    if len(resultados) == 0:
        notification_d_ok = config.get_setting('notification_d_ok', default=True)
        if notification_d_ok:
            platformtools.dialog_ok(nombre, 'No se encuentra ningún tráiler en TMDB')
        else:
            platformtools.dialog_notification(nombre, '[COLOR moccasin]No se encuentra ningún tráiler en TMDB[/COLOR]')
    else:
        while not xbmc.Monitor().abortRequested(): # (while True)
            ret = xbmcgui.Dialog().select('Tráilers para %s' % nombre, opciones, useDetails=True)
            if ret == -1: break

            platformtools.dialog_notification(resultados[ret]['name'], 'Cargando tráiler ...', time=3000, sound=False)
            from core import servertools
            if 'youtube' in resultados[ret]['url']:
                video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing('youtube', resultados[ret]['url'])
            else:
                video_urls = [] #TODO si no es youtube ...
                logger.debug(resultados[ret])
            if len(video_urls) > 0:
                # ~ logger.debug(video_urls)
                xbmc.Player().play(video_urls[-1][1]) # el último es el de más calidad
                xbmc.sleep(1000)
                while not xbmc.Monitor().abortRequested() and xbmc.Player().isPlaying():
                    xbmc.sleep(1000)
            else:
                platformtools.dialog_notification(resultados[ret]['name'], 'No se puede reproducir el tráiler', time=3000, sound=False)

            if len(resultados) == 1: break # si sólo hay un vídeo no volver al diálogo de tráilers


def manto_proxies(item):
    logger.info()

    from core import channeltools

    filtros = {'searchable': True}

    opciones = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, 'No hay canales de este tipo')
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma Eliminar los Proxies existentes en Todos los canales ?[/COLOR]'):
       for ch in ch_list:
           cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
           cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'

           if not config.get_setting(cfg_proxies_channel, default=''):
               if not config.get_setting(cfg_proxytools_max_channel, default=''):
                   continue

           config.set_setting(cfg_proxies_channel, '')
           config.get_setting(cfg_proxytools_max_channel, '')

       platformtools.dialog_notification(config.__addon_name, 'Proxies eliminados')


def manto_params(item):
    logger.info()

    if platformtools.dialog_yesno(config.__addon_name, '¿ Confirma Restablecer a sus valores por defecto los Parámetros Internos del addon ?'):
        config.set_setting('adults_password', '')

        config.set_setting('channel_cinecalidad_dominio', '')
        config.set_setting('channel_documaniatv_rua', '')
        config.set_setting('channel_hdfull_dominio', '')

        # ~ config.set_setting('downloadpath', '')  No funciona

        config.set_setting('chrome_last_version', '88.0.4324.152')

        config.set_setting('debug', '0')

        platformtools.dialog_notification(config.__addon_name, 'Parámetros restablecidos')

def manto_cookies(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'cookies.dat')

    existe = filetools.exists(path)
    if existe == False:
         platformtools.dialog_notification(config.__addon_name, '[COLOR red]No hay fichero de Cookies[/COLOR]')
         return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR moccasin]¿ Confirma Eliminar el fichero de Cookies ?[/COLOR]'):
        filetools.remove(path)
        platformtools.dialog_notification(config.__addon_name, 'Fichero Cookies eliminado')

def manto_folder_cache(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'cache')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[COLOR moccasin]Aún no hay Carpeta Caché[/COLOR]')
        return

    if platformtools.dialog_yesno(config.__addon_name, '¿ Confirma Eliminar Toda la carpeta Caché ?'):
        filetools.rmdirtree(path)
        platformtools.dialog_notification(config.__addon_name, 'Carpeta Caché eliminada')

def manto_tracking_dbs(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'tracking_dbs')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[COLOR moccasin]Aún no tiene Preferidos[/COLOR]')
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma Eliminar Todo el contenido de sus Preferidos ?[/COLOR]'):
        filetools.rmdirtree(path)
        platformtools.dialog_notification(config.__addon_name, 'Contenido Preferidos eliminado')

def manto_folder_downloads(item):
    logger.info()

    downloadpath = config.get_setting('downloadpath', default='')

    if downloadpath:
        path = downloadpath
    else:
        path = os.path.join(config.get_data_path(), 'downloads')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[COLOR moccasin]Aún no tiene Descargas[/COLOR]')
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma Eliminar el contenido de Todas sus Descargas ?[/COLOR]'):
        filetools.rmdirtree(path)
        platformtools.dialog_notification(config.__addon_name, 'Contenido Descargas eliminado')

def manto_folder_addon(item):
    logger.info()

    path = config.get_data_path()

    existe = filetools.exists(path)
    if not existe == False:
        if platformtools.dialog_yesno(config.__addon_name, '[COLOR yellow]¿ ATENCION: Confirma Eliminar Todos los Datos del Addon ?[/COLOR]'):
            filetools.rmdirtree(path) # ~  deja solo el fichero settings.xml porque lo tiene bloqueado el sistema
            platformtools.dialog_notification(config.__addon_name, 'Datos del Addon eliminados')

def adults_password(item):
    logger.info()
    if not config.get_setting('adults_password'):
        password = platformtools.dialog_numeric(0, 'Pin (4 dígitos)')
        if not password: return

        if len(password) != 4:
            platformtools.dialog_notification(config.__addon_name, 'El pin debe de ser de 4 dígitos')
            return

        confirmpassword = platformtools.dialog_numeric(0, 'Confirme el Pin')
        if not confirmpassword: return

        if password == confirmpassword:
            platformtools.dialog_notification(config.__addon_name, 'Pin establecido')
            config.set_setting('adults_password', password)
            return password
    else:
        password = platformtools.dialog_numeric(0, 'Introduzca el pin parental')
        try:
            if int(password) == int(config.get_setting('adults_password')):
                platformtools.dialog_notification(config.__addon_name, '[COLOR lime]Pin correcto[/COLOR]')
                return True
            else:
                platformtools.dialog_notification(config.__addon_name, '[COLOR red]Pin incorrecto[/COLOR]')
                return False
        except:
            return False