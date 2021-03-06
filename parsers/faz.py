from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class FAZParser(BaseParser):
    domains = ['www.faz.net']

    feeder_pat = 'aktuell/.*\.html$'
    feeder_pages = ['http://www.faz.net/aktuell/finanzen',
                    'http://www.faz.net/aktuell/gesellschaft',
                    'http://www.faz.net/aktuell/politik',
                    'http://www.faz.net/aktuell/wirtschaft',
                    'http://www.faz.net/aktuell/wissen',
                    ]

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        keywords = self.url.strip('http://www.faz.net/aktuell/').replace('/', ', ')
        self.source = ', '.join(self.domains)
        self.url = soup.find('meta', {'property': 'og:url'})['content'] if soup.find('meta', {'property': 'og:url'}) else self.url
        # category
        self.category = self.compute_category(keywords if keywords else '')
        #article headline
        elt = soup.find('meta', {'property': 'og:title'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt['content']
        # tags from meta-keywords and title
        meta_keywords = soup.find('meta', {'name': 'news_keywords'})['content'] if soup.find('meta', {'name': 'news_keywords'}) else ""
        self.keywords = self.extract_keywords(meta_keywords)
        self.keywords += ', ' + self.extract_keywords(self.title)
        # byline / author
        author = soup.find('span', {'class': 'Content Autor caps'})
        self.byline = author.getText() if author else ''
        self.byline = '' if self.byline == 'Frankfurter Allgemeine Zeitung GmbH' else self.byline
        self._cleanByline()
        # article date
        created_at = soup.find('meta', {'name': 'DC.date.issued'})
        self.date = created_at['content'] if created_at else ''
        #article content
        div = soup.find('div', 'FAZArtikelContent')
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        map(lambda x: x.extract(), div.findAll('span', {'class':'autorBox clearfix'})) # Author description
        map(lambda x: x.extract(), div.findAll('p', {'class':'WeitereBeitraege'})) # more articles like that one
        map(lambda x: x.extract(), div.findAll('ul', {'class':'WBListe'}))# other articles from this author

        div = div.find('div', {'class': ''})
        if hasattr(div, "childGenerator"):
            self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                            if isinstance(x, Tag) and x.name == 'p'])
        else:
            self.real_article = False
