import requests
import re

from bs4 import BeautifulSoup


class Shintranslations():

    _base_url = "https://shintranslations.com/"

    def __init__(self):
        super(Shintranslations, self).__init__()

    @classmethod
    def getList(self):
        ret = []
        url = self._base_url

        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        novel_list = soup.select(
            "nav.nav-menu ul#menu-menu li.menu-item a"
        )

        for novel in novel_list:
            if "ToC" in novel.getText():
                href = novel.get("href")
                # title = novel.getText()

                detail = self.getDetail(href)

                new = {
                    "title": detail["title"],
                    "title_original": detail["title_original"],
                    "url": href,
                    "image": detail["image"],
                    "author": detail["author"],
                    "artist": detail["artist"],
                }
                ret.append(new)

        return ret

    @classmethod
    def getDetail(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.select_one(
            "main#main-content div.content-box div.content-area h1.main-title"
        ).getText().replace("ToC", "").strip()
        title_original = ""
        author = ""
        artist = ""
        image = soup.select_one(
            "main#main-content div.content-box div.content-area div.text-formatting img"
        ).get("src")

        for p in soup.select(
            "main#main-content div.content-box div.content-area div.text-formatting p"
        ):
            if "English title:" in p.getText():
                if len(title) == 3 or len(title) == 4:
                    title = p.getText().replace("English title:", "").strip()
            elif "Novel title:" in p.getText():
                title_original = p.getText().replace("Novel title:", "").strip()
            elif "Author:" in p.getText():
                author = p.getText().replace("Author:", "").strip()
            elif "Illustrator:" in p.getText():
                artist = p.getText().replace("Illustrator:", "").strip()

        detail = {
            "title": title,
            "title_original": title_original,
            "author": author,
            "artist": artist,
            "image": image,
        }

        return detail

    @classmethod
    def getChapters(self, url, soup=None):
        if soup is None:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

        chapters = []

        query = soup.select_one(
            # "main#main-content div.content-box div.content-area"
            # "main#main-content"
            "body"  # because the new gate has a wrong </div> problem
        ).findAll(["h4", "p"])

        volume = ""
        c = "0"

        exception_list = [
            "Volume 1", "Volume 2"
        ]

        volume_list = []

        for tag in query:
            if tag.name == "h4":
                volume = tag.getText().strip().replace("\xa0", " ")
                c = "0"
                volume_list.append(volume)
            if tag.name == "p":
                for a in tag.findAll("a"):
                    title = a.getText().strip().replace("\xa0", " ")
                    prv = a.previous_element
                    url = a.get("href")

                    if title not in exception_list and self._base_url in url:
                        v = "".join([i for i in volume if i.isdigit()])
                        p = ""

                        if "Chapter" in title:
                            c = "".join([i for i in title if i.isdigit()])
                        elif "Part" in title:
                            if "Chapter" in prv:
                                c = "".join([i for i in prv if i.isdigit()])
                            p = "p"
                            p += "".join([i for i in title if i.isdigit()])
                            title = "Chapter " + c + " " + title
                        elif (
                            "Illustrations" in title
                            or "Kristoff Report" in title
                            or "Illustration" in title
                            or "Story" in title
                        ):
                            if len(c) > 0:
                                c = str(int(c) + 1)

                        no = "v" + v + "c" + c
                        if p != "":
                            no += p

                        chp = {
                            "no": no,
                            "title": title,
                            "url": url,
                            "volume": volume,
                        }
                        chapters.append(chp)
                    elif "Volume" in title and self._base_url in url:
                        # Specials - THE NEW GATE
                        v = "".join([i for i in title if i.isdigit()])
                        c = "9"
                        # for vol in volume_list:
                        #     if title.upper()
                        volume = "".join([
                            i for i in volume_list if title.upper() + " :" in i
                        ])

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
        body{font-family: Arial; font-size: 11pt; padding: 20px;}
        div{line-height: 25px;}
        img{margin: 10px 0px; border: 1px solid #999;}
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
            "script",
            "ins",
            "noscript",
            "main#main-content div.content-box div.content-area div.sharedaddy",
            "main#main-content div.content-box div.content-area div#disqus_thread",
        ]

        for decompose in decompose_list:
            for item in soup.select(decompose):
                if item is not None:
                    item.decompose()

        for item in soup.select(
            "main#main-content div.content-box div.content-area p"
        ):
            if "←Previous" in item.getText() or "Next→" in item.getText():
                item.decompose()

        content = soup.select_one(
            "main#main-content div.content-box div.content-area"
        )

        img_attr = [
            "data-lazy-sizes", "data-lazy-src", "data-lazy-srcset", "class",
            "srcset", "loading", "height"
        ]

        for img in content.findAll("img"):
            # print(img.get("src"))
            # print(img)
            for attr in img_attr:
                if img.get(attr) is not None:
                    del(img[attr])
            img['width'] = "100%"

        return self.buildHTML(str(content))
