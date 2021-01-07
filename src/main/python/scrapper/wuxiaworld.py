import re
import sys
import json

from bs4 import BeautifulSoup

sys.path.append(".")
from scrapper.novelbase import Novelbase


class Wuxiaworld(Novelbase):

    _base_url = "https://www.wuxiaworld.com"

    def __init__(self):
        super(Wuxiaworld, self).__init__()

    @classmethod
    def getList(self):
        ret = []
        url = self._base_url + '/api/novels/search'

        options = {
            "post": '{"title":"","tags":[],"language":"Any","genres":[],"active":null,"sortType":"Name","sortAsc":true,"searchAfter":null,"count":100}',
            "Content-Type": "application/json",
        }
        page = self._get_web_page(url, "post", options)
        parsed = json.loads(page.content)

        for dt in parsed["items"]:
            new = {
                "title": dt["name"],
                "url": self._base_url + "/novel/" + dt["slug"],
                "image": dt["coverUrl"],
                "desc": dt["synopsis"],
            }
            ret.append(new)
        return ret

    @classmethod
    def getDetail(self, url):
        pass

    def parseChapterNo(title, last_chp=0):
        c = ""
        if "–" in title:
            n = title.split("–")[0]
            c = "".join([i for i in n if i.isdigit()])

        if "-" in title and not c.isdigit():
            n = title.split("-")[0]
            c = "".join([i for i in n if i.isdigit()])

        if ":" in title and not c.isdigit():
            n = title.split(":")[0]
            c = "".join([i for i in n if i.isdigit()])

        if not c.isdigit():
            c = "".join([i for i in title if i.isdigit()])

        # number is not in title, so just + 1 last number
        if not c.isdigit():
            # print(title)
            c = last_chp + 1
            # print(c)

        return c

    @classmethod
    def getChapters(self, url, soup=None):
        if soup is None:
            page = self._get_web_page(url)
            soup = BeautifulSoup(page.content, "html.parser")

        chapters = []

        panels = soup.select(
            "div.section div.novel-bottom div.novel-content div#chapters div.panel"
        )

        v = 1
        last_chp = -1
        for panel in panels:
            volume = panel.select_one(
                "div.panel-heading h4.panel-title span.title"
            ).getText().strip()

            if volume == "Table of Contents" or volume == "Chapters":
                volume = "Volume 1"

            for a in panel.select("div.panel-body li.chapter-item a"):
                title = a.getText().strip()
                href = a.get("href")

                c = self.parseChapterNo(title, last_chp)

                no = "v" + str(v) + "c" + str(c)
                chp = {
                    "no": no,
                    "title": title,
                    "url": self._base_url + href,
                    "volume": volume
                }
                chapters.append(chp)
                last_chp = int(c)
            v += 1

        return chapters

    @classmethod
    def getContent(self, url):
        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        content = soup.select_one(
            "div.main div#content-container div.section-content div.panel div#chapter-outer"
        )

        decompose_list = [
            "div#sidebar-toggler-container",
            "div.font-resize",
            "a.chapter-nav",
            "script",
            'div[id*="google"]',
        ]

        for decompose in decompose_list:
            for item in content.select(decompose):
                if item is not None:
                    item.decompose()

        return self.buildHTML(str(content))
