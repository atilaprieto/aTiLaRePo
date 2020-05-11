######################################################################################################################################################
##
## STARTUP SERVICE
##
######################################################################################################################################################

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib2,urllib
import re
import uservar
from datetime import date, datetime, timedelta
from resources.libs import wizard as wiz

xbmc.executebuiltin("UpdateLocalAddons")
xbmc.executebuiltin("UpdateAddonRepos")

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addonid = addon.getAddonInfo('id')
dialog = xbmcgui.Dialog()
runupdate = xbmc.getInfoLabel('Skin.String(Startup.Favourites.Path)')
version = addon.getSetting('version')
update = xbmc.executebuiltin('runupdate')
if version < "1.0":	
	xbmc.executebuiltin(runupdate)
	
 
__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
 
line1 = "[COLOR yellow]Nuevo parche WiZaRTiLa[/COLOR]"
time = 10000 #in miliseconds
 
xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))





