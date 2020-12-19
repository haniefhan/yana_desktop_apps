import requests
import re

from bs4 import BeautifulSoup


class Moonruneworks():

    _base_url = "https://moonruneworks.com/"

    def __init__(self):
        super(Moonruneworks, self).__init__()

    @classmethod
    def getList(self):
        ret = []
        url = self._base_url

        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        novel_list = soup.select(
            "ul#primary-menu li#menu-item-32 ul.sub-menu li"
        )

        for novel in novel_list:
            href = novel.select_one("a").get("href")
            title = novel.select_one("a").getText()

            # detail = self.getDetail(href)

            new = {
                "title": title,
                "url": href,
            }
            ret.append(new)

        return ret

    @classmethod
    def getDetail(self, url):
        return {}

    @classmethod
    def getChapters(self, url, soup=None):
        if soup is None:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

        chapters = []

        arr_select = [
            "div.entry-content h4",
            "div.entry-content p strong"
        ]

        for query in arr_select:
            for h4 in soup.select(query):
                volume = h4.getText().strip()
                ul = h4.findNext("ul")

                for a in ul.select("li a"):
                    title = a.getText().strip()
                    url = a.get('href')

                    v = "".join([i for i in volume if i.isdigit()])
                    c = "".join([i for i in title if i.isdigit()])

                    no = "v" + v + 'c' + c

                    if title != '':
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
        body{font-family: Arial; font-size: 11pt;}
        p{margin: 10px 20px; line-height: 25px;}
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
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        decompose_list = [
            # "div#content section.content-area p.has-text-align-center",
            "div#content div.content-area article script",
            "div#content div.content-area article div.sharedaddy",
            "div#content div.content-area article footer.entry-footer",
            # "div#content section.content-area div.wpcnt"
        ]

        for decompose in decompose_list:
            item = soup.select_one(decompose)
            if item is not None:
                item.decompose()

        content = soup.select_one(
            "div#content div.content-area article"
        )

        return self.buildHTML(str(content))
