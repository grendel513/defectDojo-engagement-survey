'''
Created on Feb 18, 2015

@author: jay7958
'''
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from pytz import timezone

from dojo.models import Engagement
from dojo.views import get_breadcrumbs

from .forms import Add_Survey_Form, Delete_Survey_Form
from .models import Answered_Survey, Engagement_Survey, Answer


localtz = timezone('America/Chicago')


@user_passes_test(lambda u: u.is_staff)
def delete_survey(request, eid, sid):
    engagement = get_object_or_404(Engagement, id=eid)
    survey = get_object_or_404(Answered_Survey, id=sid)

    questions = get_answered_questions(survey=survey, read_only=True)

    form = Delete_Survey_Form(instance=survey)

    if request.method == 'POST':
        form = Delete_Survey_Form(request.POST, instance=survey)
        if form.is_valid():
            answers = Answer.objects.filter(
                question__in=[
                    question.id for question in survey.survey.questions.all()],
                answered_survey=survey)
            for answer in answers:
                answer.delete()
            survey.delete()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Survey deleted successfully.',
                                 extra_tags='alert-success')
            return HttpResponseRedirect('/engagement/%s' % eid)
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Unable to delete survey.',
                                 extra_tags='alert-danger')
    return render(request, 'defectDojo-engagement-survey/delete_survey.html',
                  {'survey': survey,
                   'form': form,
                   'engagement': engagement,
                   'questions': questions,
                   'breadcrumbs': get_breadcrumbs(
                       obj=engagement,
                       title="Delete " + survey.survey.name + " Survey")
                   })


@user_passes_test(lambda u: u.is_staff)
def answer_survey(request, eid, sid):
    survey = get_object_or_404(Answered_Survey, id=sid)
    engagement = get_object_or_404(Engagement, id=eid)

    questions = get_answered_questions(survey=survey, read_only=False)

    if request.method == 'POST':
        questions = [
            q.get_form()(request.POST or None,
                         prefix=str(q.id),
                         answered_survey=survey,
                         question=q, form_tag=False)
            for q in survey.survey.questions.all()
            ]

        questions_are_valid = []

        for question in questions:
            valid = question.is_valid()
            questions_are_valid.append(valid)
            if valid:
                question.save()

        questions_are_valid = all(questions_are_valid)
        if questions_are_valid:
            survey.completed = True
            survey.responder = request.user
            survey.answered_on = date.today()
            survey.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Successfully answered, all answers valid.',
                                 extra_tags='alert-success')
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Survey has errors, please correct.',
                                 extra_tags='alert-danger')

    return render(request,
                  'defectDojo-engagement-survey/answer_survey.html',
                  {'survey': survey,
                   'engagement': engagement,
                   'questions': questions,
                   'breadcrumbs': get_breadcrumbs(
                       obj=engagement,
                       title=survey.survey.name + " Survey")
                   })


@user_passes_test(lambda u: u.is_staff)
def view_survey(request, eid, sid):
    survey = get_object_or_404(Answered_Survey, id=sid)
    engagement = get_object_or_404(Engagement, id=eid)

    questions = get_answered_questions(survey=survey, read_only=True)

    return render(request, 'defectDojo-engagement-survey/view_survey.html',
                  {'survey': survey,
                   'user': request.user,
                   'engagement': engagement,
                   'questions': questions,
                   'breadcrumbs': get_breadcrumbs(
                       obj=engagement,
                       title=survey.survey.name + " Survey Responses"),
                   'name': survey.survey.name + " Survey Responses"
                   })


def get_answered_questions(survey=None, read_only=False):
    if survey is None:
        return None

    questions = [q.get_form()(prefix=str(q.id),
                              answered_survey=survey,
                              question=q, form_tag=False)
                 for q in survey.survey.questions.all()
                 ]
    if read_only:
        for question in questions:
            question.fields['answer'].widget.attrs = {"readonly": "readonly",
                                                      "disabled": "disabled"}

    return questions


@user_passes_test(lambda u: u.is_staff)
def add_survey(request, eid):
    user = request.user
    engagement = get_object_or_404(Engagement, id=eid)
    ids = [survey.survey.id for survey in
           Answered_Survey.objects.filter(engagement=engagement)]
    surveys = Engagement_Survey.objects.exclude(
        id__in=ids)
    form = Add_Survey_Form()
    if request.method == 'POST':
        form = Add_Survey_Form(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.engagement = engagement
            survey.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Survey successfully added, answers pending.',
                                 extra_tags='alert-success')
            if 'respond_survey' in request.POST:
                return HttpResponseRedirect(
                    '/engagement/%s/survey/%s/answer' % (eid, survey.id))

            return HttpResponseRedirect('/engagement/%s' % eid)
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Survey could not be added.',
                                 extra_tags='alert-danger')
    form.fields["survey"].queryset = surveys
    return render(request, 'defectDojo-engagement-survey/add_survey.html',
                  {'surveys': surveys,
                   'user': user,
                   'form': form,
                   'engagement': engagement})
