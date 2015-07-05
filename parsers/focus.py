from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup


class FocusParser(BaseParser):
    SUFFIX = '?drucken=1'
    domains = ['www.focus.de']

    feeder_pat   = '^http://www.focus.de/(politik|finanzen|gesundheit|wissen|panorama|digital)/.*\.html$'
    feeder_pages = ['http://www.focus.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        self.source = ', '.join(self.domains)
        # category
        keywords = self.url.strip('http://www.focus.de').replace('/', ',')
        self.category = self.compute_category(keywords if keywords else '')
        #article headline
        elt = soup.find('h1')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # tags from meta-keywords and title
        meta_keywords = soup.find('meta', {'name': 'news_keywords'})['content'] if soup.find('meta', {'name': 'news_keywords'}) else ""
        self.keywords = self.extract_keywords(meta_keywords)
        self.keywords += self.extract_keywords(self.title)
        # byline / author
        try:
            author = soup.find('a', {'rel':'author'}).text
        except:
            author = ''
        self.byline = author
        self._cleanByline()
        # article date
        created_at = soup.find('meta', {'name':'date'})
        self.date = created_at['content'] if created_at else ''
        #article content
        self.body = ''
        div = soup.find('div', 'articleContent')
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        map(lambda x: x.extract(), div.findAll('div', {'class':'adition'})) #focus
        text = ''
        p = div.findAll('p')
        for txt in p:
                text += txt.getText()+'\n'
        self.body = text
