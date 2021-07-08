# -*- coding: utf-8 -*-

from platformcode import logger, config, platformtools
from core.item import Item


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis  = config.get_setting('notification_avis_color', default='yellow')
color_exec  = config.get_setting('notification_exec_color', default='cyan')


def _marcar_canal(item):
    config.set_setting('status', item.estado, item.from_channel)
    platformtools.itemlist_refresh()

def _refresh_menu(item):
    platformtools.dialog_notification(config.__addon_name, 'Refrescando [B][COLOR %s]caché Menú[/COLOR][/B]' % color_exec)
    platformtools.itemlist_refresh()

def _dominios(item):
    logger.info()

    if item.from_channel == 'hdfull':
        from channels import hdfull
        item.channel = 'hdfull'
        hdfull.configurar_dominio(item)

def _proxies(item):
    logger.info()

    if item.from_channel == 'cinetux':
        from channels import cinetux
        item.channel = 'cinetux'
        cinetux.configurar_proxies(item)

    elif item.from_channel == 'cliver':
        from channels import cliver
        item.channel = 'cliver'
        cliver.configurar_proxies(item)

    elif item.from_channel == 'cliversite':
        from channels import cliversite
        item.channel = 'cliversite'
        cliversite.configurar_proxies(item)

    elif item.from_channel == 'cuevana3':
        from channels import cuevana3
        item.channel = 'cuevana3'
        cuevana3.configurar_proxies(item)

    elif item.from_channel == 'cuevana3video':
        from channels import cuevana3video
        item.channel = 'cuevana3video'
        cuevana3video.configurar_proxies(item)

    elif item.from_channel == 'dilo':
        from channels import dilo
        item.channel = 'dilo'
        dilo.configurar_proxies(item)

    elif item.from_channel == 'documaniatv':
        from channels import documaniatv
        item.channel = 'documaniatv'
        documaniatv.configurar_proxies(item)

    elif item.from_channel == 'dontorrents':
        from channels import dontorrents
        item.channel = 'dontorrents'
        dontorrents.configurar_proxies(item)

    elif item.from_channel == 'gnula':
        from channels import gnula
        item.channel = 'gnula'
        gnula.configurar_proxies(item)

    elif item.from_channel == 'grantorrent':
        from channels import grantorrent
        item.channel = 'grantorrent'
        grantorrent.configurar_proxies(item)

    elif item.from_channel == 'hdfull':
        from channels import hdfull
        item.channel = 'hdfull'
        hdfull.configurar_proxies(item)

    elif item.from_channel == 'mejortorrents':
        from channels import mejortorrents
        item.channel = 'mejortorrents'
        mejortorrents.configurar_proxies(item)

    elif item.from_channel == 'newpct1':
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Configurar proxies desde el canal[/COLOR][/B]' % color_avis)

    elif item.from_channel == 'pctfenix':
        from channels import pctfenix
        item.channel = 'pctfenix'
        pctfenix.configurar_proxies(item)

    elif item.from_channel == 'pelisplay':
        from channels import pelisplay
        item.channel = 'pelisplay'
        pelisplay.configurar_proxies(item)

    elif item.from_channel == 'pelisvips':
        from channels import pelisvips
        item.channel = 'pelisvips'
        pelisvips.configurar_proxies(item)

    elif item.from_channel == 'playview':
        from channels import playview
        item.channel = 'playview'
        playview.configurar_proxies(item)

    elif item.from_channel == 'repelis':
        from channels import repelis
        item.channel = 'repelis'
        repelis.configurar_proxies(item)

    elif item.from_channel == 'subtorrents':
        from channels import subtorrents
        item.channel = 'subtorrents'
        subtorrents.configurar_proxies(item)

    elif item.from_channel == 'torrentdivx':
        from channels import torrentdivx
        item.channel = 'torrentdivx'
        torrentdivx.configurar_proxies(item)

def _quitar_proxies(item):
    el_canal = ('Quitando proxies [B][COLOR %s]' + item.from_channel.capitalize() + '[/COLOR][/B]') % color_avis
    platformtools.dialog_notification(config.__addon_name, el_canal)

    config.set_setting('proxies', '', item.from_channel)
    platformtools.itemlist_refresh()

