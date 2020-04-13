# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    headers = {}
    if url_referer: headers['Referer'] = url_referer

    if '/embed/' not in page_url:
        page_url = page_url.replace('dailymotion.com/video/', 'dailymotion.com/embed/video/')

    resp = httptools.downloadpage(page_url, headers=headers, cookies=False)
    # ~ logger.debug(resp.data)

    if resp.code == 404:
        return 'El archivo no existe o ha sido borrado'

    cookie = {'Cookie': resp.headers["set-cookie"]}
    data = resp.data.replace("\\", "")
    subtitle = scrapertools.find_single_match(data, '"subtitles":.*?"es":.*?urls":\["([^"]+)"')
    qualities = scrapertools.find_multiple_matches(data, '"([^"]+)":(\[\{"type":".*?\}\])')

    for calidad, urls in qualities:
        patron = '"type":"(?:video|application)/([^"]+)","url":"([^"]+)"'
        matches = scrapertools.find_multiple_matches(urls, patron)
        for stream_type, stream_url in matches:
            stream_type = stream_type.replace('x-mpegURL', 'm3u8')
            if stream_type == "mp4":
                stream_url = httptools.downloadpage(stream_url, headers=cookie, only_headers=True, follow_redirects=False).headers.get("location", stream_url)
                if stream_url:
                    video_urls.append(["%sp .%s" % (calidad, stream_type), stream_url, 0, subtitle])
            else:
                data = httptools.downloadpage(stream_url).data
                # ~ logger.debug(data)

                matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+).*?\n(http[^\s]+)')
                if matches:
                    for res, url in sorted(matches, key=lambda x: int(x[0])):
                        if res+'p' in [x[0] for x in video_urls]: continue
                        video_urls.append([res+'p', url, 0, subtitle])

    return video_urls
