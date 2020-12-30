import requests


class Novelbase():
    _base_url = ""
    _user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

    @classmethod
    def _get_web_page(self, url, reqtype="get", options=dict()):
        headers = {}
        headers["User-Agent"] = self._user_agent

        if "Accept" in options:
            headers["Accept"] = options["Accept"]

        if "Accept-Encoding" in options:
            headers["Accept-Encoding"] = options["Accept-Encoding"]

        if "Content-Type" in options:
            headers["Content-Type"] = options["Content-Type"]

        if "Origin" in options:
            headers["Origin"] = options["Origin"]
        else:
            headers["Origin"] = self._base_url

        if "Referer" in options:
            headers["Referer"] = options["Referer"]
        else:
            headers["Referer"] = self._base_url

        if reqtype == "post":
            body = {}
            if "post" in options:
                body = options["post"]
            return requests.post(url, headers=headers, data=body)
        else:
            return requests.get(url, headers=headers)
