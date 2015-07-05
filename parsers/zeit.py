from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class ZeitParser(BaseParser):
    SUFFIX = '?print=true'
    domains = ['www.zeit.de']

<<<<<<< HEAD
    feeder_pat = '^http://www.zeit.de/(politik|wirtschaft|gesellschaft|wissen|digital)/.*\d{4}-\d{2}/.*'
    feeder_pages = ['http://www.zeit.de/index/']
=======
    feeder_pat = '^http://www.zeit.de/news/\d'
    feeder_pages = ['http://www.zeit.de/news/index/']
>>>>>>> DjangoTemplating

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
<<<<<<< HEAD
        # category
        keywords = self.url.strip('http://www.zeit.de').replace('/', ',')
        self.category = self.compute_category(keywords if keywords else '')
=======
>>>>>>> DjangoTemplating
        #article headline
        elt = soup.find('span', 'title')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
        author = soup.find('span', {'class': 'header_author'})
        self.byline = author.getText() if author else ''
<<<<<<< HEAD
        self._cleanByline()
=======
>>>>>>> DjangoTemplating
        # article date
        created_at = soup.find('span', 'articlemeta-datetime')
        self.date = created_at.getText() if created_at else ''
        #article content
        div = soup.find('div', 'article-body')
<<<<<<< HEAD
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
=======
        div = self.remove_non_content(div)
        if div is None:
            self.real_article = False
            return
>>>>>>> DjangoTemplating
        self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                        if isinstance(x, Tag) and x.name == 'p'])
