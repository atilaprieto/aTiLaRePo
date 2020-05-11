######################################################################################################################################################
##
## IGNORED
##
######################################################################################################################################################
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib2,urllib
import re
import uservar
from datetime import date, datetime, timedelta
from resources.libs import wizard as wiz

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addonid = addon.getAddonInfo('id')
dialog = xbmcgui.Dialog()
runupdate = xbmc.getInfoLabel('Skin.String(Startup.Favourites.Path)')
version = addon.getSetting('version')
update = xbmc.executebuiltin('runupdate')
if version < "1.0":	
	xbmc.executebuiltin(runupdate)