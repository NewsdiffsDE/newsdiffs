from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class RPOParser(BaseParser):
    domains = ['www.rp-online.de']

    feeder_pat = '(?<!(vid|bid|iid))(-1\.\d*)$'
    feeder_pages = ['http://www.rp-online.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        self.source = ', '.join(self.domains)
        # category
        keywords = soup.find('meta', {'property': 'vr:category'})
        self.category = self.compute_category(keywords['content'] if keywords else '')
        #article headline
        elt = soup.find('meta', {'property': 'og:title'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt['content']
        # tags from meta-keywords and title
        meta_keywords = soup.find('meta', {'name': 'news_keywords'})['content'] if soup.find('meta', {'name': 'news_keywords'}) else ""
        self.keywords = self.extract_keywords(meta_keywords)
        self.keywords += self.extract_keywords(self.title)
        # byline / author
        self.byline = ''
        self._cleanByline()
        # article date
        created_at = soup.find('meta', {'property': 'vr:published_time'})
        self.date = created_at['content'] if created_at else ''
        #article content
        div = soup.find('div', {'class': 'main-text '})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                         if isinstance(x, Tag) and x.name == 'p'])
