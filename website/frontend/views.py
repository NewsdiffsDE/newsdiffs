from datetime import datetime, timedelta
import re
import operator

from django.shortcuts import render_to_response, get_object_or_404, redirect
from models import Article, Version
import models
import json
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
import urllib
import django.db
from django.db.models import Count
import time
from django.template import Context, RequestContext, loader
from django.views.decorators.cache import cache_page

from random import randint

OUT_FORMAT = '%B %d, %Y at %l:%M%P EDT'

SEARCH_ENGINES = """
http://www.ask.com
http://www.google
https://www.google
search.yahoo.com
http://www.bing.com
""".split()

RESSORTS = """
Allgemein
Politik
Wirtschaft
Regional
Technik
Wissenschaft
Gesellschaft
""".split()


SOURCES = '''
Zeit
Bild
Focus
Spiegel
Stern
Welt
FAZ
n-tv
RP-ONLINE
Sueddeutsche
TAZ
'''.split()

SEARCH_TYPES = '''
Stichwort
Autor
URL
'''.split()

def came_from_search_engine(request):
    return any(x in request.META.get('HTTP_REFERER', '')
               for x in SEARCH_ENGINES)



def Http400():
    t = loader.get_template('404.html')
    return HttpResponse(t.render(Context()), status=400)

def get_first_update(source):
    if source is None:
        source = ''
    updates = models.Article.objects.order_by('last_update').filter(last_update__gt=datetime(1990, 1, 1, 0, 0),
                                                                    url__icontains=source)
    try:
        return updates[0].last_update
    except IndexError:
        return datetime.datetime.now()

def get_last_update(source):
    if source is None:
        source = ''
    updates = models.Article.objects.order_by('-last_update').filter(last_update__gt=datetime.datetime(1990, 1, 1, 0, 0), url__icontains=source)
    try:
        return updates[0].last_update
    except IndexError:
        return datetime.datetime.now()


@cache_page(60 * 30)  #30 minute cache
def search(request):
    search_type = request.REQUEST.get('search_type')
    searchterm = request.REQUEST.get('searchterm')
    sort = request.REQUEST.get('sort')
    source = request.REQUEST.get('source')
    date = request.REQUEST.get('date')
    ressort = request.REQUEST.get('ressort')
    pagestr=request.REQUEST.get('page', '1')

    if date is None:
        date = ''
    if searchterm is None:
        searchterm = ''

    try:
        page = int(pagestr)
    except ValueError:
        page = 1

    begin_at = 1
    end_at = 10

    if page > 1:
        begin_at = ((page-1)*10)+1
        end_at = begin_at + 9

    if len(searchterm) > 0:
        if search_type not in SEARCH_TYPES :
            search_type = u'Stichwort'
        if searchterm[:4] == 'http' or searchterm[:4] == 'www.':
            search_type = u'URL'

        if search_type == u'Stichwort':
            articles = get_articles_by_keyword(searchterm, sort, source, ressort, date, begin_at-1, end_at)
        elif search_type == u'Autor':
            articles = get_articles_by_author(searchterm, sort, source, ressort, date, begin_at-1, end_at)
        elif search_type == u'URL':
            articles = get_articles_by_url(searchterm)

        return render_to_response('suchergebnisse.html', {
                'articles': articles,
                'articles_count' : len(articles),
                'searchterm': searchterm,
                'archive_date' : date,
                'search_type': search_type,
                'source' : source,
                'sort' : sort,
                'ressort' : ressort,
                'all_sources' : SOURCES,
                'all_ressorts' : RESSORTS,
                'page':page,
                'begin_at' : begin_at,
                'end_at' : begin_at + len(articles) -1,
                'template' : 'suchergebnisse'
                })
    else:
        return render_to_response('suchergebnisse.html', {})

