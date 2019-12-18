# -*- coding: utf-8 -*-

from libs.tools import *


def mainmenu(item):
    itemlist = list()

    itemlist.append(item.clone(
        label='Test 1',
        action='test1'
    ))


    itemlist.append(item.clone(
        label='Test Youtube',
        action='play',
        VideoPlayer='youtube',
        url='play/?video_id=FuS_bXJNync'
    ))

    '''
    itemlist.append(item.clone(
        label='Test 2',
        action='test2'
    ))
    
    etc...
    '''

    return itemlist


def test1(item):
    # aqui hacemos algo y devolvemos un listado de items
    # por ejemplo una lista de enlaces

    itemlist = []

    itemlist.append(item.clone(
        label='Enlace 1',
        action='play',
        VideoPlayer='f4mtester',
        url= 'http://142-169.sport365.tech:43911/ls/83b3cd2887b24534f455d7abacd5e73c326aa8a33e60b042e4b3de4aa2adf1b4d03d40ca9bfd17f63800cc3f079cbd1ee597257b67434743fb5376f633ac93f9/5df49b5d40e4f694265176/tqiin8u6v4hd8hg62vhj8ivua7/5df4fdd361a34/Z9tejMZCdCI4dC2rCVQhG5KAyhmQLXfl/i'    ))

    itemlist.append(item.clone(
        label='Enlace 2',
        action='play',
        VideoPlayer='f4mtester',
        url= 'http://142-169.sport365.tech:43911/ls/071b0b9673d71a4ddf3127f8c56cc7e2dee34a42bf2cfcc03c4c6bb99a9709894c3af46b6c68e044cc5674bd977bfc1750777a038ef8efba87078e3bb8a4c1c0/5df49dcff068e846608333/0gharu24286ehg45v0jtjqfr26/5df4fc9802ad4/ac0kN6V0nb45f7ZHHHotnNHRlZd7NUFn/i'
    ))

    itemlist.append(item.clone(
        label='Enlace 3',
        action='play',
        VideoPlayer='inputstream',
        url= 'http://142-169.sport365.tech:43911/ls/071b0b9673d71a4ddf3127f8c56cc7e2dee34a42bf2cfcc03c4c6bb99a9709894c3af46b6c68e044cc5674bd977bfc1750777a038ef8efba87078e3bb8a4c1c0/5df49dcff068e846608333/0gharu24286ehg45v0jtjqfr26/5df4fc9802ad4/ac0kN6V0nb45f7ZHHHotnNHRlZd7NUFn/i'    ))

    return itemlist


def play(item):
    # Esta funcion devolvera el diccionario con los datos necesarios para q se reproduzca el enlace, por ejemplo:

    video_item = {'action': 'play',
           'titulo': 'Titulo del video',
           'url': item.url,
           'VideoPlayer': item.VideoPlayer # Actualmente podria ser: Directo, plexus, InputStream, Streamlink o F4mtester
           # se pueden añadir los pares clave/valor q sea necesario segun el VideoPlayer escogido
    }

    return video_item