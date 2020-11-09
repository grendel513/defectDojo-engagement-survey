'''
Created on Feb 18, 2015

@author: jay7958
'''
from django.conf.urls import url
from django.contrib import admin
from django.apps import apps
from defectDojo_engagement_survey import views as ddeng_views
if not apps.ready:
    apps.get_models()

admin.autodiscover()

urlpatterns = [
    url(r'^survey$',
        ddeng_views.survey,
        name='survey'),
    url(r'^survey/create$',
        ddeng_views.create_survey,
        name='create_survey'),
    url(r'^survey/(?P<sid>\d+)/edit$',
        ddeng_views.edit_survey,
        name='edit_survey'),
    url(r'^survey/(?P<sid>\d+)/delete',
        ddeng_views.delete_survey,
        name='delete_survey'),
    url(r'^survey/(?P<sid>\d+)/edit/questions$',
        ddeng_views.edit_survey_questions,
        name='edit_survey_questions'),
    url(r'^questions$',
        ddeng_views.questions,
        name='questions'),
    url(r'^questions/add$',
        ddeng_views.create_question,
        name='create_question'),
    url(r'^questions/(?P<qid>\d+)/edit$',
        ddeng_views.edit_question,
        name='edit_question'),
    url(r'^choices/add$',
        ddeng_views.add_choices,
        name='add_choices'),
    url(r'^engagement/(?P<eid>\d+)/add_survey$',
        ddeng_views.add_survey,
        name='add_survey'),
    url(r'^engagement/(?P<eid>\d+)/survey/(?P<sid>\d+)/answer',
        ddeng_views.answer_survey,
        name='answer_survey'),
    url(r'^engagement/(?P<eid>\d+)/survey/(?P<sid>\d+)/delete',
        ddeng_views.delete_engagement_survey,
        name='delete_engagement_survey'),
    url(r'^engagement/(?P<eid>\d+)/survey/(?P<sid>\d+)$',
        ddeng_views.view_survey,
        name='view_survey'),
]
