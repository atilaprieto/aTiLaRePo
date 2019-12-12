# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
import urllib


def get_video_url(page_url, url_referer=''):
    logger.info('page_url: %s'%page_url)
    video_urls = []
    urls = []
    streams =[]

    if 'googleusercontent' in page_url:

        response = httptools.downloadpage(page_url, follow_redirects = False, cookies=False, headers={"Referer": page_url})
        url=response.headers['location']
        if "set-cookie" in response.headers:
            try:
                cookies = ""
                cookie = response.headers["set-cookie"].split("HttpOnly, ")
                for c in cookie:
                    cookies += c.split(";", 1)[0] + "; "
                data = response.data.decode('unicode-escape')
                data = urllib.unquote_plus(urllib.unquote_plus(data))
                headers_string = "|Cookie=" + cookies
            except:
                headers_string = ""
        else:
            headers_string = ""

        quality = scrapertools.find_single_match (url, '.itag=(\d+).')

        streams.append((quality, url))

    else:
        response = httptools.downloadpage(page_url, cookies=False, headers={"Referer": page_url})
        if response.code == 429:
            return "Demasiadas conexiones al servidor, inténtelo después"
        if "no+existe" in response.data:
            return "El vídeo no existe o ha sido borrado"
        if "Se+ha+excedido+el" in response.data:
            return "Se ha excedido el número de reproducciones permitidas"
        if "No+tienes+permiso" in response.data:
            return "No tienes permiso para acceder a este vídeo"
        if "Se ha producido un error" in response.data:
            return "Se ha producido un error en el reproductor de google"
        if "No+se+puede+procesar+este" in response.data:
            return "No se puede procesar este vídeo"

        cookies = ""
        cookie = response.headers["set-cookie"].split("HttpOnly, ")
        for c in cookie:
            cookies += c.split(";", 1)[0] + "; "
        data = response.data.decode('unicode-escape')
        data = urllib.unquote_plus(urllib.unquote_plus(data))
        headers_string = "|Cookie=" + cookies
        url_streams = scrapertools.find_single_match(data, 'url_encoded_fmt_stream_map=(.*)')
        streams = scrapertools.find_multiple_matches(url_streams,
                                                     'itag=(\d+)&url=(.*?)(?:;.*?quality=.*?(?:,|&)|&quality=.*?(?:,|&))')

    itags = {'18': '360p', '22': '720p', '34': '360p', '35': '480p', '37': '1080p', '43': '360p', '59': '480p'}
    for itag, video_url in streams:
        if not video_url in urls:
            video_url += headers_string
            video_urls.append([itags[itag], video_url])
            urls.append(video_url)
        video_urls.sort(key=lambda video_urls: int(video_urls[0].replace("p", "")))

    return video_urls
