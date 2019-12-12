# -*- coding: utf-8 -*-

from libs.tools import *


def read(item):
    itemlist = list()

    try:
        data = httptools.downloadpage(item.url).data
        for it in re.findall('<item>(.*?)</item>',data,re.S):
            url = None
            action = 'main'

            if re.findall('<externallink>(.*?)</externallink>',it):
                url = re.findall('<externallink>(.*?)</externallink>',it)[0]
            elif re.findall('<jsonrpc>(.*?)</jsonrpc>',it):
                url = re.findall('<jsonrpc>(.*?)</jsonrpc>', it)[0]
                if 'plugin://plugin.video.youtube/play/' in url:
                    action='play'
            elif re.findall('<link>(.*?)</link>',it):
                url = re.findall('<link>(.*?)</link>', it)[0]
                action = 'play'

            playlist = True
            if re.findall('<playlist>(.*?)</playlist>', it):
                playlist = True if re.findall('<playlist>(.*?)</playlist>', it)[0].lower() in ['true','1','si'] else False

            search = False
            if re.findall('<search>(.*?)</search>',it):
                search = True if re.findall('<search>(.*?)</search>',it)[0].lower() in ['true', '1', 'si'] else False

            live = False
            if re.findall('<live>(.*?)</live>', it):
                live = True if re.findall('<live>(.*?)</live>',it)[0].lower() in ['true', '1', 'si'] else False

            if url:
                icon = re.findall('<thumbnail>(.*?)</thumbnail>', it)
                itemlist.append(item.clone(
                    label= re.findall('<title>(.*?)</title>', it)[0],
                    action= action,
                    isPlayable=True if action == 'play' else False,
                    url= url,
                    icon= icon[0] if icon else item.icon,
                    search=search,
                    live=live,
                    playlist=playlist
                ))

    except:
        pass

    return itemlist


def main(item):
    #logger(item)
    if 'https://pastebin.com' in item.url:
        return read(item)

    elif 'plugin://plugin.video.youtube/' in item.url:
        command = '{"jsonrpc":"2.0", "method":"Files.GetDirectory", "params":{"directory":"%s","media":"video"}, "id":1}' % item.url
        data =  load_json(xbmc.executeJSONRPC(command))
        itemlist = list()

        if data and data.get('result'):
            for n, i in enumerate(data.get('result').get('files',[])):
                if (n == 0 and i['file'].endswith('/playlists/') and not item.playlist) or \
                        (n == 1 and '/kodion/search/' in i['file'] and not item.search) or \
                        (n == 2 and i['file'].endswith('/live/') and not item.live):
                    continue

                itemlist.append(item.clone(
                    label=i['label'],
                    action='play' if 'plugin://plugin.video.youtube/play/' in i['file'] else 'main',
                    isPlayable=True if 'plugin://plugin.video.youtube/play/' in i['file'] else False,
                    url=i['file'],
                    isFolder= True if i['filetype'] == 'directory' else False
                ))

        return itemlist

    else:
        return {'action': 'play',
               'url': item.url,
               'titulo': item.label,
               'VideoPlayer': 'f4mtester'}
