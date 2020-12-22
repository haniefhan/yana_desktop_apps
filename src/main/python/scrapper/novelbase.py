import requests


class Novelbase():
    _base_url = ""
    _user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

    @classmethod
    def _get_web_page(self, url, options=dict()):
        headers = {}
        headers["User-Agent"] = self._user_agent

        if "Referer" in options:
            headers["Referer"] = options["Referer"]
        else:
            headers["Referer"] = self._base_url

        return requests.get(url, headers=headers)
