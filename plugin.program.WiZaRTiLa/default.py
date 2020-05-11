import xbmc, xbmcaddon, xbmcgui, xbmcplugin,os,sys
import shutil
import urllib2,urllib
import re
import extract
import time
import downloader
import plugintools
import zipfile
import ntpath



USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
base='aTiLa'
ADDON=xbmcaddon.Addon(id='plugin.program.WiZaRTiLa')
    
    
VERSION = "1.3"


PATH = "WiZaRTiLa"            

dp           =  xbmcgui.DialogProgress()
dialog       =  xbmcgui.Dialog()
EXCLUDES     = ['plugin.program.WiZaRTiLa', 'Database']
HOME         =  xbmc.translatePath('special://home/')

    
def CATEGORIES():
    link = OPEN_URL('http://atilaprieto.myftp.org/compartidatila/Kodi/wizardtila/wizard.txt').replace('\n','').replace('\r','')
    match = re.compile('name="(.+?)".+?rl="(.+?)".+?mg="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(link)
    for name,url,iconimage,fanart,description in match:
        addDir(name,url,1,iconimage,fanart,description)
    setView('movies', 'MAIN')
	
    addDir('FRESH START','url',6,'','','')
        
    
def OPEN_URL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link
    
    
def wizard(name,url,description):
    path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
    dp = xbmcgui.DialogProgress()
    dp.create("WiZaRTiLa","Descargando ",'', 'Por favor, espere')
    lib=os.path.join(path, name+'.zip')
    try:
       os.remove(lib)
    except:
       pass
    downloader.download(url, lib, dp)
    addonfolder = xbmc.translatePath(os.path.join('special://','home'))
    time.sleep(2)
    dp.update(0,"", "Extrayendo Zip")
    print '======================================='
    print addonfolder
    print '======================================='
    extract.all(lib,addonfolder,dp)
    dialog = xbmcgui.Dialog()
    dialog.ok("DESCARGA COMPLETA", 'ATENCION la unica manera de aplicar los nuevos cambios', 'es forzar el cierre de Kodi. Haga clic en Aceptar para forzar a Kodi a cerrar,', 'NO use las opciones normales de Salir de Kodi. Si el cierre forzado no funciona por alguna razon, por favor Reinicie el Dispositivo o finalice la tarea manualmente')
    killxbmc()
        
      
        
def killxbmc():
    choice = xbmcgui.Dialog().yesno('Fuerza Cerrar Kodi', 'Estas a punto de cerrar Kodi', 'Te gustaria continuar?', nolabel='No, Cancelar',yeslabel='Si, Cerrar')
    if choice == 0:
        return
    elif choice == 1:
        pass
    myplatform = platform()
    print "Platform: " + str(myplatform)
    if myplatform == 'osx': # OSX
        print "############   try osx force close  #################"
        try: os.system('killall -9 XBMC')
        except: pass
        try: os.system('killall -9 Kodi')
        except: pass
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "Si estas viendo este mensaje es porque el cierre forzado", "ha fallado. Por favor, fuerza el cierre de Kodi [COLOR=lime]NO USE[/COLOR] el menu para Salir.",'')
    elif myplatform == 'linux': #Linux
        print "############   try linux force close  #################"
        try: os.system('killall XBMC')
        except: pass
        try: os.system('killall Kodi')
        except: pass
        try: os.system('killall -9 xbmc.bin')
        except: pass
        try: os.system('killall -9 kodi.bin')
        except: pass
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "Si estas viendo este mensaje es porque el cierre forzado", "ha fallado. Por favor, fuerza el cierre de Kodi [COLOR=lime]NO USE[/COLOR] el menu para Salir.",'')
    elif myplatform == 'android': # Android  
        print "############   try android force close  #################"
        try: os.system('adb shell am force-stop org.xbmc.kodi')
        except: pass
        try: os.system('adb shell am force-stop org.kodi')
        except: pass
        try: os.system('adb shell am force-stop org.xbmc.xbmc')
        except: pass
        try: os.system('adb shell am force-stop org.xbmc')
        except: pass        
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "Tu sistema ha sido detectado como Android, por tanto ", "[COLOR=yellow][B]DEBES[/COLOR][/B] forzar el cierre de Kodi. [COLOR=lime]NO USE[/COLOR] el menu para Salir.","Cierre con el Administrador de tareas (si no esta seguro, desenchufe su dispositivo).")
    elif myplatform == 'windows': # Windows
        print "############   try windows force close  #################"
        try:
            os.system('@ECHO off')
            os.system('tskill XBMC.exe')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('tskill Kodi.exe')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im Kodi.exe /f')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im XBMC.exe /f')
        except: pass
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "Si estas viendo este mensaje es porque el cierre forzado", "ha fallado. Por favor, fuerza el cierre de Kodi [COLOR=lime]NO USE[/COLOR] el menu para Salir.","Use el gestor de tareas y NO ALT F4")
    else: #ATV
        print "############   try atv force close  #################"
        try: os.system('killall AppleTV')
        except: pass
        print "############   try raspbmc force close  #################" #OSMC / Raspbmc
        try: os.system('sudo initctl stop kodi')
        except: pass
        try: os.system('sudo initctl stop xbmc')
        except: pass
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "Si estas viendo este mensaje es porque el cierre forzado", "ha fallado. Por favor, fuerza el cierre de Kodi [COLOR=lime]NO USE[/COLOR] el menu para Salir.","No se pudo detectar su Sistema, asi que desenchufe su dispositivo.")

