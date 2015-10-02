from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, include, url

js_info_dict = {
    'packages': ('tilejetserver.proxy',),
}

urlpatterns = patterns('tilejetserver.proxy.views',
    url(r'^proxy/', 'proxy')
)
