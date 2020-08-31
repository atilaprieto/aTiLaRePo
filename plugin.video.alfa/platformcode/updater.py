# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Updater (kodi)
# --------------------------------------------------------------------------------

import os
import time
import threading
import traceback

from platformcode import config, logger, platformtools

from core import httptools
from core import jsontools
from core import downloadtools
from core import ziptools

def check_addon_init():
    logger.info()
    
    # Subtarea de monitor.  Se activa cada X horas para comprobar si hay FIXES al addon
    def check_addon_monitor():
        logger.info()
        
        # Obtiene el íntervalo entre actualizaciones y si se quieren mensajes
        try:
            timer = int(config.get_setting('addon_update_timer'))       # Intervalo entre actualizaciones, en Ajustes de Alfa
            if timer <= 0:
                return                                                  # 0.  No se quieren actualizaciones
            verbose = config.get_setting('addon_update_message')
        except:
            timer = 12                                                  # Por defecto cada 12 horas
            verbose = False                                             # Por defecto, sin mensajes
        timer = timer * 3600                                            # Lo pasamos a segundos

        if config.get_platform(True)['num_version'] >= 14:              # Si es Kodi, lanzamos el monitor
            import xbmc
            monitor = xbmc.Monitor()
        else:                                                           # Lanzamos solo una actualización y salimos
            check_addon_updates(verbose)                                # Lanza la actualización
            return
            
        while not monitor.abortRequested():                             # Loop infinito hasta cancelar Kodi

            check_addon_updates(verbose)                                # Lanza la actualización
            
            if monitor.waitForAbort(timer):                             # Espera el tiempo programado o hasta que cancele Kodi
                break                                                   # Cancelación de Kodi, salimos
                
        return
                
    # Lanzamos en Servicio de actualización de FIXES
    try:
        threading.Thread(target=check_addon_monitor).start()            # Creamos un Thread independiente, hasta el fin de Kodi
        time.sleep(5)                                                   # Dejamos terminar la primera verificación...
    except:                                                             # Si hay problemas de threading, se llama una sola vez
        try:
            timer = int(config.get_setting('addon_update_timer'))       # Intervalo entre actualizaciones, en Ajustes de Alfa
            if timer <= 0:
                return                                                  # 0.  No se quieren actualizaciones
            verbose = config.get_setting('addon_update_message')
        except:
            verbose = False                                             # Por defecto, sin mensajes
            pass
        check_addon_updates(verbose)                                    # Lanza la actualización, en Ajustes de Alfa
        time.sleep(5)                                                   # Dejamos terminar la primera verificación...
              
    return
    

