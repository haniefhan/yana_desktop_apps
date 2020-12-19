import requests
import re

from bs4 import BeautifulSoup


class Stabbingwithasyringe():

    _base_url = "https://stabbingwithasyringe.home.blog/"

    def __init__(self):
        super(Stabbingwithasyringe, self).__init__()

    # def sourceQuery():
    #     return """
    #         INSERT INTO source (
    #             src_name,
    #             src_scrapper_name,
    #             src_base_url
    #         ) VALUES (
    #             'Stabbing With Syringe',
    #             'stabbingwithasyringe',
    #             'https://stabbingwithasyringe.home.blog/'
    #         );"""

    @classmethod
    def getList(self):
        ret = []
        url = self._base_url

        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        novel_list = soup.select(
            "ul#menu-main li#menu-item-2550 ul.sub-menu li"
        )

        for novel in novel_list:
            href = novel.select_one("a").get("href")
            # title = novel.select_one("a").contents[0]
            title = novel.select_one("a").getText()

            detail = self.getDetail(href)

            new = {
                "title": title,
                "url": href,
                "image": detail["image"],
                # "image_original": detail["image"],
                "author": detail["author"],
                "url_original": detail["url_original"],
                # "chapters": detail["chapters"],
            }
            ret.append(new)

        return ret

    @classmethod
    def getDetail(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        image = soup.select_one(
            "div.wp-block-image figure img").get("data-orig-file")

        for p in soup.select("div.entry-content p"):
            if p.find(text=re.compile("Author")):
                author = p.getText().replace("Author: ", "")
            elif p.find(text=re.compile("riginal webnovel link")):
                url_original = p.find("a").get("href")

        detail = {
            "image": image,
            "author": author,
            "url_original": url_original,
            # "chapters": self.getChapters(url, soup),
        }

        return detail

    @classmethod
    def getChapters(self, url, soup=None):
        if soup is None:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

        chapters = []
        # no = 1
        last_volume = "0"
        for h3 in soup.select("div.entry-content h3"):
            if h3.get("class") is None:
                volume = h3.getText().replace("(Full Text)", "").strip()
                p = h3.findNext("p")

                for a in p.find_all("a"):
                    title = a.getText().strip()

                    if volume in [
                        "Afterstories", "Final Volume", "Omake (Extra) 1",
                        "Omake (Extra) 2", "Epilogue"
                    ]:
                        lv = int(
                            "".join([i for i in last_volume if i.isdigit()])
                        ) + 1
                        volume = "Volume " + str(lv) + " – " + volume
                        v = str(lv)
                    else:
                        v = "".join([i for i in volume if i.isdigit()])

                    c = ""
                    if "–" in title:
                        cp = title.split("–")
                        c = "".join([i for i in cp[0] if i.isdigit()])
                    elif ":" in title:
                        cp = title.split(":")
                        c = "".join([i for i in cp[0] if i.isdigit()])
                    else:
                        c = "".join([i for i in title if i.isdigit()])

                    if v == "":
                        v = "0"
                    if c == "":
                        c = "0"

                    prefix_chapter = "c"
                    if "Prologue" in title:
                        prefix_chapter = "b"

                    no = "v" + v + prefix_chapter + c

                    if title != '':
                        chp = {
                            "no": no,
                            "title": title,
                            "url": a.get("href"),
                            "volume": volume,
                        }
                        chapters.append(chp)
                        # no += 1
                last_volume = volume
        return chapters

    addStyleSheet = """
    <style>
        body{font-family: Arial; font-size: 11pt;}
        h3{font-size: 1.5625rem; margin: 20px;}
        p{margin: 10px 20px; line-height: 25px;}
    </style>"""

    @classmethod
    def buildHTML(self, body):
        return """
        <html>
            <head>
            """ + self.addStyleSheet + """
            </head>
            <body style="padding: 50px;">
            """ + body + """
            </body>
        </html>
        """

    @classmethod
    def getContent(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        decompose_list = [
            "div#content section.content-area div#comments",
            "div#content section.content-area p.has-text-align-center",
            "div#content section.content-area script",
            "div#content section.content-area div#jp-post-flair",
            "div#content section.content-area div.wpcnt",
            "div#content section.content-area div.entry-content div.wpcnt",
        ]

        for decompose in decompose_list:
            items = soup.select(decompose)
            for item in items:
                if item is not None:
                    item.decompose()

        for h6 in soup.select("div#content section.content-area h6"):
            h6.decompose()

        content = soup.select_one(
            "div#content section.content-area"
        )

        return self.buildHTML(str(content))
