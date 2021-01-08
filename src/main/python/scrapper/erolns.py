import re
import sys

from bs4 import BeautifulSoup

sys.path.append(".")
from scrapper.novelbase import Novelbase


class Erolns(Novelbase):

    _base_url = "http://erolns.blogspot.com/"
    _base_url_https = "https://erolns.blogspot.com/"

    def __init__(self):
        super(Erolns, self).__init__()

    @classmethod
    def getList(self):
        ret = []
        url = self._base_url + "2015/11/projects.html"

        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        novel_list = soup.select(
            "div.post-outer div.post h3 a"
        )

        for novel in novel_list:
            href = novel.get("href")
            title = novel.getText()

            detail = self.getDetail(href)

            new = {
                "title": title,
                "url": href,
                "image": detail["image"],
                "author": detail["author"],
                "artist": detail["artist"],
            }
            ret.append(new)

        return ret

    @classmethod
    def getDetail(self, url):
        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        image = soup.select_one(
            "div.post-outer div.post div.post-body a img").get("src")

        brs = soup.select("div.post-outer div.post div.post-body br")

        author = ""
        artist = ""
        for br in brs:
            if br.next_sibling is not None:
                if "Author" in br.next_sibling:
                    author = br.next_sibling.replace("Author:", "").strip()
                elif "Illustrator" in br.next_sibling:
                    artist = br.next_sibling.replace("Illustrator:", "").strip()

        detail = {
            "image": image,
            "author": author,
            "artist": artist,
        }

        return detail

    @classmethod
    def getChapters(self, url, soup=None):
        if soup is None:
            page = self._get_web_page(url)
            soup = BeautifulSoup(page.content, "html.parser")

        chapters = []

        ass = soup.select("div.post-outer div.post div.post-body a")
        no = 1
        for a in ass:
            if a.get("href") is not None:
                if self._base_url in a.get("href") or self._base_url_https in a.get("href"):
                    chp = {
                        "no": no,
                        "title": a.getText().strip(),
                        "url": a.get("href"),
                        "volume": "Volume 1",
                    }
                    chapters.append(chp)
                    no += 1
        return chapters

    styleSheet = """
    <style>
        body{font-family: Arial; font-size: 11pt; padding: 20px;}
        div{line-height: 25px;}
    </style>"""

    @classmethod
    def getContent(self, url):
        page = self._get_web_page(url)
        soup = BeautifulSoup(page.content, "html.parser")

        decompose_list = [
            "div.content div.main.section div.blog-posts div.post div.post-footer",
        ]

        for decompose in decompose_list:
            item = soup.select_one(decompose)
            if item is not None:
                item.decompose()

        content = soup.select_one(
            "div.content div.main.section div.blog-posts div.post"
        )

        img_attr = [
            "border", "height", "width"
        ]

        for img in content.findAll("img"):
            for attr in img_attr:
                if img.get(attr) is not None:
                    del(img[attr])
            img['width'] = "100%"

        for a in content.findAll("a"):
            del(a["href"])
            if a.get("style") is not None:
                del(a["style"])

        return self.buildHTML(str(content))
