#------------------------------------------------------------
# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta 4
# Copyright 2015 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
#------------------------------------------------------------
# This file is part of tvalacarta 4.
#
# tvalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tvalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tvalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------
# Channel for api listings
#------------------------------------------------------------
import urlparse,re
import urllib
import datetime
import time

from core import api
from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import suscription

DEBUG = config.get_setting("debug")
CHANNELNAME = "api_programas"

#------------------------------------------------------------
# Navigation
#------------------------------------------------------------

def mainlist(item):
    logger.info("tvalacarta.channels.api_programas mainlist")
    return api.navigation_get_programs_menu(item)

def programas(item):
    logger.info("tvalacarta.channels.api_programas programas")
    return api.navigation_get_programs_menu_by_section(item,"programas")

def infantil(item):
    logger.info("tvalacarta.channels.api_programas infantil")
    return api.navigation_get_programs_menu_by_section(item,"infantil")

def series(item):
    logger.info("tvalacarta.channels.api_programas series")
    return api.navigation_get_programs_menu_by_section(item,"series")

def cine(item):
    logger.info("tvalacarta.channels.api_programas cine")
    return api.navigation_get_programs_menu_by_section(item,"cine")

def informativos(item):
    logger.info("tvalacarta.channels.api_programas informativos")
    return api.navigation_get_programs_menu_by_section(item,"informativos")

def deportes(item):
    logger.info("tvalacarta.channels.api_programas deportes")
    return api.navigation_get_programs_menu_by_section(item,"deportes")

def get_items(item):
    logger.info("tvalacarta.channels.api_programas get_items")
    return api.get_items(item)

def search(item,tecleado):
    logger.info("tvalacarta.channels.api_programas search")
    item.url = item.url + urllib.quote_plus(tecleado)
    return api.get_items(item)

def play(item):
    logger.info("tvalacarta.channels.api_programas play item="+item.tostring())

    api.mark_as_watched(item,really_watched=True)


    exec "from channels import "+item.channel_id+" as channelmodule"
    if hasattr(channelmodule, 'play'):
        play_items = channelmodule.play(item)
    else:
        item.server = item.channel_id
        play_items = [item]

    valid_url = False
    for play_item in play_items:
        if play_item.server=="directo" and play_item.url.startswith("http"):
            valid_url = True
        if play_item.server<>"directo" and play_item.url!="":
            valid_url = True

    if not valid_url:
        response = api.videos_get_media_url(item)
        play_items = [Item(channel=item.channel, server="directo", url=response["body"])]

    return play_items

# Por compatibilidad con versiones anteriores
def videos_get_by_program(item):
    return get_items(item)

def other_videos_same_program(item):
    logger.info("tvalacarta.channels.api_programas other_videos_same_program item="+item.tostring())

    return other_videos_same_program(item)

#------------------------------------------------------------
# Context menu
#------------------------------------------------------------

def get_context_menu_for_item(item):

    context_commands = []

    if item.item_type == "video":

        if item.watched=="false":
            context_commands.append( item.clone(command_title="Marcar vídeo como visto", action="mark_as_watched") )
        else:
            context_commands.append( item.clone(command_title="Marcar vídeo como no visto", action="mark_as_unwatched") )

        #context_commands.append( item.clone(command_title="Ver otros vídeos de '"+item.show_title+"'", action="other_videos_same_program") )
        
        # Ver mas tarde

        # Añadir / quitar programa XXX de favoritos
        if item.is_favorite_show=="true":
            context_commands.append( item.clone(command_title="Quitar programa '"+item.show_title+"' de favoritos", action="remove_from_favorites") )
        else:
            context_commands.append( item.clone(command_title="Añadir programa '"+item.show_title+"' a favoritos", action="add_to_favorites") )

        # Ocultar programa
        context_commands.append( item.clone(command_title="Ocultar programa '"+item.show_title+"'", action="add_to_hidden") )

    elif item.item_type == "program":

        if item.is_favorite=="true":
            context_commands.append( item.clone(command_title="Quitar programa '"+item.show_title+"' de favoritos", action="remove_from_favorites") )
        else:
            context_commands.append( item.clone(command_title="Añadir programa '"+item.show_title+"' a favoritos", action="add_to_favorites") )

        if item.is_hidden=="true":
            context_commands.append( item.clone(command_title="Dejar de ocultar programa '"+item.show_title+"'", action="remove_from_hidden") )
        else:
            context_commands.append( item.clone(command_title="Ocultar programa '"+item.show_title+"'", action="add_to_hidden") )

        if not suscription.already_suscribed(item):
            context_commands.append( item.clone(command_title="Activar descarga automática", action="subscribe_to_program") )
        else:
            context_commands.append( item.clone(command_title="Cancelar descarga automática", action="unsubscribe_to_program") )

        context_commands.append( item.clone(command_title="Descargar ahora todos los vídeos", action="download_all_videos") )

    return context_commands

