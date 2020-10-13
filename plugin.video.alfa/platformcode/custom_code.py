# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# Updater (kodi)
# --------------------------------------------------------------------------------

#from builtins import str
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import traceback
import xbmc
import xbmcaddon
import xbmcgui
import threading
import subprocess
import time
import os

from platformcode import config, logger, platformtools

from core import jsontools
from core import filetools
from core.item import Item

json_data_file_name = 'custom_code.json'


def init():
    logger.info()

    """
    Todo el código añadido al add-on se borra con cada actualización.  Esta función permite restaurarlo automáticamente con cada actualización.  Esto permite al usuario tener su propio código, bajo su responsabilidad, y restaurarlo al add-on cada vez que se actualiza.
    
    El mecanismo funciona copiando el contenido de la carpeta-arbol "./userdata/addon_data/plugin.video.alfa/custom_code/..." sobre
    las carpetas de código del add-on.  No verifica el contenido, solo vuelca(reemplaza) el contenido de "custom_code".
    
    El usuario almacenará en las subcarpetas de "custom_code" su código actualizado y listo para ser copiado en cualquier momento.
    Si no se desea que copie algo, simplemente se borra de "custom_code" y ya no se copiará en la próxima actualización.
    
    Los pasos que sigue esta función, son los siguientes:
    
    1.- La función se llama desde videolibrary_service.py, desde la función inicial:
            # Copia Custom code a las carpetas de Alfa desde la zona de Userdata
            from platformcode import custom_code
            custom_code.init()
            
    2.- En el inicio de Kodi, comprueba si existe la carpeta "custom_code" en "./userdata/addon_data/plugin.video.alfa/".  
        Si no existe, la crea y sale sin más, dando al ususario la posibilidad de copiar sobre esa estructura su código, 
        y que la función la vuelque sobre el add-on en el próximo inicio de Kodi.
        
    3.- En el siguiente inicio de Kodi, comprueba si existe el custom_code.json en la carpeta root del add-on.
        Si no existe, lo crea con el número de versión del add-on vacío, para permitir que se copien los archivos en esta pasada.
        
    4.- Verifica que el número de versión del add-on es diferente de el de custom_code.json.  Si es la misma versión, 
        se sale porque ya se realizo la copia anteriormente.
        Si la versión es distinta, se realiza el volcado de todos los archivos de la carpeta-árbol "custom_code" sobre el add-on.
        Si la carpeta de destino no existe, dará un error y se cancelará la copia.  Se considera que no tienen sentido nuevas carpetas.
        
    5.- Si la copia ha terminado con éxito, se actualiza el custom_code.json con el número de versión del add-on,
        para que en inicios sucesivos de Kodi no se realicen las copias, hasta que el add-on cambie de versión.
        En el número de versión del add-on no se considera el número de fix.
        
    Tiempos:    Copiando 7 archivos de prueba, el proceso ha tardado una décima de segundo.
    """

    try:
        #Comprime la BD de cache de TMDB para evitar que crezca demasiado
        bd_tmdb_maintenance()
        if config.get_setting('tmdb_cache_expire', default=4) == 4:
            config.set_setting('tmdb_cache_expire', 2)

        #Verifica si es necsario instalar script.alfa-update-helper
        verify_script_alfa_update_helper()
        
        #Borra el .zip de instalación de Alfa de la carpeta Packages, por si está corrupto, y que así se pueda descargar de nuevo
        version = 'plugin.video.alfa-%s.zip' % config.get_addon_version(with_fix=False)
        filetools.remove(filetools.join('special://home', 'addons', 'packages', version), True)
        
        #Borrar contenido de carpeta de Torrents y de Subtitles
        filetools.rmdirtree(filetools.join(config.get_videolibrary_path(), 'temp_torrents_Alfa'), silent=True)
        subtitle_path = config.get_kodi_setting("subtitles.custompath")
        ret = filetools.rmdirtree(subtitle_path, silent=True)
        if not ret: logger.error('RMDIR: ' + subtitle_path)
        time.sleep(1)
        ret = filetools.mkdir(subtitle_path, silent=True)
        if not ret: logger.error('MKDIR: ' + subtitle_path)

        #Verifica si Kodi tiene algún achivo de Base de Datos de Vídeo de versiones anteriores, entonces los borra
        verify_Kodi_video_DB()
        
        #Verifica si la Base de Datos de Vídeo tiene la fuente de CINE con useFolderNames=1
        set_Kodi_video_DB_useFolderNames()

        #LIBTORRENT: se descarga el binario de Libtorrent cada vez que se actualiza Alfa
        try:
            threading.Thread(target=update_libtorrent).start()          # Creamos un Thread independiente, hasta el fin de Kodi
            time.sleep(2)                                               # Dejamos terminar la inicialización...
        except:                                                         # Si hay problemas de threading, nos vamos
            logger.error(traceback.format_exc())
        
        #QUASAR: Preguntamos si se hacen modificaciones a Quasar
        if not filetools.exists(filetools.join(config.get_data_path(), "quasar.json")) \
                    and not config.get_setting('addon_quasar_update', default=False):
            question_update_external_addon("quasar")
        
        #QUASAR: Hacemos las modificaciones a Quasar, si está permitido, y si está instalado
        if config.get_setting('addon_quasar_update', default=False) or \
                    (filetools.exists(filetools.join(config.get_data_path(), \
                    "quasar.json")) and not xbmc.getCondVisibility('System.HasAddon("plugin.video.quasar")')):
            if not update_external_addon("quasar"):
                platformtools.dialog_notification("Actualización Quasar", "Ha fallado. Consulte el log")
        
        #Existe carpeta "custom_code" ? Si no existe se crea y se sale
        custom_code_dir = filetools.join(config.get_data_path(), 'custom_code')
        if not filetools.exists(custom_code_dir):
            create_folder_structure(custom_code_dir)
            return
        
        else:
            #Existe "custom_code.json" ? Si no existe se crea
            custom_code_json_path = config.get_runtime_path()
            custom_code_json = filetools.join(custom_code_json_path, 'custom_code.json')
            if not filetools.exists(custom_code_json):
                create_json(custom_code_json_path)
            
            #Se verifica si la versión del .json y del add-on son iguales.  Si es así se sale.  Si no se copia "custom_code" al add-on
            verify_copy_folders(custom_code_dir, custom_code_json_path)
        
        #Si se han quedado "colgadas" descargas con archivos .RAR, se intenta identificarlos y reactivar el UnRar
        reactivate_unrar(init=True, mute=True)
        
        #Inicia un rastreo de vídeos decargados desde .torrent: marca los VISTOS y elimina los controles de los BORRADOS
        from servers import torrent
        try:
            threading.Thread(target=torrent.mark_torrent_as_watched).start()    # Creamos un Thread independiente, hasta el fin de Kodi
            time.sleep(2)                                                       # Dejamos terminar la inicialización...
        except:                                                                 # Si hay problemas de threading, nos vamos
            logger.error(traceback.format_exc())
    except:
        logger.error(traceback.format_exc())


