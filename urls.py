# app specific urls

from django.conf.urls.defaults import *


urlpatterns = patterns('geonode.datamanager.views',
    url(r'^$', 'datamanager', name='datamanager'),
    #url(r'^html$', 'search_page', {'template': 'search/search_content.html'}, name='search_content'),
    #url(r'^api$', 'search_api', name='search_api'),
    #url(r'^api/data$', 'search_api', kwargs={'type':'layer'}, name='layer_search_api'),
    #url(r'^api/maps$', 'search_api', kwargs={'type':'map'}, name='maps_search_api'),
    #url(r'^api/documents$', 'search_api', kwargs={'type':'document'}, name='document_search_api'),
    #url(r'^api/authors$', 'author_list', name='search_api_author_list'),
    #url(r'^form/$', 'advanced_search', name='advanced_search'), 
)