def platform():
    if xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'windows'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    elif xbmc.getCondVisibility('system.platform.ios'):
        return 'ios'


def addDir(name,url,mode,iconimage,fanart,description):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="https://archive.org/download/Build_201801_201801/freshstart.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
        
       
        
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
        
                      
def killxbmc():
    choice = xbmcgui.Dialog().yesno('Fuerza el cierre de Kodi', 'Estas a punto de cerrar Kodi', 'Quieres continuar?', nolabel='No, Cancelar',yeslabel='Si, Cerrar')
    if choice == 0:
        return
    elif choice == 1:
        pass
    myplatform = platform()
    print "Platform: " + str(myplatform)
    if myplatform == 'osx': # OSX
        print "############   try osx force close  #################"
        try: os.system('killall -9 XBMC')
        except: pass
        try: os.system('killall -9 Kodi')
        except: pass
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "Si estas viendo este mensaje es porque el cierre forzado", "ha fallado. Por favor, fuerza el cierre de Kodi [COLOR=lime]NO USE[/COLOR] el menu para Salir.",'')
    elif myplatform == 'linux': #Linux
        print "############   try linux force close  #################"
        try: os.system('killall XBMC')
        except: pass
        try: os.system('killall Kodi')
        except: pass
        try: os.system('killall -9 xbmc.bin')
        except: pass
        try: os.system('killall -9 kodi.bin')
        except: pass
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "Si estas viendo este mensaje es porque el cierre forzado", "ha fallado. Por favor, fuerza el cierre de Kodi [COLOR=lime]NO USE[/COLOR] el menu de Kodi -Apagar- para cerrarlo.",'')
    elif myplatform == 'android': # Android  
        print "############   try android force close  #################"
        try: os.system('adb shell am force-stop org.xbmc.kodi')
        except: pass
        try: os.system('adb shell am force-stop org.kodi')
        except: pass
        try: os.system('adb shell am force-stop org.xbmc.xbmc')
        except: pass
        try: os.system('adb shell am force-stop org.xbmc')
        except: pass        
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "El cierre automatico ha fallado. Por favor, [COLOR=yellow]fuerza el cierre de Kodi[/COLOR]", "[COLOR=lime]NO USE[/COLOR] el menu de Kodi -Apagar- para cerrarlo.","Cierre manualmente, con el Administrador de tareas (si no esta seguro, desenchufe su dispositivo).")
    elif myplatform == 'windows': # Windows
        print "############   try windows force close  #################"
        try:
            os.system('@ECHO off')
            os.system('tskill XBMC.exe')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('tskill Kodi.exe')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im Kodi.exe /f')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im XBMC.exe /f')
        except: pass
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "El cierre automatico ha fallado. Por favor, fuerza el cierre de Kodi", "[COLOR=lime]NO USE[/COLOR] el menu de Kodi -Apagar- para cerrarlo.","Use el gestor de tareas y NO ALT F4")
    else: #ATV
        print "############   try atv force close  #################"
        try: os.system('killall AppleTV')
        except: pass
        print "############   try raspbmc force close  #################" #OSMC / Raspbmc
        try: os.system('sudo initctl stop kodi')
        except: pass
        try: os.system('sudo initctl stop xbmc')
        except: pass
        dialog.ok("[COLOR=red][B]Atencion  !!![/COLOR][/B]", "El cierre automatico ha fallado. Por favor, fuerza el cierre de Kodi", "[COLOR=lime]NO USE[/COLOR] el menu de Kodi -Apagar- para cerrarlo.","No se pudo detectar su Sistema, asi que desenchufe su dispositivo.")

def FRESHSTART(params):

    choice2 = xbmcgui.Dialog().yesno("Borrar todo el contenido?", '[COLOR=red]Estas seguro de borrar todo el contenido?[/COLOR]', 'Se borrara todo [B]menos[/B] el addon [COLOR=orange][B]WiZaRTiLa[/B][/COLOR] y tu [COLOR=lime][B]Videoteca[/B][/COLOR]', yeslabel='Si',nolabel='No')
    if choice2 == 0:
        return
    elif choice2 == 1:
        dp.create("Espere","FRESHSTART EN PROGRESO",'', 'Espere')
        try:
            for root, dirs, files in os.walk(HOME,topdown=True):
                dirs[:] = [d for d in dirs if d not in EXCLUDES]
                for name in files:
                    try:
                        os.remove(os.path.join(root,name))
                        os.rmdir(os.path.join(root,name))
                    except: pass
                        
                for name in dirs:
                    try: os.rmdir(os.path.join(root,name)); os.rmdir(root)
                    except: pass
        except: pass
    dialog.ok('Completado','Freshtart terminado, Fuerza el cierre de Kodi para aplicar los cambios.','','')
    killxbmc()					  
					  
					  
					  
					  
params=get_params()
url=None
name=None
mode=None
iconimage=None
fanart=None
description=None


try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:        
        mode=int(params["mode"])
except:
        pass
try:        
        fanart=urllib.unquote_plus(params["fanart"])
except:
        pass
try:        
        description=urllib.unquote_plus(params["description"])
except:
        pass
        
        
print str(PATH)+': '+str(VERSION)
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "IconImage: "+str(iconimage)


def setView(content, viewType):
    # set content type so library shows more views and info
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if ADDON.getSetting('auto-view')=='true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % ADDON.getSetting(viewType) )
        
        
if mode==None or url==None or len(url)<1:
        CATEGORIES()
       
elif mode==1:
        wizard(name,url,description)
		       
elif mode==6:        
	FRESHSTART(params)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))