def get_archive(date, ressort, search_source, begin_at, end_at):
    articles = {}

    all_articles = Article.objects.filter(initial_date__year=date[6:10],
                                            initial_date__month=date[3:5],
                                            initial_date__day=date[0:2]).exclude(source='')

    if search_source in SOURCES:
        all_articles = all_articles.filter(source__icontains = search_source)
    if ressort in RESSORTS:
        all_articles = all_articles.filter(category__icontains = ressort)

    all_articles = all_articles[begin_at : end_at]

    for a in all_articles:
        version = Version.objects.filter(article_id = a.id)
        article_title = version.order_by('date')[0].title
        articles[a.id] = {
                'id': a.id,
                'title': article_title,
                'url': a.url,
                'source':  a.source,
                'date':  a.initial_date,
                'versioncount': version.count()
                }
    return articles

def get_articles_by_url(url):
        articles = {}
        all_articles = Article.objects.filter(url = url).exclude(source='')

        for a in all_articles:
            version = Version.objects.filter(article_id = a.id)
            versioncount = Version.objects.filter(article_id = a.id).count()
            article_title = version.order_by('date')[0].title
            articles[a.id] = {
                'id': a.id,
                'title': article_title,
                'url': a.url,
                'source':  a.source,
                'date':  a.initial_date,
                'versioncount': versioncount,
                'ressort' : a.category
                }
        return articles

def get_articles_by_author(searchterm, sort, search_source, ressort, date, begin_at, end_at):
    articles = {}
    all_articles = []
    versions = Version.objects.filter(byline__icontains = searchterm)

    for v in versions:
        article_objects = Article.objects.filter(id = v.article_id).exclude(source='')
        if len(date) is 10:
            article_objects = article_objects.filter(initial_date__year=date[6:10],
                                                        initial_date__month=date[3:5],
                                                        initial_date__day=date[0:2])
        if search_source in SOURCES:
            article_objects = article_objects.filter(source__icontains = search_source)
        if ressort in RESSORTS :
            article_objects = article_objects.filter(category = ressort)
        all_articles += article_objects.order_by('initial_date')

    all_articles = all_articles[begin_at : end_at]

    for a in all_articles:
        version = Version.objects.filter(article_id = a.id)
        versioncount = Version.objects.filter(article_id = a.id).count()
        article_title = version.order_by('date')[0].title
        articles[a.id] = {
            'id': a.id,
            'title': article_title,
            'url': a.url,
            'source':  a.source,
            'date':  a.initial_date,
            'ressort':  a.category,
            'versioncount': versioncount
            }

    if sort == u'sortCount':
        articles = sorted(articles.items(), reverse=True, key=operator.itemgetter('versioncount'))
    return articles

def get_articles_by_keyword(searchterm, sort, search_source, ressort, date, begin_at, end_at):
    articles = {}

    all_articles = Article.objects.filter(keywords__icontains = searchterm).exclude(source='')

    if len(date) is 10:
        all_articles = all_articles.filter(initial_date__year=date[6:10],
                                                        initial_date__month=date[3:5],
                                                        initial_date__day=date[0:2])
    if search_source in SOURCES:
        all_articles = all_articles.filter(source__icontains = search_source)
    if ressort in RESSORTS:
        all_articles = all_articles.filter(category__icontains = ressort)
    all_articles = all_articles.order_by('initial_date')[begin_at : end_at]

    for a in all_articles:
        version = Version.objects.filter(article_id = a.id)
        versioncount = Version.objects.filter(article_id = a.id).count()
        article_title = version.order_by('date')[0].title
        articles[a.id] = {
            'id': a.id,
            'title': article_title,
            'url': a.url,
            'source':  a.source,
            'date':  a.initial_date,
            'versioncount': versioncount,
            'ressort' : a.category
            }

    if sort is 'sortCount':
        articles = sorted(articles.items(), reverse=True, key=operator.itemgetter('versioncount'))
    return articles

