from django.conf.urls import patterns, url, include
from rest_framework import routers
from tickets import views

__author__ = 'alfred'


ticket_code_urlpatterns = patterns('',
                                   url(r'^(?P<code>.*)/attempt/?$',
                                       views.attempt,
                                       name='ticketcode_attempt'))

router = routers.DefaultRouter()
router.register(r'codes', views.TicketCodeViewSet)
router.register(r'codes/(?P<code>.*)/attempts/?', views.TicketCodeAttemptViewSet)

rest_ticket_code_urlpatterns = [url(r'^', include(router.urls))]
