from django.conf.urls import patterns, url
#from django.core.urlresolvers import reverse


urlpatterns = patterns('',

    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name':'auth/login.html'},
        name='login'),
                       
    url(r'^logout/$', 'auth.views.logout_view', name='logout'),
    url(r'^register/$', 'auth.views.register', name='register'),
    url(r'^change_password/$', 'auth.views.change_password',
        name='change_password'), 
)