def bd_tmdb_maintenance():
    try:
        import sqlite3
        
        fname = filetools.join(config.get_data_path(), "alfa_db.sqlite")
        
        if filetools.exists(fname):
            conn = sqlite3.connect(fname)
            conn.execute("VACUUM")
            conn.close()
            logger.info('TMDB DB compacted')
    except:
        logger.error(traceback.format_exc(1))


def marshal_check():
    try:
        marshal_modules = ['lib/alfaresolver_py3', 'core/proxytools_py3']
        for module in marshal_modules:
            path = filetools.join(config.get_runtime_path(), filetools.dirname(module))
            path_list = filetools.listdir(path)
            library = filetools.dirname(module).rstrip('/')
            module_name = filetools.basename(module)
            for alt_module in path_list:
                if module_name not in alt_module:
                    continue
                if alt_module == module_name + '.py':
                    continue
                try:
                    alt_module_path = '%s.%s' % (library, alt_module.rstrip('.py'))
                    spec = __import__(alt_module_path, None, None, [alt_module_path])
                    if not spec:
                        raise
                except Exception as e:
                    logger.info('marshal_check ERROR in %s: %s' % (alt_module, str(e)), force=True)
                    continue
                filetools.copy(filetools.join(path, alt_module), filetools.join(path, module_name + '.py'), silent=True)
                logger.info('marshal_check FOUND: %s' % alt_module, force=True)
                break
            else:
                logger.info('marshal_check NOT FOUND: %s.py' % module_name, force=True)
    except:
        logger.error(traceback.format_exc(1))


