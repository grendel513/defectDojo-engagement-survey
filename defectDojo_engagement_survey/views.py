'''
Created on Feb 18, 2015

@author: jay7958
'''
from datetime import date
import pickle

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.html import escape
from pytz import timezone

from defectDojo_engagement_survey.models import Question
from defectDojo_engagement_survey.filters import SurveyFilter, QuestionFilter
from dojo.models import Engagement
from dojo.views import get_breadcrumbs, get_page_items
from .forms import Add_Survey_Form, Delete_Survey_Form, CreateSurveyForm, Delete_Eng_Survey_Form, \
    EditSurveyQuestionsForm, CreateQuestionForm, TextQuestionForm, ChoiceQuestionForm, CreateTextQuestionForm, \
    CreateChoiceQuestionForm, QuestionForm, EditTextQuestionForm, EditChoiceQuestionForm, AddChoicesForm
from .models import Answered_Survey, Engagement_Survey, Answer, TextQuestion, ChoiceQuestion, Choice

localtz = timezone('America/Chicago')


@user_passes_test(lambda u: u.is_staff)
def delete_engagement_survey(request, eid, sid):
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


@user_passes_test(lambda u: u.is_staff)
def edit_survey(request, sid):
    survey = get_object_or_404(Engagement_Survey, id=sid)
    old_name = survey.name
    old_desc = survey.description
    old_active = survey.active

    form = CreateSurveyForm(instance=survey)
    answered = Answered_Survey.objects.filter(survey=survey)
    if len(answered) > 0:
        messages.add_message(request,
                             messages.ERROR,
                             'This survey already has answered instances. If you change it, the responses may no longer'
                             ' be valid.',
                             extra_tags='alert-info')

    if request.method == 'POST':
        form = CreateSurveyForm(request.POST, instance=survey)
        if form.is_valid():
            if survey.name != old_name or \
                            survey.description != old_desc or \
                            survey.active != old_active:
                survey = form.save()

                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Survey successfully updated, you may now add/edit questions.',
                                     extra_tags='alert-success')
            else:
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'No changes detected, survey not updated.',
                                     extra_tags='alert-warning')
            if 'add_questions' in request.POST:
                return HttpResponseRedirect(reverse('edit_survey_questions', args=(survey.id,)))
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Please correct any errors displayed below.',
                                 extra_tags='alert-danger')

    return render(request, 'defectDojo-engagement-survey/create_survey.html',
                  {"survey": survey,
                   "form": form,
                   "name": "Edit Survey",
                   'breadcrumbs': get_breadcrumbs(title="Edit Survey", user=request.user)})


@user_passes_test(lambda u: u.is_staff)
def delete_survey(request, sid):
    survey = get_object_or_404(Engagement_Survey, id=sid)
    form = Delete_Eng_Survey_Form(instance=survey)

    from django.contrib.admin.util import NestedObjects
    from django.db import DEFAULT_DB_ALIAS

    collector = NestedObjects(using=DEFAULT_DB_ALIAS)
    collector.collect([survey])
    rels = collector.nested()

    if request.method == 'POST':
        if 'id' in request.POST and str(survey.id) == request.POST['id']:
            form = Delete_Eng_Survey_Form(request.POST, instance=survey)
            if form.is_valid():
                survey.delete()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Survey and relationships removed.',
                                     extra_tags='alert-success')
                return HttpResponseRedirect(reverse('survey'))

    return render(request, 'defectDojo-engagement-survey/delete_survey.html',
                  {'survey': survey,
                   'form': form,
                   'rels': rels,
                   'breadcrumbs': get_breadcrumbs(title="Delete Survey " + survey.name, user=request.user)})


