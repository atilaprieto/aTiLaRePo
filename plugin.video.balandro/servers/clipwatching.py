# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('http://', 'https://').replace('://www.', '://')

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    if "File Not Found" in data or "File was deleted" in data:
        return 'El archivo ya no está presente en el servidor'

    if 'sources: [' in data:
        matches = scrapertools.find_multiple_matches(data, 'src\s*:\s*"([^"]+)",.*?label\s*:\s*"([^"]+)"')
        if matches:
            # ~ for url, lbl in matches:
            for url, lbl in sorted(matches, key=lambda x: int(x[1])):
                if url.endswith('.srt'): continue
                video_urls.append([lbl, url])
            return video_urls
        else:
            matches = scrapertools.find_multiple_matches(data, '"([^"]+\.mp4)"')
            for url in matches:
                video_urls.append(['mp4', url])
            video_urls.reverse() # calidad increscendo

    try:
        packed = scrapertools.find_single_match(data, "text/javascript'>(.*?)\s*</script>")
        if packed:
            unpacked = jsunpack.unpack(packed)
            # ~ logger.debug(unpacked)
            videos = scrapertools.find_multiple_matches(unpacked, 'file:"([^"]+).*?label:"([^"]+)')
            for video, label in videos:
                if ".jpg" not in video:
                    video_urls.append([label, video])

            video_urls.sort(key=lambda it: int(it[0].replace('p','')))
    except:
        pass

    return video_urls