def add_to_favorites(item):
    logger.info("tvalacarta.channels.api_programas add_to_favorites item="+repr(item))

    api.add_to_favorites(item)
    
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def remove_from_favorites(item):
    logger.info("tvalacarta.channels.api_programas remove_from_favorites item="+repr(item))

    api.remove_from_favorites(item)
    
    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def add_to_hidden(item):
    logger.info("tvalacarta.channels.api_programas add_to_hidden item="+repr(item))

    api.add_to_hidden(item)

    if config.is_xbmc():
        import xbmcgui
        xbmcgui.Dialog().ok( "Programa ocultado" , "Ya no verás este programa ni sus vídeos, puedes volver a mostrarlo desde el menú de configuración.")

        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def remove_from_hidden(item):
    logger.info("tvalacarta.channels.api_programas remove_from_hidden item="+repr(item))
    
    api.remove_from_hidden(item)

    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def mark_as_watched(item):
    logger.info("tvalacarta.channels.api_programas mark_as_watched item="+repr(item))
    
    api.mark_as_watched(item,really_watched=False)

    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def mark_as_unwatched(item):
    logger.info("tvalacarta.channels.api_programas mark_as_unwatched item="+repr(item))
    
    api.mark_as_unwatched(item)

    if config.is_xbmc():
        import xbmc
        xbmc.executebuiltin("XBMC.Container.Refresh()");

def subscribe_to_program(item):
    logger.info("tvalacarta.channels.api_programas subscribe_to_program item="+repr(item))
    
    item.action="get_items"
    
    if not suscription.already_suscribed(item):
        suscription.append_suscription(item)

        if config.is_xbmc():
            import xbmcgui
            xbmcgui.Dialog().ok( "Descarga automática activada" , "A partir de ahora los nuevos vídeos que se publiquen de este programa se descargarán automáticamente, podrás encontrarlos en la sección 'Descargas'.")

            import xbmc
            xbmc.executebuiltin("XBMC.Container.Refresh()");

def unsubscribe_to_program(item):
    logger.info("tvalacarta.channels.api_programas subscribe_to_program item="+repr(item))

    if suscription.already_suscribed(item):
        suscription.remove_suscription(item)

        if config.is_xbmc():
            import xbmcgui
            xbmcgui.Dialog().ok( "Descarga automática cancelada" , "Los vídeos que hayas descargado se mantienen, pero los nuevos ya no se descargarán ellos solos.")

            import xbmc
            xbmc.executebuiltin("XBMC.Container.Refresh()");

def download_all_videos(item):
    logger.info("tvalacarta.channels.api_programas download_all_videos item="+repr(item))

    item.action="get_items"

    from core import downloadtools
    downloadtools.download_all_episodes(item)

def get_hidden_programs(item):
    logger.info("tvalacarta.channels.api_programas get_hidden_programs")

    return api.get_hidden_programs(item)

def get_favorite_programs(item):
    logger.info("tvalacarta.channels.api_programas get_favorite_programs")

    return api.get_favorite_programs(item)
