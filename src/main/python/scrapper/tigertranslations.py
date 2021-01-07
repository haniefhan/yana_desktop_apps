import re
import sys

from bs4 import BeautifulSoup

sys.path.append(".")
from scrapper.novelbase import Novelbase


class Tigertranslations(Novelbase):

    _base_url = "https://tigertranslations.org/"

    def __init__(self):
        super(Tigertranslations, self).__init__()

    @classmethod
    def getList(self):
        ret = []
        url = self._base_url

        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        novel_list = soup.select(
            "div.site-container header.masthead nav ul#nav li a"
        )

        for novel in novel_list:
            href = novel.get("href")
            title = novel.getText()

            detail = self.getDetail(href)

            new = {
                "title": detail["title"],
                "url": href,
                "image": detail["image"],
                "author": detail["author"],
            }
            ret.append(new)
            # break

        return ret

    @classmethod
    def getDetail(self, url):
        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.select_one(
            "div.main-content article header.entry-header h1"
        ).getText()

        img = soup.select_one(
            "div.main-content article section.entry div.the-content img"
        ).get("src")

        image = img.split('?')[0]

        tags = soup.select_one(
            "div.main-content article section.entry div.the-content"
        ).findAll(["p"])

        author = ""
        for tag in tags:
            if title in tag.getText():
                title = tag.getText().strip()
            elif "Author" in tag.getText():
                author = tag.getText().replace("Author:", "").strip()

        detail = {
            "title": title,
            "image": image,
            "author": author,
        }

        return detail

    @classmethod
    def getChapters(self, url, soup=None):
        if soup is None:
            page = self._get_web_page(url)
            soup = BeautifulSoup(page.content, "html.parser")

        chapters = []

        ass = soup.select(
            "div.main-content article section.entry div.the-content p a")
        for a in ass:
            if a.get("href") is not None:
                if self._base_url in a.get("href"):
                    title = a.getText().strip()

                    c = "".join([i for i in title if i.isdigit()])
                    no = "v1c" + c

                    chp = {
                        "no": no,
                        "title": title,
                        "url": a.get("href"),
                        "volume": "Volume 1",
                    }
                    chapters.append(chp)
        return chapters

    @classmethod
    def getContent(self, url):
        content_page_1 = ""
        content_page_2 = ""

        img_attr = [
            "data-lazy-sizes", "data-lazy-src", "data-lazy-srcset", "class",
            "srcset", "loading", "height", "sizes"
        ]

        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        decompose_list = [
            "script",
            "div.main-content article section.entry div.the-content p.taxonomies",
            "div.main-content article section.entry div.the-content div.sharedaddy",
        ]

        for decompose in decompose_list:
            for item in soup.select(decompose):
                if item is not None:
                    item.decompose()

        content = soup.select_one(
            "div.main-content article section.entry div.the-content"
        )

        page_2 = ""
        for a in content.findAll("a"):
            if "PAGE 2" in a.getText():
                page_2 = a.get("href")
                a.decompose()
            else:
                for attr in ["href"]:
                    if a.get(attr) is not None:
                        del(a[attr])

        for img in content.findAll("img"):
            for attr in img_attr:
                if img.get(attr) is not None:
                    del(img[attr])
            img['width'] = "100%"

        content_page_1 = content

        if page_2 != "":
            page = self._get_web_page(page_2)
            soup = BeautifulSoup(page.content, "html.parser")

            for decompose in decompose_list:
                for item in soup.select(decompose):
                    if item is not None:
                        item.decompose()

            content = soup.select_one(
                "div.main-content article section.entry div.the-content"
            )

            for a in content.findAll("a"):
                if "PAGE 1" in a.getText():
                    a.decompose()
                else:
                    for attr in ["href"]:
                        if a.get(attr) is not None:
                            del(a[attr])

            for img in content.findAll("img"):
                for attr in img_attr:
                    if img.get(attr) is not None:
                        del(img[attr])
                img['width'] = "100%"

            content_page_2 = content

        ret = str(content_page_1)
        ret += "<br/><b>End Of Page 1</b><br/>"
        ret += "<hr/>"
        ret += "<br/><b>Page 2</b><br/>"
        ret += str(content_page_2)

        return self.buildHTML(ret)
