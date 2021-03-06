from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class ZeitParser(BaseParser):
    SUFFIX = '?print=true'
    domains = ['www.zeit.de']

    feeder_pat = '^http://www.zeit.de/(politik|wirtschaft|gesellschaft|wissen|digital)/.*\d{4}-\d{2}/.*'
    feeder_pages = ['http://www.zeit.de/index/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        keywords = self.url.strip('http://www.zeit.de').replace('/', ', ')
        self.source = ', '.join(self.domains)
        self.url = soup.find('meta', {'property': 'og:url'})['content'] if soup.find('meta', {'property': 'og:url'}) else self.url
        # category
        self.category = self.compute_category(keywords if keywords else '')
        #article headline
        elt = soup.find('span', 'title')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # tags from meta-keywords and title
        meta_keywords = soup.find('meta', {'name': 'keywords'})['content'] if soup.find('meta', {'name': 'keywords'}) else ""
        self.keywords = self.extract_keywords(meta_keywords)
        self.keywords += ', ' + self.extract_keywords(self.title)
        # byline / author
        author = soup.find('span', {'class': 'header_author'})
        self.byline = author.getText() if author else ''
        self._cleanByline()
        # article date
        created_at = soup.find('span', 'articlemeta-datetime')
        self.date = created_at.getText() if created_at else ''
        #article content
        div = soup.find('div', 'article-body')
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                        if isinstance(x, Tag) and x.name == 'p'])