def verify_script_alfa_update_helper():
    logger.info()
    
    import json
    from zipfile import ZipFile
    from core import httptools
    
    addonid = 'script.alfa-update-helper'
    package = addonid + '-0.0.1.zip'
    filetools.remove(filetools.join('special://home', 'addons', 'packages', package), True)
    
    # Comprobamos si hay acceso a Github
    url = 'https://github.com/alfa-addon/alfa-repo/raw/master/plugin.video.alfa/addon.xml'
    response = httptools.downloadpage(url, timeout=5, ignore_response_code=True, alfa_s=True)
    if response.code != 200 and not bool(xbmc.getCondVisibility("System.HasAddon(%s)" % addonid)):
        
        # Si no lo hay, descargamos el Script desde Bitbucket y lo salvamos a disco
        url = 'https://bitbucket.org/alfa_addon/alfa-repo/raw/master/script.alfa-update-helper/%s' % package
        response = httptools.downloadpage(url, ignore_response_code=True, alfa_s=True, json_to_utf8=False)
        if response.code == 200:
            zip_data = response.data
            addons_path = filetools.translatePath("special://home/addons")
            pkg_updated = filetools.join(addons_path, 'packages', package)
            res = filetools.write(pkg_updated, zip_data, mode='wb')
            
            # Verificamos el .zip
            ret = None
            try:
                with ZipFile(pkg_updated, "r") as zf:
                    ret = zf.testzip()
            except Exception as e:
                ret = str(e)
            if ret is not None:
                logger.error("Corrupted .zip, error: %s" % (str(ret)))
            else:
                # Si el .zip es correcto los extraemos e instalamos
                with ZipFile(pkg_updated, "r") as zf:
                    zf.extractall(addons_path)

                logger.info("Installing %s" % package)
                xbmc.executebuiltin('UpdateLocalAddons')
                time.sleep(2)
                method = "Addons.SetAddonEnabled"
                xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "id":1, "method": "%s", "params": {"addonid": "%s", "enabled": true}}' % (method, addonid))
                profile = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "Profiles.GetCurrentProfile"}'))
                logger.info("Reloading Profile...")
                user = profile["result"]["label"]
                xbmc.executebuiltin('LoadProfile(%s)' % user)


def create_folder_structure(custom_code_dir):
    logger.info()

    #Creamos todas las carpetas.  La importante es "custom_code".  Las otras sirven meramente de guía para evitar errores de nombres...
    filetools.mkdir(custom_code_dir)
    filetools.mkdir(filetools.join(custom_code_dir, 'channels'))
    filetools.mkdir(filetools.join(custom_code_dir, 'core'))
    filetools.mkdir(filetools.join(custom_code_dir, 'lib'))
    filetools.mkdir(filetools.join(custom_code_dir, 'platformcode'))
    filetools.mkdir(filetools.join(custom_code_dir, 'resources'))
    filetools.mkdir(filetools.join(custom_code_dir, 'servers'))

    return


def create_json(custom_code_json_path, json_name=json_data_file_name):
    logger.info()

    #Guardamaos el json con la versión de Alfa vacía, para permitir hacer la primera copia
    json_data_file = filetools.join(custom_code_json_path, json_name)
    if filetools.exists(json_data_file):
        filetools.remove(json_data_file)
    result = filetools.write(json_data_file, jsontools.dump({"addon_version": ""}))
    
    return


def verify_copy_folders(custom_code_dir, custom_code_json_path):
    logger.info()
    
    #verificamos si es una nueva versión de Alfa instalada o era la existente.  Si es la existente, nos vamos sin hacer nada
    json_data_file = filetools.join(custom_code_json_path, json_data_file_name)
    json_data = jsontools.load(filetools.read(json_data_file))
    current_version = config.get_addon_version(with_fix=False)
    if not json_data or not 'addon_version' in json_data: 
        create_json(custom_code_json_path)
        json_data = jsontools.load(filetools.read(json_data_file))
    try:
        if current_version == json_data['addon_version']:
            return
    except:
        logger.error(traceback.format_exc(1))
    
    #Ahora copiamos los archivos desde el área de Userdata, Custom_code, sobre las carpetas del add-on
    for root, folders, files in filetools.walk(custom_code_dir):
        for file in files:
            input_file = filetools.join(root, file)
            output_file = input_file.replace(custom_code_dir, custom_code_json_path)
            if not filetools.copy(input_file, output_file, silent=True):
                return
    
    #Guardamaos el json con la versión actual de Alfa, para no volver a hacer la copia hasta la nueva versión
    json_data['addon_version'] = current_version
    filetools.write(json_data_file, jsontools.dump(json_data))

    return

    
