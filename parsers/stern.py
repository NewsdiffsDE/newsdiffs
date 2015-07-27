from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup


class SternParser(BaseParser):
    SUFFIX = ''
    domains = ['www.stern.de']

    feeder_pat   = '^http://www.stern.de/(politik|wirtschaft|panorama|wissen|digital)/.*\d*\.html$'
    feeder_pages = ['http://www.stern.de/news/',
                    'http://www.stern.de/news/?order&month&year&pageNum=1',
                    'http://www.stern.de/news/?order&month&year&pageNum=2',
                    'http://www.stern.de/news/?order&month&year&pageNum=3'
                    ]


    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        print(self.url)
        self.source = ', '.join(self.domains)
        self.url = soup.find('meta', {'property': 'og:url'})['content'] if soup.find('meta', {'property': 'og:url'}) else self.url
        print(self.url)
        # category
        keywords = self.url.strip('http://www.stern.de/').replace('/', ',')
        self.category = self.compute_category(keywords if keywords else '')
        #article headline
        elt = soup.find('h2', {'class': 'a-h1-title'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # tags from meta-keywords and title
        meta_keywords = soup.find('meta', {'name': 'news_keywords'})['content'] if soup.find('meta', {'name': 'news_keywords'}) else ""
        self.keywords = self.extract_keywords(meta_keywords)
        self.keywords += self.extract_keywords(self.title)
        # byline / author
        author = soup.find('div', {'class': 'guest-authors'})
        self.byline = author.getText() if author else ''
        self._cleanByline()
        # article date
        created_at = soup.find('meta', {'name': 'date'})
        self.date = created_at['content'] if created_at else ''
        #article content
        div = soup.find('article', {'class': 'article'})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        text = ''
        p = div.findAll('p')
        for txt in p:
                text += txt.getText()+'\n'
        self.body = text

