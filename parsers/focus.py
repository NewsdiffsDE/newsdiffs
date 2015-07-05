from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup


class FocusParser(BaseParser):
    SUFFIX = '?drucken=1'
    domains = ['www.focus.de']

<<<<<<< HEAD
    feeder_pat   = '^http://www.focus.de/(politik|finanzen|gesundheit|wissen|panorama|digital)/.*\.html$'
=======
    feeder_pat   = '^http://www.focus.de/(politik|finanzen|gesundheit|wissen)'
>>>>>>> DjangoTemplating
    feeder_pages = ['http://www.focus.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
<<<<<<< HEAD
        # category
        keywords = self.url.strip('http://www.focus.de').replace('/', ',')
        self.category = self.compute_category(keywords if keywords else '')
=======
>>>>>>> DjangoTemplating
        #article headline
        elt = soup.find('h1')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
        try:
            author = soup.find('a', {'rel':'author'}).text
        except:
            author = ''
        self.byline = author
<<<<<<< HEAD
        self._cleanByline()
=======
>>>>>>> DjangoTemplating
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
<<<<<<< HEAD
        self.body = text
=======
        self.body = text
>>>>>>> DjangoTemplating
