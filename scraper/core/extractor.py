from pyquery import PyQuery as pq

from . import client


class ExtractorBase:

    name = None

    def __init__(self, url):
        self.url = url
        self._html = None

    def __repr__(self):
        return self.name

    # @property
    # def ok(self):
    #     return bool(self.html)

    @property
    def html(self):
        if self._html is None:
            self._html = client.html(self.url)
        return self._html

    @property
    def doc(self):
        return pq(self.html or None)


class Image(ExtractorBase):

    def general_choice(self):
        sel = (
            'meta[property="og:image"],'       # attr: content
            'meta[itemprop="image"],'          # attr: content
            'meta[name="twitter:image"],'      # attr: content
            'meta[name="twitter:image:src"]'   # attr: content
        )
        image = self.doc(sel).attr('content')

        if not image:
            sel = 'img[itemprop="image"],[itemprop="image"] img'
            image = self.doc(sel).attr('src')

        if not image:
            sel = 'link[rel="image_src"]'
            image = self.doc(sel).attr('href')

        return image
