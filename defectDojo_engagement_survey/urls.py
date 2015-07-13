'''
Created on Feb 18, 2015

@author: jay7958
'''
from django.conf.urls import patterns, url
from django.contrib import admin
from django.db.models.loading import cache as model_cache

if not model_cache.ready:
    model_cache.get_models()

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^survey$',
        'defectDojo_engagement_survey.views.survey',
        name='survey'),
    url(r'^survey/create$',
        'defectDojo_engagement_survey.views.create_survey',
        name='create_survey'),
    url(r'^survey/(?P<sid>\d+)/edit$',
        'defectDojo_engagement_survey.views.edit_survey',
        name='edit_survey'),
    url(r'^survey/(?P<sid>\d+)/delete',
        'defectDojo_engagement_survey.views.delete_survey',
        name='delete_survey'),
    url(r'^survey/(?P<sid>\d+)/edit/questions$',
        'defectDojo_engagement_survey.views.edit_survey_questions',
        name='edit_survey_questions'),
    url(r'^questions$',
        'defectDojo_engagement_survey.views.questions',
        name='questions'),
    url(r'^questions/add$',
        'defectDojo_engagement_survey.views.create_question',
        name='create_question'),
    url(r'^questions/(?P<qid>\d+)/edit$',
        'defectDojo_engagement_survey.views.edit_question',
        name='edit_question'),
    url(r'^choices/add$',
        'defectDojo_engagement_survey.views.add_choices',
        name='add_choices'),
    url(r'^engagement/(?P<eid>\d+)/add_survey$',
        'defectDojo_engagement_survey.views.add_survey',
        name='add_survey'),
    url(r'^engagement/(?P<eid>\d+)/survey/(?P<sid>\d+)/answer',
        'defectDojo_engagement_survey.views.answer_survey',
        name='answer_survey'),
    url(r'^engagement/(?P<eid>\d+)/survey/(?P<sid>\d+)/delete',
        'defectDojo_engagement_survey.views.delete_survey',
        name='delete_survey'),
    url(r'^engagement/(?P<eid>\d+)/survey/(?P<sid>\d+)$',
        'defectDojo_engagement_survey.views.view_survey',
        name='view_survey'),
)
