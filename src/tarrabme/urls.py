from django.conf.urls import patterns, include, url
from django.contrib import admin
from tickets.urls import ticket_code_urlpatterns, rest_ticket_code_urlpatterns
from users.urls import user_urlpatterns, rest_user_urlpatterns


resturlpatterns = patterns(r'^api/',
                           url(r'^accounts/', include(rest_user_urlpatterns)),
                           url(r'^', include(rest_ticket_code_urlpatterns)))


urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^codes/', include(ticket_code_urlpatterns)),
                       url(r'^users/', include(user_urlpatterns)),
                       url(r'^rest/', include(resturlpatterns)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')))
