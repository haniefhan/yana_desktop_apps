import requests
import re
import sys

from bs4 import BeautifulSoup

sys.path.append(".")
from scrapper.novelbase import Novelbase


class Graverobber(Novelbase):

    _base_url = "https://graverobbertl.site/"

    def __init__(self):
        super(Graverobber, self).__init__()

    @classmethod
    def getList(self):
        ret = []
        url = self._base_url

        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        query_list = [
            "div.container nav.navbar ul#menu-primary li#menu-item-10 a",
            "div.container nav.navbar ul#menu-primary li#menu-item-803 a",
            "div.container nav.navbar ul#menu-primary li#menu-item-2122 a",
        ]

        for query in query_list:
            novel = soup.select_one(query)

            href = novel.get("href")
            # title = novel.getText()

            detail = self.getDetail(href)

            new = {
                "title": detail["title"],
                "url": href,
                "image": detail["image"],
                "author": detail["author"],
                "url_original": detail["url_original"],
            }
            ret.append(new)
            # break

        return ret

    @classmethod
    def getDetail(self, url):
        image = ""
        author = ""
        raw = ""

        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.select_one(
            "section.content-area article div.post-header h1.entry-title"
        ).getText()

        img = soup.select_one(
            "section.content-area article div.post-entry img"
        )
        if img is not None:
            image = img.get("src")

        query = soup.select_one(
            "section.content-area article div.post-entry"
        ).findAll("p")

        for tag in query:
            if "Table of content" in tag.getText():
                break

            if tag.name == "p":
                if "Author:" in tag.getText():
                    author = tag.getText().replace("Author:", "").strip()
                elif "Raw" in tag.getText() or "RAW" in tag.getText():
                    raw = tag.select_one("a").get("href")

        return {
            "title": title,
            "image": image,
            "author": author,
            "url_original": raw,
        }

    @classmethod
    def getChapters(self, url, soup=None):
        if soup is None:
            page = self._get_web_page(url)
            soup = BeautifulSoup(page.content, "html.parser")

        chapters = []

        query = soup.select_one(
            "section.content-area article div.post-entry"
        ).findAll(["ul", "p", "h2"])

        toc = False
        volume = "Arc 0"
        for tag in query:
            if toc is False and (
                "Table of content" in tag.getText()
                or "Table of Content" in tag.getText()
            ):
                toc = True
                continue
            elif toc is False and "Chapter" in tag.getText():
                toc = True
                volume = "Arc 1"

            if toc is True:
                if tag.name == "p":
                    if tag.find('strong') is not None:
                        volume = tag.find('strong').getText().strip()
                elif tag.name == "ul":
                    for a in tag.select("li a"):
                        url = a.get("href")
                        if self._base_url in url:
                            title = a.parent.getText()
                            v = "".join([i for i in volume if i.isdigit()])
                            if "Illustration" in title:
                                if len(c) > 0:
                                    c = str(int(c) + 1)
                                else:
                                    c = "0"
                            else:
                                c = "".join([i for i in title if i.isdigit()])

                            no = "v" + v + "c" + c
                            chp = {
                                "no": no,
                                "title": title,
                                "url": url,
                                "volume": volume,
                            }

                            chapters.append(chp)
        return chapters

    addStyleSheet = """
    <style>
        body{
            font-family: Arial;
            font-size: 11pt;
            padding: 20px;
            line-height: 25px;
        }
    </style>"""

    @classmethod
    def buildHTML(self, body):
        return """
        <html>
            <head>
            """ + self.addStyleSheet + """
            </head>
            <body>
            """ + body + """
            </body>
        </html>
        """

    @classmethod
    def getContent(self, url):
        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        decompose_list = [
            "script",
            "div#content div#primary main#main article div.post-entry div.wp-block-columns",
        ]

        for decompose in decompose_list:
            item = soup.select_one(decompose)
            if item is not None:
                item.decompose()

        content = soup.select_one(
            "div#content div#primary main#main article div.post-entry"
        )

        img_attr = [
            "data-lazy-sizes", "data-lazy-src", "data-lazy-srcset", "class",
            "srcset", "loading", "height", "sizes"
        ]

        for img in content.findAll("img"):
            for attr in img_attr:
                if img.get(attr) is not None:
                    del(img[attr])
            img['width'] = "100%"

        return self.buildHTML(str(content))
