from datetime import datetime
import re
import operator
from django.shortcuts import render_to_response, get_object_or_404
from models import Article, Version
import models
import json
from django.http import HttpResponse, Http404
import django.db
from django.db.models import Count
from twitter import *
from django.template import Context, RequestContext, loader

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

def search(request):
    search_type = request.REQUEST.get('search_type')
    searchterm = request.REQUEST.get('searchterm')
    sort = request.REQUEST.get('sort')
    source = request.REQUEST.get('source')
    date = request.REQUEST.get('date')
    ressort = request.REQUEST.get('ressort')
    pagestr=request.REQUEST.get('page', '1')

    results_displayed = 10          # number of results for each page

    if date is None:
        date = ''
    if searchterm is None:
        searchterm = ''

    try:
        page = int(pagestr)
    except ValueError:
        page = 1

    # range of results
    begin_at = 1
    end_at = results_displayed

    if page > 1:
        begin_at = ((page-1)*results_displayed)+1
        end_at = begin_at + (results_displayed-1)

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
    # get all articles which were updated on s specific date
    all_articles = Article.objects.filter(last_update__year=date[6:10],
                                            last_update__month=date[3:5],
                                            last_update__day=date[0:2]).exclude(source='')

    if search_source in SOURCES:
        all_articles = all_articles.filter(source__icontains = search_source)
    if ressort in RESSORTS:
        all_articles = all_articles.filter(category__icontains = ressort)

    all_articles = all_articles[begin_at : end_at]          # range of results

    for a in all_articles:
        versions = Version.objects.filter(article_id = a.id)
        version_count = versions.count()
        if version_count > 1:       # get all articles with changes
            all_diffs = '/diffview/?vid1='+str(a.first_version().id)+'&vid2='+str(a.latest_version().id)
            article_title = versions.order_by('-date')[0].title
            articles[a.id] = {
                'id': a.id,
                'title': article_title,
                'url': a.url,
                'source':  a.source,
                'ressort' : a.category,
                'date':  a.initial_date,
                'versioncount': version_count,
                'all_diffs' : all_diffs
                }
    return articles

