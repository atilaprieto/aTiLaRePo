# -*- coding: utf-8 -*-

from libs.tools import *


def main(item):
    itemlist = list()
    try:
        url = 'plugin://script.module.TvTap/list_channels/5'
        command = '{"jsonrpc":"2.0", "method":"Files.GetDirectory", "params":{"directory":"%s","media":"video","properties":["thumbnail"]}, "id":1}' % url
        data = load_json(xbmc.executeJSONRPC(command))
        canales = data['result']['files']

        if get_setting('tap_sort'):
            canales.sort(key=lambda e: e['label'])

        for i in canales:
            if i['filetype'] == 'file':
                pais, name = i['label'].split(' - ')
                itemlist.append(item.clone(
                    label=name + (" (%s)" % pais if pais != 'OTH' else ''),
                    url=i['file'],
                    isPlayable=True,
                    icon= i['thumbnail'],
                    action='play'
                ))

    except:
        xbmcgui.Dialog().ok('1x2',
                            'Ups!  Parece que en estos momentos no hay eventos programados.',
                            'Intentelo mas tarde, por favor.')

    return itemlist