@user_passes_test(lambda u: u.is_staff)
def create_survey(request):
    form = CreateSurveyForm()
    survey = None

    if request.method == 'POST':
        form = CreateSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save()

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Survey successfully created, you may now add questions.',
                                 extra_tags='alert-success')
            if 'add_questions' in request.POST:
                return HttpResponseRedirect(reverse('edit_survey_questions', args=(survey.id,)))
            else:
                return HttpResponseRedirect(reverse('edit_survey', args=(survey.id,)))
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Please correct any errors displayed below.',
                                 extra_tags='alert-danger')

    return render(request, 'defectDojo-engagement-survey/create_survey.html',
                  {"survey": survey,
                   "form": form,
                   "name": "Create Survey",
                   'breadcrumbs': get_breadcrumbs(title="Create Survey", user=request.user)})


@user_passes_test(lambda u: u.is_staff)
def edit_survey_questions(request, sid):
    survey = get_object_or_404(Engagement_Survey, id=sid)

    answered_surveys = Answered_Survey.objects.filter(survey=survey)
    reverted = False

    form = EditSurveyQuestionsForm(instance=survey)

    if request.method == 'POST':
        form = EditSurveyQuestionsForm(request.POST, instance=survey)

        if form.is_valid():
            form.save()
            for answered_survey in answered_surveys:
                answered_survey.completed = False
                answered_survey.answered_on = None
                answered_survey.save()
                reverted = True

            if reverted:
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Answered surveys associated with this survey have been set to uncompleted.',
                                     extra_tags='alert-warning')
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Survey questions successfully saved.',
                                 extra_tags='alert-success')
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Survey questions not saved, please correct any errors displayed below.',
                                 extra_tags='alert-success')
    return render(request, 'defectDojo-engagement-survey/edit_survey_questions.html',
                  {"survey": survey,
                   "form": form,
                   "name": "Update Survey Questions",
                   'breadcrumbs': get_breadcrumbs(title="Update Survey Questions", user=request.user)})


@user_passes_test(lambda u: u.is_staff)
def survey(request):
    user = request.user
    surveys = Engagement_Survey.objects.all()
    surveys = SurveyFilter(request.GET, queryset=surveys)
    paged_surveys = get_page_items(request, surveys, 25)

    return render(request, 'defectDojo-engagement-survey/list_surveys.html',
                  {"surveys": paged_surveys,
                   "filtered": surveys,
                   "name": "All Surveys",
                   'breadcrumbs': get_breadcrumbs(title="All Surveys", user=user)})


@user_passes_test(lambda u: u.is_staff)
def questions(request):
    user = request.user
    questions = Question.objects.all()
    questions = QuestionFilter(request.GET, queryset=questions)
    paged_questions = get_page_items(request, questions, 25)

    return render(request, 'defectDojo-engagement-survey/list_questions.html',
                  {"questions": paged_questions,
                   "filtered": questions,
                   "name": "All Questions",
                   'breadcrumbs': get_breadcrumbs(title="All Questions", user=user)})