def get_articles(source=None, distance=0):
    articles = []
    rx = re.compile(r'^https?://(?:[^/]*\.)%s/' % source if source else '')

    pagelength = datetime.timedelta(days=1)
    end_date = datetime.datetime.now() - distance * pagelength
    start_date = end_date - pagelength

    print 'Asking query'
    version_query = '''SELECT
    version.id, version.article_id, version.v, version.title,
      version.byline, version.date, version.boring, version.diff_json,
      T.age as age,
      Articles.url as a_url, Articles.initial_date as a_initial_date,
      Articles.last_update as a_last_update, Articles.last_check as a_last_check
    FROM version,
     (SELECT Articles.id as article_id, MAX(T3.date) AS age, COUNT(T3.id) AS num_vs
      FROM Articles LEFT OUTER JOIN version T3 ON (Articles.id = T3.article_id)
      WHERE (T3.boring=0) GROUP BY Articles.id
      HAVING (age > %s  AND age < %s  AND num_vs > 1 )) T, Articles
    WHERE (version.article_id = Articles.id) and
          (version.article_id = T.article_id) and
          NOT version.boring
    ORDER BY date'''

    all_versions = models.Version.objects.raw(version_query,
                                              (start_date, end_date))
    article_dict = {}
    for v in all_versions:
        a=models.Article(id=v.article_id,
                         url=v.a_url, initial_date=v.a_initial_date,
                         last_update=v.a_last_update, last_check=v.a_last_check)
        v.article = a
        article_dict.setdefault(v.article, []).append(v)

    for article, versions in article_dict.items():
        url = article.url
        if not rx.match(url):
            print 'REJECTING', url
            continue
        if 'blogs.nytimes.com' in url: #XXX temporary
            continue

        if len(versions) < 2:
            continue
        rowinfo = get_rowinfo(article, versions)
        articles.append((article, versions[-1], rowinfo))
    print 'Queries:', len(django.db.connection.queries), django.db.connection.queries
    articles.sort(key = lambda x: x[-1][0][1].date, reverse=True)
    return articles

def is_valid_domain(domain):
    """Cheap method to tell whether a domain is being tracked."""
    return any(domain.endswith(source) for source in SOURCES)

@cache_page(60 * 30)  #30 minute cache
def browse(request):
    archive_date=request.REQUEST.get('date')
    ressort=request.REQUEST.get('ressort')
    source=request.REQUEST.get('source')
    pagestr=request.REQUEST.get('page', '1')
    sort=request.REQUEST.get('sort')
    try:
        page = int(pagestr)
    except ValueError:
        page = 1

    begin_at = 1
    end_at = 10

    if page > 1:
        begin_at = ((page-1)*10)+1
        end_at = begin_at + 9

    if archive_date is None or archive_date is u'':
        archive_date = datetime.today().strftime('%d.%m.%Y')

    articles = get_archive(archive_date, ressort, source, begin_at-1, end_at)
    return render_to_response('archiv.html', {
                'articles': articles,
                'articles_count' : len(articles),
                'archive_date': archive_date,
                'all_sources': SOURCES,
                'source' : source,
                'ressort' : ressort,
                'all_ressorts' : RESSORTS,
                'page':page,
                'sort' : sort,
                'begin_at' : begin_at,
                'end_at' : begin_at + len(articles) -1,
                'template' : 'archive'
                })

@cache_page(60 * 30)  #30 minute cache
def feed(request, source=''):
    if source not in SOURCES + ['']:
        raise Http404
    pagestr=request.REQUEST.get('page', '1')
    try:
        page = int(pagestr)
    except ValueError:
        page = 1

    first_update = get_first_update(source)
    last_update = get_last_update(source)
    num_pages = (datetime.datetime.now() - first_update).days + 1
    page_list=range(1, 1+num_pages)

    articles = get_articles(source=source, distance=page-1)
    return render_to_response('feed.xml', {
            'source': source, 'articles': articles,
            'page':page,
            'request':request,
            'page_list': page_list,
            'last_update': last_update,
            'sources': SOURCES
            },
            context_instance=RequestContext(request),
            mimetype='application/atom+xml')

