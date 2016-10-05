from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^upload/', 'epa.views.upload_data'),
    url(r'^send_url/', 'epa.views.upload_from_url'),    
    url(r'^delete/', 'epa.views.delete_data'),
    url(r'^prediction_data/$', 'epa.views.view_prediction_data'),
    url(r'^prediction_data/(?P<page>\d+)/(?P<page_size>\d+)/$', 'epa.views.view_prediction_data'),

    url(r'^account/my/$', 'epa.views.edit_user'),
    url(r'^account/change/$', 'epa.views.edit_user'),
    url(r'^account_delete/$', 'epa.views.delete_user'),
    url(r'^account/add/$', 'epa.views.add_user'),
    url(r'^account/register/$', 'epa.views.register'),
    url(r'^account/$', 'epa.views.view_user'),
    url(r'^login/$', 'epa.views.view_login'),
    url(r'^search_help/$', 'epa.views.search_help'),
    url(r'^help/$', 'epa.views.view_help'),
    url(r'^help/(?P<id>\d+)/$', 'epa.views.view_help'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^reset/$', 'epa.views.reset_password'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'epa.views.view_prediction_data')

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
