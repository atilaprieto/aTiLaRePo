# -*- coding: utf-8 -*-

import os, time, traceback

from platformcode import config, logger, platformtools
from core import httptools, jsontools, filetools, downloadtools, scrapertools


def check_addon_updates(verbose=False, force=False):
    logger.info()

    color_alert = config.get_setting('notification_alert_color', default='red')
    color_infor = config.get_setting('notification_infor_color', default='pink')
    color_adver = config.get_setting('notification_adver_color', default='violet')
    color_avis  = config.get_setting('notification_avis_color', default='yellow')
    color_exec  = config.get_setting('notification_exec_color', default='cyan')

    get_last_chrome_list()

    ADDON_UPDATES_JSON = 'https://balandro.tk/addon_updates/updates-v2.0.0.json'
    ADDON_UPDATES_ZIP  = 'https://balandro.tk/addon_updates/updates-v2.0.0.zip'

    try:
        last_fix_json = os.path.join(config.get_runtime_path(), 'last_fix.json')   # información de la versión fixeada del usuario
        # Se guarda en get_runtime_path en lugar de get_runtime_path para que se elimine al cambiar de versión
        if force and os.path.exists(last_fix_json): os.remove(last_fix_json)

        # Descargar json con las posibles actualizaciones
        data = httptools.downloadpage(ADDON_UPDATES_JSON, timeout=2).data
        if data == '':
            logger.info('No se encuentra addon_updates')
            if verbose:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No se encuentra addon_updates[/COLOR][/B]' % color_alert)
            return False

        data = jsontools.load(data)
        if 'addon_version' not in data or 'fix_version' not in data:
            logger.info('Sin Fix actualizaciones pdtes.')
            if verbose:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin Fix actualizaciones pdtes.[/COLOR][/B]' % color_adver)
            return False

        # Comprobar versión que tiene instalada el usuario con versión de la actualización
        current_version = config.get_addon_version(with_fix=False)
        if current_version != data['addon_version']:
            logger.info('Versión Incorrecta NO se actualizan Fixes para la versión %s' % current_version)
            if verbose:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Versión incorrecta NO se actualizan Fixes[/COLOR][/B]' % color_alert)
            return False

        if os.path.exists(last_fix_json):
            lastfix = jsontools.load(filetools.read(last_fix_json))
            if lastfix['addon_version'] == data['addon_version'] and lastfix['fix_version'] == data['fix_version']:
                logger.info('Está actualizado. Versión %s.fix%d' % (data['addon_version'], data['fix_version']))
                if verbose:
                    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Está actualizado versión %s.fix%d[/COLOR][/B]' % color_adver, (data['addon_version'], data['fix_version']))
                return False

        # Descargar zip con las actualizaciones
        localfilename = os.path.join(config.get_data_path(), 'temp_updates.zip')
        if os.path.exists(localfilename): os.remove(localfilename)

        down_stats = downloadtools.do_download(ADDON_UPDATES_ZIP, config.get_data_path(), 'temp_updates.zip', silent=True, resume=False)
        if down_stats['downloadStatus'] != 2: # 2:completed
            logger.info('No se pudo descargar la actualización')
            if verbose:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No se pudo descargar la actualización[/COLOR][/B]' % color_alert)
            return False

        # Descomprimir zip dentro del addon
        try:
            import zipfile
            dir = zipfile.ZipFile(localfilename,'r')
            dir.extractall(config.get_runtime_path())
            dir.close()
        except:
            import xbmc
            xbmc.executebuiltin('Extract("%s", "%s")' % (localfilename, config.get_runtime_path()))
            time.sleep(2)

        # Borrar el zip descargado
        os.remove(localfilename)

        # Guardar información de la versión fixeada
        # ~ if 'files' in data: data.pop('files', None)  # necesario para visalizar en helper el contenido del fix

        filetools.write(last_fix_json, jsontools.dump(data))

        logger.info('Addon actualizado correctamente a %s.fix%d' % (data['addon_version'], data['fix_version']))
        if verbose:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Actualizado a la versión %s.fix%d[/COLOR][/B]' % color_avis, (data['addon_version'], data['fix_version']))
        return True
    except:
        logger.error('Error comprobación actualizaciones!')
        logger.error(traceback.format_exc())
        if verbose:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Error comprobación actualizaciones[/COLOR][/B]' % color_alert)
        return False

def get_last_chrome_list():
    logger.info()

    ver_stable_chrome = config.get_setting("ver_stable_chrome", default=True)

    if ver_stable_chrome:
        try:
           data = httptools.downloadpage('https://omahaproxy.appspot.com/all?csv=1').data
           web_last_ver_chrome = scrapertools.find_single_match(data, "win64,stable,([^,]+),")
        except:
           web_last_ver_chrome = ''

        if not web_last_ver_chrome == '':
            config.set_setting('chrome_last_version', web_last_ver_chrome)

