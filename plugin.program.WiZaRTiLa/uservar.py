import os, xbmc, xbmcaddon

#########################################################
### Global Variables ####################################
#########################################################
PATH           = xbmcaddon.Addon().getAddonInfo('path')
ART            = os.path.join(PATH, 'resources', 'art')
#########################################################

#########################################################
### User Edit Variables #################################
#########################################################
ADDON_ID       = xbmcaddon.Addon().getAddonInfo('id')
ADDONTITLE     = 'WiZaRTiLa'
BUILDERNAME    = 'aTiLa'
EXCLUDES       = [ADDON_ID]
# Enable/Disable the text file caching with 'Yes' or 'No' and age being how often it rechecks in minutes
CACHETEXT      = 'Yes'
CACHEAGE       = 30
# Text File with build info in it.
BUILDFILE      = 'http://atilaprieto.myftp.org/compartidatila/Kodi/wizartila/autobuilds.txt'
# How often you would like it to check for build updates in days
# 0 being every startup of kodi
UPDATECHECK    = 0
# Text File with apk info in it.  Leave as 'http://' to ignore
APKFILE        = 'https://'
# Text File with Youtube Videos urls.  Leave as 'http://' to ignore
YOUTUBETITLE   = ''
YOUTUBEFILE    = ''
# Text File for addon installer.  Leave as 'http://' to ignore
ADDONFILE      = 'https://'
# Text File for advanced settings.  Leave as 'http://' to ignore
ADVANCEDFILE   = 'http://'
#########################################################

#########################################################
### Theming Menu Items ##################################
#########################################################

ICONBUILDS     = 'http://atilaprieto.myftp.org/compartidatila/Kodi/wizartila/icon.png'
ICONMAINT      = 'http://'
ICONAPK        = 'http://'
ICONADDONS     = 'http://'
ICONYOUTUBE    = 'http://'
ICONSAVE       = 'http://'
ICONCONTACT    = 'http://'
ICONSETTINGS   = 'http://'
ICONSPEED      = 'http://'
ICONTRAKT      = 'http://'
ICONREAL       = 'http://'
ICONLOGIN      = 'http://'
# Hide the ====== seperators 'Yes' or 'No'
HIDESPACERS    = 'No'
# Character used in seperator
SPACER         = '='

# You can edit these however you want, just make sure that you have a %s in each of the
# THEME's so it grabs the text from the menu item
COLOR1         = 'darkorange'
COLOR2         = 'white'
# Primary menu items   / %s is the menu item and is required
THEME1         = '[COLOR '+COLOR1+'][B][COLOR '+COLOR2+'][/COLOR][/B][/COLOR] [COLOR '+COLOR2+']%s[/COLOR]'
# Build Names          / %s is the menu item and is required
THEME2         = '[COLOR '+COLOR2+']%s[/COLOR]'
# Alternate items      / %s is the menu item and is required
THEME3         = '[COLOR '+COLOR1+']%s[/COLOR]'
# Current Build Header / %s is the menu item and is required
THEME4         = '[COLOR '+COLOR1+']Version WiZaRTiLa Instalada:[/COLOR] [COLOR '+COLOR2+']%s[/COLOR]'
# Current Theme Header / %s is the menu item and is required
THEME5         = '[COLOR '+COLOR1+']Current Theme:[/COLOR] [COLOR '+COLOR2+']%s[/COLOR]'
# Current Theme Header / %s is the menu item and is required
THEME6         = '[COLOR '+COLOR1+']Version WiZaRTiLa a instalar:[/COLOR] [COLOR '+COLOR2+']%s[/COLOR]'

# Message for Contact Page
# Enable 'Contact' menu item 'Yes' hide or 'No' dont hide
HIDECONTACT    = 'No'
# You can add \n to do line breaks
CONTACT        = 'Gracias por elegir WiZaRTiLa.'
#Images used for the contact window.  http:// for default icon and fanart
CONTACTICON    = 'http://atilaprieto.myftp.org/compartidatila/Kodi/wizartila/icon.png'
CONTACTFANART  = 'http://atilaprieto.myftp.org/compartidatila/Kodi/wizartila/fanart.jpg'
#########################################################

#########################################################
### Auto Update                   #######################
###        For Those With No Repo #######################
#########################################################
# Enable Auto Update 'Yes' or 'No'
AUTOUPDATE     = 'Yes'
# Url to wizard version
WIZARDFILE     = 'http://atilaprieto.myftp.org/compartidatila/Kodi/wizartila/autobuilds.txt'
#########################################################

#########################################################
### Auto Install                 ########################
###        Repo If Not Installed ########################
#########################################################
# Enable Auto Install 'Yes' or 'No'
AUTOINSTALL    = 'Yes'
# Addon ID for the repository
REPOID         = 'aTiLaRePo'
# Url to Addons.xml file in your repo folder(this is so we can get the latest version)
REPOADDONXML   = 'https://raw.githubusercontent.com/atilaprieto/aTiLaRePo/master/_repo/addons.xml'
# Url to folder zip is located in
REPOZIPURL     = 'https://raw.githubusercontent.com/atilaprieto/aTiLaRePo/master/_repo/aTiLaRePo/'
#########################################################

#########################################################
### Notification Window #################################
#########################################################
# Enable Notification screen Yes or No
ENABLE         = 'Yes'
# Url to notification file
NOTIFICATION   = 'http://atilaprieto.myftp.org/compartidatila/Kodi/wizartila/notify.txt'
# Use either 'Text' or 'Image'
HEADERTYPE     = 'Text'
HEADERMESSAGE  = 'WiZaRTiLa'
# Font size of header
FONTHEADER     = 'Font14'
# url to image if using Image 424x180
HEADERIMAGE    = 'http://'
# Font for Notification Window
FONTSETTINGS   = 'Font13'
# Background for Notification Window
BACKGROUND     = 'http://atilaprieto.myftp.org/compartidatila/Kodi/wizardtila/fanart.jpg'
#########################################################