def question_update_external_addon(addon_name):
    logger.info(addon_name)
    
    #Verificamos que el addon está instalado
    stat = False
    if xbmc.getCondVisibility('System.HasAddon("plugin.video.%s")' % addon_name):
        #Si es la primera vez que se pregunta por la actualización del addon externo, recogemos la respuesta,  
        # guardaos un .json en userdat/alfa para no volver a preguntar otra vez, y se actualiza el setting en Alfa.
        stat = platformtools.dialog_yesno('Actualización de %s' % addon_name.capitalize(), '¿Quiere que actualicemos Quasar para que sea compatible con las últimas versiones de Kodi? (recomendado: SÍ)', '', 'Si actualiza Quasar, reinicie Kodi en un par de minutos')

        #Con la respuesta actualizamos la variable en Alfa settings.xml.  Se puede cambiar en Ajustes de Alfa, Otros
        if stat:
            config.set_setting('addon_quasar_update', True)
        else:
            config.set_setting('addon_quasar_update', False)
            
        #Creamos un .json en userdata para no volver a preguntar otra vez
        create_json(config.get_data_path(), "%s.json" % addon_name)
    
    return stat


def update_external_addon(addon_name):
    logger.info(addon_name)
    
    try:
        #Verificamos que el addon está instalado
        if xbmc.getCondVisibility('System.HasAddon("plugin.video.%s")' % addon_name):
            #Path de actualizaciones de Alfa
            alfa_addon_updates_mig = filetools.join(config.get_runtime_path(), "lib")
            alfa_addon_updates = filetools.join(alfa_addon_updates_mig, addon_name)
            
            #Path de destino en addon externo
            __settings__ = xbmcaddon.Addon(id="plugin.video." + addon_name)
            if addon_name.lower() in ['quasar', 'elementum']:
                addon_path_root = filetools.translatePath(__settings__.getAddonInfo('Path'))
                addon_path_mig = filetools.join(addon_path_root, filetools.join("resources", "site-packages"))
                addon_path = filetools.join(addon_path_mig, addon_name)
            else:
                addon_path_root = ''
                addon_path_mig = ''
                addon_path = ''
            
            #Hay modificaciones en Alfa? Las copiamos al addon, incuidas las carpetas de migración a PY3
            if filetools.exists(alfa_addon_updates) and filetools.exists(addon_path):
                for root, folders, files in filetools.walk(alfa_addon_updates_mig):
                    if ('future' in root or 'past' in root) and not 'concurrent' in root:
                        for file in files:
                            alfa_addon_updates_mig_folder = root.replace(alfa_addon_updates_mig, addon_path_mig)
                            if not filetools.exists(alfa_addon_updates_mig_folder):
                                filetools.mkdir(alfa_addon_updates_mig_folder)
                            if file.endswith('.pyo') or file.endswith('.pyd'):
                                continue
                            input_file = filetools.join(root, file)
                            output_file = input_file.replace(alfa_addon_updates_mig, addon_path_mig)
                            if not filetools.copy(input_file, output_file, silent=True):
                                logger.error('Error en la copia de MIGRACIÓN: Input: %s o Output: %s' % (input_file, output_file))
                                return False
                
                for root, folders, files in filetools.walk(alfa_addon_updates):
                    for file in files:
                        input_file = filetools.join(root, file)
                        output_file = input_file.replace(alfa_addon_updates, addon_path_mig)
                        if file in ['addon.xml']:
                            filetools.copy(input_file, filetools.join(addon_path_root, file), silent=True)
                            continue
                        if not filetools.copy(input_file, output_file, silent=True):
                            logger.error('Error en la copia: Input: %s o Output: %s' % (input_file, output_file))
                            return False
                return True
            else:
                logger.error('Alguna carpeta no existe: Alfa: %s o %s: %s' % (alfa_addon_updates, addon_name, addon_path_mig))
        # Se ha desinstalado Quasar, reseteamos la opción
        else:
            config.set_setting('addon_quasar_update', False)
            if filetools.exists(filetools.join(config.get_data_path(), "%s.json" % addon_name)):
                filetools.remove(filetools.join(config.get_data_path(), "%s.json" % addon_name))
            return True
    except:
        logger.error(traceback.format_exc())
    
    return False


