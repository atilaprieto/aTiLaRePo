#   script.limpiarkodi
#   Copyright (C) 2016  Teco
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.



import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib2,urllib
import re
import os
addon_id = 'script.limpiarkodi'
fanart = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
icon3 = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'luar.png'))
icon2 = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'indigo.png'))
thumbnailPath = xbmc.translatePath('special://thumbnails');
cachePath = os.path.join(xbmc.translatePath('special://home'), 'cache')
cdmPath = os.path.join(xbmc.translatePath('special://home'), 'cdm')
purgePath = os.path.join(xbmc.translatePath('special://home/addons'), 'packages')
tempPath = xbmc.translatePath('special://home/addons/temp/')
indigoPath = xbmc.translatePath('special://home/addons/plugin.program.indigo')
ltempPath = xbmc.translatePath('special://home/temp')
addonPath = os.path.join(os.path.join(xbmc.translatePath('special://home'), 'addons'),'script.limpiarkodi')
mediaPath = os.path.join(addonPath, 'media')
databasePath = xbmc.translatePath('special://database')
THUMBS = xbmc.translatePath(os.path.join('special://home/userdata/Thumbnails',''))
#######################################################################
#                          CLASSES
#######################################################################

class cacheEntry:
    def __init__(self, namei, pathi):
        self.name = namei
        self.path = pathi



def mainMenu():

    addItem('Limpiar Cache y Rom','url', 1,icon)
    addItem('Borrar Imagenes', 'url', 2,icon)
    addItem('Limpiar Temp', 'url', 3,icon)
    addItem('Purgar Packages', 'url', 4,icon)
    addItem('Actualizar Addons y Repositorios', 'url', 5,icon)
    addItem('Dependencias', 'url', 8,icon)
    addItem('Herramientas Luar', 'url', 8,icon3)
    addItem('Elimina Indigo', 'url', 7,icon2)



    
#######################################################################
#                        Add to menus
#######################################################################