def check_addon_updates(verbose=False):
    logger.info()

    ADDON_UPDATES_JSON = 'https://extra.alfa-addon.com/addon_updates/updates.json'
    ADDON_UPDATES_ZIP = 'https://extra.alfa-addon.com/addon_updates/updates.zip'

    try:
        last_fix_json = os.path.join(config.get_runtime_path(), 'last_fix.json')   # información de la versión fixeada del usuario
        # Se guarda en get_runtime_path en lugar de get_data_path para que se elimine al cambiar de versión

        try:
            localfilename = os.path.join(config.get_data_path(), 'temp_updates.zip')
            if os.path.exists(localfilename): os.remove(localfilename)
        except:
            pass
        
        # Descargar json con las posibles actualizaciones
        # -----------------------------------------------
        data = httptools.downloadpage(ADDON_UPDATES_JSON, timeout=5).data
        if data == '': 
            logger.info('No se encuentran actualizaciones del addon')
            if verbose:
                platformtools.dialog_notification('Alfa ya está actualizado', 'No hay ninguna actualización urgente')
            check_update_to_others(verbose=verbose)                             # Comprueba las actualuzaciones de otros productos
            return False

        data = jsontools.load(data)
        if 'addon_version' not in data or 'fix_version' not in data: 
            logger.info('No hay actualizaciones del addon')
            if verbose:
                platformtools.dialog_notification('Alfa ya está actualizado', 'No hay ninguna actualización urgente')
            check_update_to_others(verbose=verbose)                             # Comprueba las actualuzaciones de otros productos
            return False

        # Comprobar versión que tiene instalada el usuario con versión de la actualización
        # --------------------------------------------------------------------------------
        current_version = config.get_addon_version(with_fix=False)
        if current_version != data['addon_version']:
            logger.info('No hay actualizaciones para la versión %s del addon' % current_version)
            if verbose:
                platformtools.dialog_notification('Alfa ya está actualizado', 'No hay ninguna actualización urgente')
            check_update_to_others(verbose=verbose)                             # Comprueba las actualuzaciones de otros productos
            return False

        if os.path.exists(last_fix_json):
            try:
                lastfix =  {} 
                lastfix = jsontools.load(open(last_fix_json, "r").read())
                if lastfix['addon_version'] == data['addon_version'] and lastfix['fix_version'] == data['fix_version']:
                    logger.info('Ya está actualizado con los últimos cambios. Versión %s.fix%d' % (data['addon_version'], data['fix_version']))
                    if verbose:
                        platformtools.dialog_notification('Alfa ya está actualizado', 'Versión %s.fix%d' % (data['addon_version'], data['fix_version']))
                    check_update_to_others(verbose=verbose)                             # Comprueba las actualuzaciones de otros productos
                    return False
            except:
                if lastfix:
                    logger.error('last_fix.json: ERROR en: ' + str(lastfix))
                else:
                    logger.error('last_fix.json: ERROR desconocido')
                lastfix =  {}

        # Descargar zip con las actualizaciones
        # -------------------------------------

        downloadtools.downloadfile(ADDON_UPDATES_ZIP, localfilename, silent=True)
        
        # Descomprimir zip dentro del addon
        # ---------------------------------
        try:
            unzipper = ziptools.ziptools()
            unzipper.extract(localfilename, config.get_runtime_path())
        except:
            import xbmc
            xbmc.executebuiltin('Extract("%s", "%s")' % (localfilename, config.get_runtime_path()))
            time.sleep(1)
        
        # Borrar el zip descargado
        # ------------------------
        try:
            os.remove(localfilename)
        except:
            pass
        
        # Guardar información de la versión fixeada
        # -----------------------------------------
        if 'files' in data: data.pop('files', None)
            
        open(last_fix_json, "w").write(jsontools.dump(data))
        
        logger.info('Addon actualizado correctamente a %s.fix%d' % (data['addon_version'], data['fix_version']))
        if verbose:
            platformtools.dialog_notification('Alfa actualizado a', 'Versión %s.fix%d' % (data['addon_version'], data['fix_version']))
        
        check_update_to_others(verbose=verbose)                                 # Comprueba las actualuzaciones de otros productos
        return True

    except:
        logger.error('Error al comprobar actualizaciones del addon!')
        logger.error(traceback.format_exc())
        if verbose:
            platformtools.dialog_notification('Alfa actualizaciones', 'Error al comprobar actualizaciones')
        check_update_to_others(verbose=verbose)                                 # Comprueba las actualuzaciones de otros productos
        return False


def check_update_to_others(verbose=False):
    logger.info()
    
    try:
        import xbmc
        
        list_folder = os.listdir(os.path.join(config.get_runtime_path(), 'tools'))
        for folder in list_folder:
            in_folder = os.path.join(config.get_runtime_path(), 'tools', folder)
            if not os.path.isdir(in_folder):
                continue

            out_folder = xbmc.translatePath(os.path.join('special://home/', 'addons', folder))
            if os.path.exists(out_folder):
                
                copytree(in_folder, out_folder)
                
                logger.info('%s updated' % folder)
    except:
        logger.error('Error al actualizar OTROS paquetes')
        logger.error(traceback.format_exc())
        
    try:
        from lib import alfa_assistant
        res, addonid = alfa_assistant.update_alfa_assistant()
    except:
        logger.error("Alfa Assistant.  Error en actualización")
        logger.error(traceback.format_exc())


def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy a directory tree using copy2().
    
    *** Obtained from Kody Python 2.7 Shutil ***
    *** Ignores error if dst-dir exists ***

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    length = 16*1024
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.exists(dst):
        os.makedirs(dst)
    
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)

        if symlinks and os.path.islink(srcname):
            linkto = os.readlink(srcname)
            os.symlink(linkto, dstname)
        elif os.path.isdir(srcname):
            copytree(srcname, dstname, symlinks, ignore)
        else:
            # Will raise a SpecialFileError for unsupported file types
            with open(srcname, 'rb') as fsrc:
                with open(dstname, 'wb') as fdst:
                    while 1:
                        buf = fsrc.read(length)
                        if not buf:
                            break
                        fdst.write(buf)
