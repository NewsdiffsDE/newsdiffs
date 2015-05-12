from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class FAZParser(BaseParser):
    domains = ['www.faz.net']

    feeder_pat = 'aktuell/.*\.html$'
    feeder_pages = ['http://www.faz.net/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        #article headline
        elt = soup.find('meta', {'property': 'og:title'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt['content']
        # byline / author
        author = soup.find('meta', {'name': 'author'})['content']
        self.byline = author if author else ''
        # article date
        created_at = soup.find('meta', {'name': 'DC.date.issued'})['content']
        self.date = created_at if created_at else ''
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