def diffview(request, vid1='', vid2=''):
    # urlarg is unused, and only for readability
    # Could be strict and enforce urlarg == article.filename()

    vid1=request.REQUEST.get('vid1')
    vid2=request.REQUEST.get('vid2')
    try:
        v1 = Version.objects.get(id=int(vid1))
        v2 = Version.objects.get(id=int(vid2))
    except Version.DoesNotExist:
        raise Http404

    article = v1.article

    if v1.article != v2.article:
        raise Http404

    title = article.latest_version().title

    versions = dict(enumerate(article.versions()))

    adjacent_versions = []
    dates = []
    texts = []

    for v in (v1, v2):
        texts.append(v.text())
        dates.append(v.date.strftime(OUT_FORMAT))

        indices = [i for i, x in versions.items() if x == v]
        if not indices:
            #One of these versions doesn't exist / is boring
            return Http400()
        index = indices[0]
        adjacent_versions.append([versions.get(index+offset)
                                  for offset in (-1, 1)])


    if any(x is None for x in texts):
        return Http400()

   # links = []

    #if urlarg[0:7] is 'http://':
     #   urlarg= article.url[len('http://'):].rstrip('/')
    #for i in range(2):
     #   if all(x[i] for x in adjacent_versions):
      #      diffl = reverse('diffview', kwargs=dict(vid1=adjacent_versions[0][i].id,
                        #                            vid2=adjacent_versions[1][i].id))
      #      links.append(diffl)
      #  else:
      #      links.append('')

    date1 = dates[0].strftime('%d.%m.%Y')
    date2 = dates[1].strftime('%d.%m.%Y')

    return render_to_response('diffview.html', {
            'title': title,
            'date1':date1, 'date2':date2,
            'text1':texts[0], 'text2':texts[1],
            'article_shorturl': article.filename(),
            'article_url': article.url, 'v1': v1, 'v2': v2,
            })

def get_rowinfo(article, version_lst=None):
    if version_lst is None:
        version_lst = article.versions()
    rowinfo = []
    lastv = None
    urlarg = article.filename()
    for version in version_lst:
        version.date = version.date.strftime('%d.%m.%Y')
        if lastv is None:
            diffl = ''
        else:
           # diffl = reverse('diffview', kwargs=dict(vid1=lastv.id, vid2=version.id, urlarg=urlarg))
            diffl = '/diffview/?vid1='+str(lastv.id)+'&vid2='+str(version.id)
        rowinfo.append((diffl, version))
        lastv = version
    rowinfo.reverse()
    return rowinfo


def prepend_http(url):
    """Return a version of the url that starts with the proper scheme.
    url may look like
    www.nytimes.com
    https:/www.nytimes.com    <- because double slashes get stripped
    http://www.nytimes.com
    """
    components = url.split('/', 2)
    if len(components) <= 2 or '.' in components[0]:
        components = ['http:', '']+components
    elif components[1]:
        components[1:1] = ['']
    return '/'.join(components)


def article_history(request):
    id = request.REQUEST.get('id') # this is the deprecated interface.
    try:
        article = Article.objects.get(id=id)
    except Article.DoesNotExist:
        try:
            return render_to_response('article_history_missing.html', {'id': id})
        except (TypeError, ValueError):
            # bug in django + mod_rewrite can cause this. =/
            return HttpResponse('Bug!')

    versions = get_rowinfo(article)
    return render_to_response('article_history.html', {'article':article,
                                                       'versions':versions,
                                                        'display_search_banner': came_from_search_engine(request),
                                                       'created_at': article.initial_date
                                                       })
def article_history_feed(request):
    id = request.REQUEST.get('id')
    article = get_object_or_404(Article, id=id)
    rowinfo = get_rowinfo(article)
    return render_to_response('article_history.xml',
                              { 'article': article,
                                'versions': rowinfo,
                                'request': request,
                                },
                              context_instance=RequestContext(request),
                              mimetype='application/atom+xml')

def json_view(request, vid):
    version = get_object_or_404(Version, id=int(vid))
    data = dict(
        #category=version.category,
        title=version.title,
        byline = version.byline,
        date = version.date.isoformat(),
        text = version.text(),
        )
    return HttpResponse(json.dumps(data), mimetype="application/json")

def about(request):
    return render_to_response('about.html', {})

def history(request):
    return render_to_response('article_history.html', {})

def artikel(request):
    return render_to_response('diffview.html', {})

def entdecken(request):
    return render_to_response('entdecken.html', {})

def highlights(request):
    return render_to_response('highlights.html', {})

def kontakt(request):
    return render_to_response('kontakt.html', {})

def impressum(request):
    return render_to_response('impressum.html', {})

def index(request):
    return render_to_response('index.html', {'sources': SOURCES})
