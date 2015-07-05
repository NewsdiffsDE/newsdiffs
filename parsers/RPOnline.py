from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class RPOParser(BaseParser):
    domains = ['www.rp-online.de']

<<<<<<< HEAD
    feeder_pat = '(?<!(vid|bid|iid))(-1\.\d*)$'
=======
    feeder_pat = '1\.\d*$'
>>>>>>> DjangoTemplating
    feeder_pages = ['http://www.rp-online.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
<<<<<<< HEAD
        # category
        keywords = soup.find('meta', {'property': 'vr:category'})
        self.category = self.compute_category(keywords['content'] if keywords else '')
        #article headline
        elt = soup.find('meta', {'property': 'og:title'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt['content']
        # byline / author
        self.byline = ''
        self._cleanByline()
        # article date
        created_at = soup.find('meta', {'property': 'vr:published_time'})
        self.date = created_at['content'] if created_at else ''
        #article content
        div = soup.find('div', {'class': 'main-text '})
=======
        #article headline
        elt = soup.find('meta', {'property': 'og:title'})['content']
        if elt is None:
            self.real_article = False
            return
        self.title = elt
        # byline / author
        author = soup.find('meta', {'itemprop': 'author'})['content']
        self.byline = author if author else ''
        # article date
        created_at = soup.find('meta', {'property': 'vr:published_time'})['content']
        self.date = created_at if created_at else ''
        #article content
        div = soup.find('div', {'class': 'main-text '})
        intro = soup.find('div', {'class': 'first intro'})
        if intro is None:
            intro = ''
        else:
            intro = intro.find('strong').getText()
>>>>>>> DjangoTemplating
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
<<<<<<< HEAD
        self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
=======
        self.body = intro
        self.body += '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
>>>>>>> DjangoTemplating
                                         if isinstance(x, Tag) and x.name == 'p'])