def update_libtorrent():
    logger.info()
    
    if not config.get_setting("mct_buffer", server="torrent", default=""):
        default = config.get_setting("torrent_client", server="torrent", default=0)
        config.set_setting("torrent_client", default, server="torrent")
        config.set_setting("mct_buffer", "50", server="torrent")
        if config.get_setting("mct_download_path", server="torrent", default=config.get_setting("downloadpath")):
            config.set_setting("mct_download_path", config.get_setting("downloadpath"), server="torrent")
        config.set_setting("mct_background_download", True, server="torrent")
        config.set_setting("mct_rar_unpack", True, server="torrent")
        config.set_setting("bt_buffer", "50", server="torrent")
        if config.get_setting("bt_download_path", server="torrent", default=config.get_setting("downloadpath")):
            config.set_setting("bt_download_path", config.get_setting("downloadpath"), server="torrent")
        config.set_setting("mct_download_limit", "", server="torrent")
        config.set_setting("magnet2torrent", False, server="torrent")
        
    if not filetools.exists(filetools.join(config.get_setting("bt_download_path", server="torrent"), 'BT-torrents')):
        filetools.mkdir(filetools.join(config.get_setting("bt_download_path", server="torrent"), 'BT-torrents'))
    if not filetools.exists(filetools.join(config.get_setting("mct_download_path", server="torrent"), 'MCT-torrent-videos')):
        filetools.mkdir(filetools.join(config.get_setting("mct_download_path", server="torrent"), 'MCT-torrent-videos'))
        filetools.mkdir(filetools.join(config.get_setting("mct_download_path", server="torrent"), 'MCT-torrents'))
        
    if not filetools.exists(filetools.join(config.get_runtime_path(), "custom_code.json")) or not \
                    config.get_setting("unrar_path", server="torrent", default=""):
    
        path = filetools.join(config.get_runtime_path(), 'lib', 'rarfiles')
        creationflags = ''
        sufix = ''
        unrar = ''
        for device in filetools.listdir(path):
            if xbmc.getCondVisibility("system.platform.android") and 'android' not in device: continue
            if xbmc.getCondVisibility("system.platform.windows") and 'windows' not in device: continue
            if not xbmc.getCondVisibility("system.platform.windows") and not  xbmc.getCondVisibility("system.platform.android") \
                        and ('android' in device or 'windows' in device): continue
            if 'windows' in device:
                creationflags = 0x08000000
                sufix = '.exe'
            else:
                creationflags = ''
                sufix = ''
            unrar = filetools.join(path, device, 'unrar%s') % sufix
            if not filetools.exists(unrar): unrar = ''
            if unrar:
                if not xbmc.getCondVisibility("system.platform.windows"):
                    try:
                        if xbmc.getCondVisibility("system.platform.android"):
                            # Para Android copiamos el binario a la partición del sistema
                            unrar_org = unrar
                            unrar = filetools.join('special://xbmc/', 'files').replace('/cache/apk/assets', '')
                            if not filetools.exists(unrar):
                                filetools.mkdir(unrar)
                            unrar = filetools.join(unrar, 'unrar')
                            filetools.copy(unrar_org, unrar, silent=True)
                        
                        filetools.chmod(unrar, '777')
                    except:
                        logger.info('######## UnRAR ERROR in path: %s' % str(unrar), force=True)
                        logger.error(traceback.format_exc())

                try:
                    if xbmc.getCondVisibility("system.platform.windows"):
                        p = subprocess.Popen(unrar, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags)
                    else:
                        p = subprocess.Popen(unrar, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output_cmd, error_cmd = p.communicate()
                    if p.returncode != 0 or error_cmd:
                        logger.info('######## UnRAR returncode in module %s: %s, %s in %s' % \
                                (device, str(p.returncode), str(error_cmd), unrar), force=True)
                        unrar = ''
                    else:
                        logger.info('######## UnRAR OK in %s: %s' % (device, unrar), force=True)
                        break
                except:
                    logger.info('######## UnRAR ERROR in module %s: %s' % (device, unrar), force=True)
                    logger.error(traceback.format_exc(1))
                    unrar = ''
        
        if unrar: config.set_setting("unrar_path", unrar, server="torrent")

    # Ahora descargamos la última versión disponible de Libtorrent para esta plataforma
    try:
        version_base = filetools.join(config.get_runtime_path(), 'lib', 'python_libtorrent')
        if config.get_setting("libtorrent_version", server="torrent", default=""):
            current_system, current_version = config.get_setting("libtorrent_version", server="torrent", default="").split('/')
        else:
            current_system = ''
            current_version = ''

        version_base = filetools.join(version_base, current_system)
        if current_version:
            old_version = current_version
            new_version = sorted(filetools.listdir(version_base))
            new_version_alt = new_version[:]
            if new_version:
                for folder in new_version_alt:
                    if not filetools.isdir(filetools.join(version_base, folder)):
                        new_version.remove(folder)
                if old_version != new_version[-1]:
                    current_version = ''
            else:
                current_version = ''
    except:
        current_version = ''
        logger.error(traceback.format_exc(1))
    
    custom_code_json = filetools.exists(filetools.join(config.get_runtime_path(), "custom_code.json"))
    if custom_code_json and current_version:
        msg = 'Libtorrent_path: %s' % config.get_setting("libtorrent_path", server="torrent", default="")
        if current_version not in msg:
            msg += ' - Libtorrent_version: %s/%s' % (current_system, current_version)
        logger.info(msg, force=True)
        return

    try:
        logger.info('Libtorrent stored version: %s, %s' % (config.get_setting("libtorrent_version", \
                            server="torrent", default=""), str(custom_code_json)), force=True)
        from lib.python_libtorrent.python_libtorrent import get_libtorrent
    except Exception as e:
        logger.error(traceback.format_exc(1))
        if not PY3:
            e = unicode(str(e), "utf8", errors="replace").encode("utf8")
        config.set_setting("libtorrent_path", "", server="torrent")
        if not config.get_setting("libtorrent_error", server="torrent", default=''):
            config.set_setting("libtorrent_error", str(e), server="torrent")
    
    return
    

def verify_Kodi_video_DB():
    logger.info()
    import random
    
    platform = {}
    path = ''
    db_files = []
    
    try:
        path = filetools.join("special://masterprofile/", "Database")
        if filetools.exists(path):
            platform = config.get_platform(full_version=True)
            if platform and platform['num_version'] <= 19:
                db_files = filetools.walk(path)
                if filetools.exists(filetools.join(path, platform['video_db'])):
                    for root, folders, files in db_files:
                        for file in files:
                            if platform['video_db'] not in file:
                                if file.startswith('MyVideos'):
                                    randnum = str(random.randrange(1, 999999))
                                    filetools.rename(filetools.join(path, file), 'OLD_' + randnum +'_' + file)
                                    logger.error('BD obsoleta: ' + file)
                    
                else:
                    logger.error('Video_DB: ' + str(platform['video_db']) + ' para versión Kodi ' + str(platform['num_version']) + ' NO EXISTE. Analizar carpeta: ' + str(db_files))
            else:
                logger.error('Estructura de get_platform(full_version=True) incorrecta')
        else:
            logger.error('Path a Userdata/Database (' + path + ') no encontrado')
        
    except:
        logger.error('Platform: ' + str(platform) + ' / Path: ' + str(path) + ' / Files: ' + str(db_files))
        logger.error(traceback.format_exc())
        
    return
    

def set_Kodi_video_DB_useFolderNames():
    logger.info()
    
    from platformcode import xbmc_videolibrary

    strPath = filetools.join(config.get_videolibrary_path(), config.get_setting("folder_movies"), ' ').strip()
    scanRecursive = 2147483647
        
    sql = 'UPDATE path SET useFolderNames=1 WHERE (strPath="%s" and scanRecursive=%s and strContent="movies" ' \
                        'and useFolderNames=0)' % (strPath, scanRecursive)
                      
    nun_records, records = xbmc_videolibrary.execute_sql_kodi(sql)
    
    if nun_records > 0:
        logger.debug('MyVideos DB updated to Videolibrary %s useFolderNames=1' % config.get_setting("folder_movies"))


def reactivate_unrar(init=False, mute=True):
    logger.info()
    from servers import torrent
    
    torrent_paths = torrent.torrent_dirs()
    download_paths = []
    
    for torr_client, save_path_videos in list(torrent_paths.items()):
        if 'BT' not in torr_client and 'MCT' not in torr_client:
            torr_client = torr_client.lower()
        if '_' not in torr_client and '_web' not in torr_client and save_path_videos \
                            and save_path_videos not in str(download_paths):
            download_paths.append((torr_client, save_path_videos))              # Agregamos el path para este Cliente

            # Borramos archivos de control "zombies"
            rar_control = {}
            if filetools.exists(filetools.join(save_path_videos, '_rar_control.json')):
                rar_control = jsontools.load(filetools.read(filetools.join(save_path_videos, '_rar_control.json')))
            if rar_control and len(rar_control['rar_files']) == 1:
                ret = filetools.remove(filetools.join(save_path_videos, '_rar_control.json'), silent=True)

    search_for_unrar_in_error(download_paths, init=init)    


def search_for_unrar_in_error(download_paths, init=False):
    logger.info(download_paths)
    
    for torrent_client, path in download_paths:
        list_dir = filetools.listdir(path)
        for folder_w in list_dir:
            folder = filetools.join(path, folder_w)
            if filetools.isdir(folder):
                if not filetools.exists(filetools.join(folder, '_rar_control.json')):
                    continue
            else:
                if not '_rar_control.json' in folder:
                    continue

            rar_control = jsontools.load(filetools.read(filetools.join(folder, '_rar_control.json')))
            rar_control['status'] += ': Recovery'
            if ('UnRARing' in rar_control['status'] or 'RECOVERY' in rar_control['status']) and not init:
                continue
            if 'UnRARing' in rar_control['status'] or 'ERROR' in rar_control['status']:
                rar_control['status'] = 'RECOVERY: ' + rar_control['status']
            rar_control['download_path'] = folder
            rar_control['torr_client'] = torrent_client
            if 'ERROR' in rar_control['status'] or 'UnRARing' in rar_control['status'] \
                        or 'RECOVERY' in rar_control['status']:
                rar_control['error'] += 1
            ret = filetools.write(filetools.join(rar_control['download_path'], '_rar_control.json'), jsontools.dump(rar_control))
            logger.debug('%s, %s, %s, %s, %s, %s' % (rar_control['download_path'], \
                        rar_control['rar_names'][0], rar_control['password'], \
                        str(rar_control['error']), rar_control['error_msg'], rar_control['status']))
            if ('ERROR' in rar_control['status'] and rar_control['error'] > 2) \
                        or ('UnRARing' in rar_control['status'] and rar_control['error'] > 3) \
                        or ('RECOVERY' in rar_control['status'] and rar_control['error'] > 3)  \
                        or 'DONE' in rar_control['status']:
                continue
            
            if ret:
                try:
                    threading.Thread(target=call_unrar, args=(rar_control,)).start()    # Creamos un Thread independiente por UnRAR
                    time.sleep(1)                                               # Dejamos terminar la inicialización...
                except:                                                         # Si hay problemas de threading, pasamos al siguiente
                    logger.error(traceback.format_exc())

    if not init:
        sys.exit(0)


def call_unrar(rar_control):
    logger.info(rar_control['status'])
    
    item = Item().fromurl(rar_control['item'])
    mediaurl = rar_control['mediaurl']
    rar_files = rar_control['rar_files']
    torr_client = rar_control['torr_client']
    password = rar_control['password']
    size = rar_control['size']
    
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

    platformtools.set_infolabels(xlistitem, item)
    
    return platformtools.rar_control_mng(item, xlistitem, mediaurl, rar_files, \
                    torr_client, password, size, rar_control)

