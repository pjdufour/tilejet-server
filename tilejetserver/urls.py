from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import tilejetserver.proxy.urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ittc.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

if 'tilejetserver.cache' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^cache/', include('tilejetserver.cache.urls')),
    )

if 'tilejetserver.proxy' in settings.INSTALLED_APPS:
    urlpatterns += tilejetserver.proxy.urls.urlpatterns
