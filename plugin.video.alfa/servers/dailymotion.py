# -*- coding: utf-8 -*-

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    response = httptools.downloadpage(page_url)
    if "Contenido rechazado" in response.data:
        return False, "[Dailymotion] El archivo no existe o ha sido borrado"
    if response.code == 404:
        return False, "[Dailymotion] El archivo no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    response = httptools.downloadpage(page_url, cookies=False)
    cookie = {'Cookie': response.headers["set-cookie"]}
    data = response.data.replace("\\", "")
    subtitle = scrapertools.find_single_match(data, '"subtitles":.*?"es":.*?urls":\["([^"]+)"')
    qualities = scrapertools.find_multiple_matches(data, '"([^"]+)":(\[\{"type":".*?\}\])')
    for calidad, urls in qualities:
        patron = '"type":"(?:video|application)/([^"]+)","url":"([^"]+)"'
        matches = scrapertools.find_multiple_matches(urls, patron)
        for stream_type, stream_url in matches:
            stream_type = stream_type.replace('x-mpegURL', 'm3u8')
            if stream_type == "mp4":
                stream_url = httptools.downloadpage(stream_url, headers=cookie, only_headers=True,
                                                    follow_redirects=False).headers.get("location", stream_url)
            else:
                data_m3u8 = httptools.downloadpage(stream_url).data
                stream_url_http = scrapertools.find_single_match(data_m3u8, '(http:.*?\.m3u8)')
                if stream_url_http:
                    stream_url = stream_url_http
            video_urls.append(["%sp .%s [dailymotion]" % (calidad, stream_type), stream_url, 0, subtitle])
    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))
    return video_urls