def get_articles_by_url(url):
        articles = {}
        all_articles = Article.objects.filter(url = url).exclude(source='')

        for a in all_articles:
            versions = Version.objects.filter(article_id = a.id)
            version_count = versions.count()
            if version_count > 1:           # get all articles with changes
                all_diffs = '/diffview/?vid1='+str(a.first_version().id)+'&vid2='+str(a.latest_version().id)
                article_title = versions.order_by('-date')[0].title
                articles[a.id] = {
                    'id': a.id,
                    'title': article_title,
                    'url': a.url,
                    'source':  a.source,
                    'date':  a.initial_date,
                    'versioncount': version_count,
                    'ressort' : a.category,
                    'all_diffs' : all_diffs
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
        all_articles += article_objects.order_by('-initial_date')

    all_articles = all_articles[begin_at : end_at]

    for a in all_articles:
        versions = Version.objects.filter(article_id = a.id)
        version_count = versions.count()
        if version_count > 1:           # get all articles with changes
            all_diffs = '/diffview/?vid1='+str(a.first_version().id)+'&vid2='+str(a.latest_version().id)
            article_title = versions.order_by('-date')[0].title
            articles[a.id] = {
                'id': a.id,
                'title': article_title,
                'url': a.url,
                'source':  a.source,
                'date':  a.initial_date,
                'ressort':  a.category,
                'versioncount': version_count,
                'all_diffs' : all_diffs
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
    all_articles = all_articles.order_by('-initial_date')[begin_at : end_at]

    for a in all_articles:
        versions = Version.objects.filter(article_id = a.id)
        version_count = versions.count()
        if version_count > 1:           # get all articles with changes
            article_title = versions.order_by('-date')[0].title
            all_diffs = '/diffview/?vid1='+str(a.first_version().id)+'&vid2='+str(a.latest_version().id)
            articles[a.id] = {
                'id': a.id,
                'title': article_title,
                'url': a.url,
                'source':  a.source,
                'date':  a.initial_date,
                'versioncount': version_count,
                'ressort' : a.category,
                'all_diffs' : all_diffs
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

def browse(request):
    archive_date=request.REQUEST.get('date')
    ressort=request.REQUEST.get('ressort')
    source=request.REQUEST.get('source')
    pagestr=request.REQUEST.get('page', '1')
    sort=request.REQUEST.get('sort')

    results_displayed = 10          # number of results for each page

    try:
        page = int(pagestr)
    except ValueError:
        page = 1

    # range of results
    begin_at = 1
    end_at = results_displayed

    if page > 1:
        begin_at = ((page-1)*results_displayed)+1
        end_at = begin_at + (results_displayed-1)

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
        dates.append(v.date.strftime('%d.%m.%Y - %H:%M Uhr'))

        indices = [i for i, x in versions.items() if x == v]
        if not indices:
            #One of these versions doesn't exist / is boring
            return Http400()
        index = indices[0]
        adjacent_versions.append([versions.get(index+offset)
                                  for offset in (-1, 1)])


    if any(x is None for x in texts):
        return Http400()

    links = []

    for i in range(2):
        if all(x[i] for x in adjacent_versions):
           diffl = '/diffview/?vid1='+str(adjacent_versions[0][i].id)+'&vid2='+str(adjacent_versions[1][i].id)
           links.append(diffl)
        else:
            links.append('')


    oldest_newest = '/diffview/?vid1='+str(article.first_version().id)+'&vid2='+str(article.latest_version().id)

    return render_to_response('diffview.html', {
            'title': title,
            'date1':dates[0], 'date2':dates[1],
            'text1':texts[0], 'text2':texts[1],
            'prev':links[0], 'next':links[1],
            'article_shorturl': article.filename(),
            'article_id' : article.id,
            'article_url': article.url, 'v1': v1, 'v2': v2,
            'all_diffs' : oldest_newest,
            }, context_instance=RequestContext(request))

def get_rowinfo(article, version_lst=None):
    if version_lst is None:
        version_lst = article.versions()
    rowinfo = []
    lastv = None
    for version in version_lst:
        version.date = version.date.strftime('%d.%m.%Y - %H:%M Uhr')
        if lastv is None:
            diffl = ''
        else:
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
    id = request.REQUEST.get('id')
    url = request.REQUEST.get('url')

    if url :
        article = Article.objects.get(url=url)
    else:
        try:
            article = Article.objects.get(id=id)
        except Article.DoesNotExist:
            try:
                return render_to_response('article_history_missing.html', {'id': id})
            except (TypeError, ValueError):
                # bug in django + mod_rewrite can cause this. =/
                return HttpResponse('Bug!')
    created_at = article.initial_date.strftime('%d.%m.%Y - %H:%M Uhr')
    versions = get_rowinfo(article)
    return render_to_response('article_history.html', {'article':article,
                                                       'versions':versions,
                                                        'display_search_banner': came_from_search_engine(request),
                                                       'created_at': created_at,
                                                       'source' : article.source,
							'ressort': article.ressort,
							'versioncount': article.versioncount
                                                       })
def article_history_feed(request):
    id = request.REQUEST.get('id')
    url = request.REQUEST.get('url')

    if url :
        article = Article.objects.get(url=url)
    else:
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
    config = {}
    execfile("/var/www/dev/config.py", config)
    twitter = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))
    alltrends = twitter.trends.place(_id = 23424829)
    results = []

    for location in alltrends:
        for trend in location["trends"]:
            result = trend["name"].encode("utf-8")
            if result.startswith('#'):
                result = result.replace("#", "")
            results.append(result)

    return render_to_response('entdecken.html', {
                        'trend1': results[0],
						'trend2': results[1],
						'trend3': results[2],
						'trend4': results[3],
						'trend5': results[4],
						'trend6': results[5],
						'trend7': results[6],
						'trend8': results[7],
						'trend9': results[8],
						'trend10': results[9],
						})



def highlights(request):
    return render_to_response('highlights.html', {})

def kontakt(request):
    return render_to_response('kontakt.html', {})

def impressum(request):
    return render_to_response('impressum.html', {})

def index(request):
    return render_to_response('index.html', {'sources': SOURCES})