def addLink(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok


def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addItem(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty('fanart_image', fanart)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok

#######################################################################
#                        Parses Choice
#######################################################################
      
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
    return param

#######################################################################
#                        Work Functions
#######################################################################
def setupCacheEntries():
    entries = 21 #make sure this refelcts the amount of entries you have
    dialogName = [" YouTube", " UrlResolve", " Simple Cacher", " Simple Downloader", " Metadatautils", " Streamlink", " Tvalacarta", " Resolveurl", " Alfa Downloads", " Metahandler", " Youtube.dl", " Extendedinfo", " TheMovieDB", " Extendedinfo/YouTube", " Autocompletion/Google", " Autocompletion/Bing", " Universalscrapers", " Torrents Alfa", " MediaExplorer Downloads", " Balandro Downloads", " MediaExplorer Torrent"]
    pathName = ["special://profile/addon_data/plugin.video.youtube/kodion", "special://profile/addon_data/script.module.urlresolve/cache",
                    "special://profile/addon_data/script.module.simplecache", "special://profile/addon_data/script.module.simple.downloader",
                    "special://profile/addon_data/script.module.metadatautils/animatedgifs", "special://profile/addon_data/script.module.streamlink/base","special://profile/addon_data/plugin.video.tvalacarta/downloads", "special://profile/addon_data/script.module.resolveurl/cache", "special://profile/addon_data/plugin.video.alfa/downloads", "special://profile/addon_data/script.module.metahandler/meta_cache", "special://profile/addon_data/script.module.youtube.dl/tmp", "special://profile/addon_data/script.extendedinfo/images", "special://profile/addon_data/script.extendedinfo/TheMovieDB", "special://profile/addon_data/script.extendedinfo/YouTube", "special://profile/addon_data/plugin.program.autocompletion/Google", "special://profile/addon_data/plugin.program.autocompletion/Bing", "special://profile/addon_data/script.module.universalscrapers", "special://profile/addon_data/plugin.video.alfa/videolibrary/temp_torrents_Alfa", "special://profile/addon_data/plugin.video.mediaexplorer/downloads", "special://profile/addon_data/plugin.video.balandro/downloads", "special://profile/addon_data/plugin.video.mediaexplorer/torrent"]
                    
    cacheEntries = []
    
    for x in range(entries):
        cacheEntries.append(cacheEntry(dialogName[x],pathName[x]))
    
    return cacheEntries


def clearCache():

    if os.path.exists(cachePath)==True:
        for root, dirs, files in os.walk(cachePath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Borrar Cache", str(file_count) + " Archivos Encontrados", "Desea Eliminarlos?"):
                
                    for f in files:
                        try:
                            if (f == "*.log" or f == "*.old.log"): continue
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass
    if os.path.exists(tempPath)==True:    
        for root, dirs, files in os.walk(tempPath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Borrar Archivos en ROM Cache", str(file_count) + " Archivos Encontrados", "Desea Eliminarlos?"):
                    for g in files:
                        try:
                            if (g == "*.log" or f == "*.old.log"): continue
                            os.unlink(os.path.join(root, g))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass
    if os.path.exists(cdmPath)==True:    
        for root, dirs, files in os.walk(cdmPath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Borrar Archivos en CDM", str(file_count) + " Archivos Encontrados", "Desea Eliminarlos?"):
                    for h in files:
                        try:
                            if (h == "*.dmp" or f == "*.txt"): continue
                            os.unlink(os.path.join(root, h))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass
    if os.path.exists(purgePath)==True:
        for root, dirs, files in os.walk(purgePath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Borrar Cache", str(file_count) + " Archivos Encontrados", "Desea Eliminarlos?"):
                
                    for f in files:
                        try:
                            if (f == "*.*" or f == "*.*"): continue
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass
    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')
        
        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)
        
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Borra ATV2 Cache ", str(file_count) + " Archivos Encontrados 'Otros'", "Desea Eliminarlo?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')
        
        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)
        
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Borra ATV2 Cache ", str(file_count) + " Archivos Encontrados 'LocalAndRental'", "Desea Eliminarlos?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass

    cacheEntries = setupCacheEntries()

    for entry in cacheEntries:
        clear_cache_path = xbmc.translatePath(entry.path)
        if os.path.exists(clear_cache_path)==True:    
            for root, dirs, files in os.walk(clear_cache_path):
                file_count = 0
                file_count += len(files)
                if file_count > 0:

                    dialog = xbmcgui.Dialog()
                    if dialog.yesno("Limpia tu Kodi",str(file_count) + "%s Archivos Cache Encontrados"%(entry.name), "Desea Eliminarlos?"):
                        for f in files:
                            os.unlink(os.path.join(root, f))
                        for d in dirs:
                            shutil.rmtree(os.path.join(root, d))
                            
                else:
                    pass


    dialog = xbmcgui.Dialog()
    dialog.ok("Limpia tu Kodi", "Todos los Archivos se Limpiaron con Exito")


def deleteThumbnails():

    if os.path.exists(thumbnailPath)==True:  
            dialog = xbmcgui.Dialog()
            if dialog.yesno("Borrar Imagenes", "Esta opcion eliminara todas las Imagenes", "Desea continuar?"):
                for root, dirs, files in os.walk(thumbnailPath):
                    file_count = 0
                    file_count += len(files)
                    if file_count > 0:
                        for f in files:
                            try:
                                os.unlink(os.path.join(root, f))
                            except:
                                pass


    if os.path.exists(THUMBS):
        try:
            for root, dirs, files in os.walk(THUMBS):
                file_count = 0
                file_count += len(files)
                # Count files and give option to delete
                if file_count > 0:
                        for f in files:    os.unlink(os.path.join(root, f))
                        for d in dirs: shutil.rmtree(os.path.join(root, d))
        except:
            pass

    try:
        text13 = os.path.join(databasePath,"Textures13.db")
        os.unlink(text13)
    except:
        pass
    dialog.ok("[COLOR=red]Atencion[/COLOR]", "Debe Reiniciar Kodi Para Aplicar los Cambios")
        
def purgeCacheRom():

    tempPath = xbmc.translatePath('special://home/addons/temp')
    dialog = xbmcgui.Dialog()
    for root, dirs, files in os.walk(tempPath):
            file_count = 0
            file_count += len(files)
    if os.path.exists(tempPath)==True:    
        for root, dirs, files in os.walk(tempPath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Borrar Archivos en Temp", str(file_count) + " Archivos Encontrados", "Desea Eliminarlos?"):

                    for f in files:
                        try:
                            if (f == "*.*" or f == "*.*"): continue
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass

def purgePackages():

    purgePath = xbmc.translatePath('special://home/addons/packages')
    dialog = xbmcgui.Dialog()
    for root, dirs, files in os.walk(purgePath):
            file_count = 0
            file_count += len(files)
    if dialog.yesno("Borrar contenido en Paquetes", "%d Paquetes Encontrados."%file_count, "Desea Eliminarlos?"):
        for root, dirs, files in os.walk(purgePath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:            
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
                dialog = xbmcgui.Dialog()
                dialog.ok("Limpia tu Kodi", "Borrar todo el contenido de Paquetes")
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok("Limpia tu Kodi", "Eliminados Paquetes")

def update():

        xbmc.executebuiltin('UpdateAddonRepos()')
        xbmc.executebuiltin('UpdateLocalAddons()')
        xbmc.executebuiltin('RunAddon(plugin.video.palantir)')
        xbmc.executebuiltin("ActivateWindow(home)")
        xbmc.executebuiltin("ReloadSkin()")
        xbmcgui.Dialog().notification('Limpia Tu Kodi', "Repositorios [COLOR green]Actualizados[/COLOR]")

def depen():

        xbmc.executebuiltin('ActivateWindow(10025,addons://dependencies/&quot;)')


def deleteindigo():

    indigoPath = xbmc.translatePath('special://home/addons/plugin.program.indigo')
    dialog = xbmcgui.Dialog()
    for root, dirs, files in os.walk(indigoPath):
            file_count = 0
            file_count += len(files)
    if os.path.exists(indigoPath)==True:    
        for root, dirs, files in os.walk(indigoPath):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Este Proceso Desinstala Indigo", str() + "Para desinstslar completamenete [COLOR red]reinicie Kodi[/COLOR] despues del proceso.", "Esta seguro de que desea eliminar Indigo?"):

                    for f in files:
                        try:
                            if (f == "*.*" or f == "*.*"): continue
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass


def luar():

        xbmc.executebuiltin('RunAddon(script.luar)')






#######################################################################
#                       Support
#######################################################################


params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

if mode==None or url==None or len(url)<1:
        mainMenu()
       
elif mode==1:
        clearCache()
        
elif mode==2:
        deleteThumbnails()

elif mode==3:
        purgeCacheRom()

elif mode==4:
        purgePackages()

elif mode==5:
        update()

elif mode==6:
        luar()

elif mode==7:
        deleteindigo()

elif mode==8:
        depen()

xbmcplugin.endOfDirectory(int(sys.argv[1]))