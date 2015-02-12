from django.conf.urls import patterns, url

__author__ = 'alfred'


user_urlpatterns = patterns('',
                            url(r'^login/?$', 'users.views.login'),
                            url(r'^logout/?$', 'users.views.logout'),
                            url(r'^me/?$', 'users.views.about_me'))

rest_user_urlpatterns = patterns('',
                                 url(r'^login/?$', 'users.views.rest_login'),
                                 url(r'^logout/?$', 'users.views.rest_logout'),
                                 url(r'^me/?$', 'users.views.rest_about_me'))
