from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class NTVParser(BaseParser):
    domains = ['www.n-tv.de']

    feeder_pat = '^http://www.n-tv.de/(politik|wirtschaft|panorama|technik|wissen)/.*article\d*'
    feeder_pages = ['http://www.n-tv.de']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        # category
        keywords = self.url.strip('http://www.n-tv.de').replace('/', ',')
        self.category = self.compute_category(keywords if keywords else '')
        # Remove any potential "rogue" video articles, that bypass the URL check
        try:
            if 'Mediathek' in soup.find('title').getText():
                self.real_article = False
                return
        except:
            pass
        #article headline
        elt = soup.find('h1', {'class': 'h1'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
        author = soup.find('p', {'class': 'author'})
        self.byline = author.getText() if author else ''
        self._cleanByline()
        # article date
        created_at = soup.find('div', {'itemprop': 'datePublished'})
        self.date = created_at['content'] if created_at else ''
        #article content
        div = soup.find('div', {'class': 'content'})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        map(lambda x: x.extract(), div.findAll('p', {'class': 'author'}))
        self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                        if isinstance(x, Tag) and x.name == 'p'])