@user_passes_test(lambda u: u.is_staff)
def create_question(request):
    error = False
    form = CreateQuestionForm()
    textQuestionForm = CreateTextQuestionForm()
    choiceQuestionFrom = CreateChoiceQuestionForm()
    created_question = None

    if request.method == 'POST':
        form = CreateQuestionForm(request.POST)
        textQuestionForm = CreateTextQuestionForm(request.POST)
        choiceQuestionFrom = CreateChoiceQuestionForm(request.POST)

        if form.is_valid():
            type = form.cleaned_data['type']

            if type == 'text':

                if textQuestionForm.is_valid():
                    created_question = TextQuestion.objects.create(optional=form.cleaned_data['optional'],
                                                                   order=form.cleaned_data['order'],
                                                                   text=textQuestionForm.cleaned_data['text'])
                    messages.add_message(request,
                                         messages.SUCCESS,
                                         'Text Question added successfully.',
                                         extra_tags='alert-success')
                else:
                    error = True

            elif type == 'choice':

                if choiceQuestionFrom.is_valid():

                    created_question = ChoiceQuestion.objects.create(optional=form.cleaned_data['optional'],
                                                                     order=form.cleaned_data['order'],
                                                                     text=choiceQuestionFrom.cleaned_data['c_text'],
                                                                     multichoice=choiceQuestionFrom.cleaned_data[
                                                                         'multichoice'])

                    choices_to_process = pickle.loads(choiceQuestionFrom.cleaned_data['answer_choices'])

                    for c in choices_to_process:
                        if c is not None and len(c) > 0:
                            created_question.choices.add(Choice.objects.get_or_create(label=c)[0])

                    created_question.save()

                    messages.add_message(request,
                                         messages.SUCCESS,
                                         'Choice Question added successfully.',
                                         extra_tags='alert-success')
                else:
                    error = True

            if '_popup' in request.GET and not error:
                resp = '<script type="text/javascript">opener.dismissAddAnotherPopupDojo(window, "%s", "%s");</script>' \
                       % (escape(created_question._get_pk_val()), escape(created_question.text))
                resp += '<script type="text/javascript">window.close();</script>'
                return HttpResponse(resp)

    return render(request, 'defectDojo-engagement-survey/create_related_question.html', {
        'name': 'Add Question',
        'breadcrumbs': get_breadcrumbs(title="Add Question",
                                       user=request.user),
        'form': form,
        'textForm': textQuestionForm,
        'choiceForm': choiceQuestionFrom})


@user_passes_test(lambda u: u.is_staff)
def edit_question(request, qid):
    error = False

    question = get_object_or_404(Question, id=qid)
    survey = Engagement_Survey.objects.filter(questions__in=[question])
    reverted = False

    if survey is not None:
        answered = Answered_Survey.objects.filter(survey=survey)
        if len(answered) > 0:
            messages.add_message(request,
                                 messages.ERROR,
                                 'This question is part of an already answered survey. If you change it, the responses '
                                 'may no longer be valid.',
                                 extra_tags='alert-info')

    type = str(ContentType.objects.get_for_model(question))

    if type == 'text question':
        form = EditTextQuestionForm(instance=question)
    elif type == 'choice question':
        form = EditChoiceQuestionForm(instance=question)
    else:
        raise Http404()

    if request.method == 'POST':
        if type == 'text question':
            form = EditTextQuestionForm(request.POST, instance=question)
        elif type == 'choice question':
            form = EditChoiceQuestionForm(request.POST, instance=question)
        else:
            raise Http404()

        if form.is_valid():
            form.save()

            for answered_survey in answered:
                answered_survey.completed = False
                answered_survey.answered_on = None
                answered_survey.save()
                reverted = True

            if reverted:
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Answered surveys associated with this survey have been set to uncompleted.',
                                     extra_tags='alert-warning')

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Question updated successfully.',
                                 extra_tags='alert-success')

    return render(request, 'defectDojo-engagement-survey/edit_question.html', {
        'name': 'Edit Question',
        'question': question,
        'breadcrumbs': get_breadcrumbs(title="Edit Question",
                                       user=request.user),
        'form': form})


@user_passes_test(lambda u: u.is_staff)
def add_choices(request):
    form = AddChoicesForm()
    if request.method == 'POST':
        form = AddChoicesForm(request.POST)
        if form.is_valid():
            choice, created = Choice.objects.get_or_create(**form.cleaned_data)
            if created:
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Choice added successfully.',
                                     extra_tags='alert-success')
            if '_popup' in request.GET:
                resp = ''
                if created:
                    resp = '<script type="text/javascript">opener.dismissAddAnotherPopupDojo(window, "%s", "%s");</script>' \
                           % (escape(choice._get_pk_val()), escape(choice.label))
                resp += '<script type="text/javascript">window.close();</script>'
                return HttpResponse(resp)

    return render(request, 'defectDojo-engagement-survey/add_choices.html', {
        'name': 'Add Choice',
        'breadcrumbs': get_breadcrumbs(title="Add Choice",
                                       user=request.user),
        'form': form})
