from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup


class SternParser(BaseParser):
    SUFFIX = ''
    domains = ['www.stern.de']

<<<<<<< HEAD
    feeder_pat   = '^http://www.stern.de/(politik|wirtschaft|panorama|wissen|digital)/.*\d*\.html$'
    feeder_pages = ['http://www.stern.de/news',
                    'http://www.stern.de/news/?order&month&year&pageNum=1',
                    'http://www.stern.de/news/?order&month&year&pageNum=2',
                    'http://www.stern.de/news/?order&month&year&pageNum=3'
=======
    feeder_pat   = '^http://www.stern.de/(politik|wirtschaft|panorama|lifestyle|wissen|digital)/'
    feeder_pages = ['http://www.stern.de/news',
                    'http://www.stern.de/news/2',
                    'http://www.stern.de/news/3',
                    'http://www.stern.de/news/4'
>>>>>>> DjangoTemplating
                    ]

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
<<<<<<< HEAD
        # category
        keywords = self.url.strip('http://www.stern.de/').replace('/', ',')
        self.category = self.compute_category(keywords if keywords else '')
        #article headline
        elt = soup.find('h2', {'class': 'a-h1-title'})
=======
        #article headline
        elt = soup.find('h2', {'id': 'div_article_headline'})
>>>>>>> DjangoTemplating
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
<<<<<<< HEAD
        author = soup.find('div', {'class': 'guest-authors'})
        self.byline = author.getText() if author else ''
        self._cleanByline()
=======
        author = soup.find('p', {'id': 'div_article_intro'}).find('span')
        self.byline = author.getText() if author else ''
>>>>>>> DjangoTemplating
        # article date
        created_at = soup.find('meta', {'name': 'date'})
        self.date = created_at['content'] if created_at else ''
        #article content
<<<<<<< HEAD
        div = soup.find('article', {'class': 'article'})
=======
        div = soup.find('div', {'itemprop': 'mainContentOfPage'})
>>>>>>> DjangoTemplating
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        text = ''
        p = div.findAll('p')
        for txt in p:
                text += txt.getText()+'\n'
<<<<<<< HEAD
        self.body = text
=======
        self.body = text
>>>>>>> DjangoTemplating
