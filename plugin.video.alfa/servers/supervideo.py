# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from platformcode import logger
from lib import jsunpack
from bs4 import BeautifulSoup


def test_video_exists(page_url):
    global soup
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    soup = BeautifulSoup(data, "html5lib")
    if "File is no longer available as it expired or has been deleted" in data:
        return False, "[supervideo] El fichero ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    opts = soup.find("ul", class_="dropdown-menu downloadbox__dropdown-menu")
    matches = opts.find_all("li")

    for elem in matches:
        dl_url = eval(elem.a["onclick"])
        qlty = elem.a.span.text.split(",")[0].strip()
        dl_data = httptools.downloadpage(dl_url).data
        url = BeautifulSoup(dl_data, "html5lib").find("a", class_="btn_primary")["href"]
        video_urls.append(["%s [supervideo]" % qlty, url])

    return video_urls


def download_video(id, mode, hash):
    return "https://supervideo.tv/dl?op=download_orig&id=%s&mode=%s&hash=%s" % (id, mode, hash)