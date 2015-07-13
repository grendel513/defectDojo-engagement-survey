'''
Created on Feb 18, 2015

@author: jay7958
'''
import pickle
from crispy_forms.bootstrap import InlineRadios, InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.db.models import Count
from dojo.forms import MultipleSelectWithPop

from .models import Engagement_Survey, Answered_Survey, TextAnswer, ChoiceAnswer, Choice, Question, TextQuestion, \
    ChoiceQuestion


# List of validator_name:func_name
# Show in admin a multichoice list of validator names
# pass this to form using field_name='validator_name' ?
class QuestionForm(forms.Form):
    ''' Base class for a Question
    '''

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        # If true crispy-forms will render a <form>..</form> tags
        self.helper.form_tag = kwargs.get('form_tag', True)

        if 'form_tag' in kwargs:
            del kwargs['form_tag']

        self.answered_survey = kwargs.get('answered_survey')
        if not self.answered_survey:
            raise ValueError('Need an answered_survey to save answers too')

        del kwargs['answered_survey']

        self.helper.form_class = kwargs.get('form_class', '')

        self.question = kwargs.get('question')

        if not self.question:
            raise ValueError('Need a question to render')

        del kwargs['question']
        super(QuestionForm, self).__init__(*args, **kwargs)


class TextQuestionForm(QuestionForm):
    def __init__(self, *args, **kwargs):
        super(TextQuestionForm, self).__init__(*args, **kwargs)

        # work out initial data

        initial_answer = TextAnswer.objects.filter(
            answered_survey=self.answered_survey,
            question=self.question
        )

        if initial_answer.exists():
            initial_answer = initial_answer[0].answer
        else:
            initial_answer = ''

        self.fields['answer'] = forms.CharField(
            label=self.question.text,
            widget=forms.Textarea(),
            required=not self.question.optional,
            initial=initial_answer,
        )

        answer = self.fields['answer']

    def save(self):
        if not self.is_valid():
            raise forms.ValidationError('form is not valid')

        answer = self.cleaned_data.get('answer')

        if not answer:
            if self.fields['answer'].required:
                raise forms.ValidationError, 'Required'
            return

        text_answer, created = TextAnswer.objects.get_or_create(
            answered_survey=self.answered_survey,
            question=self.question,
        )

        if created:
            text_answer.answered_survey = self.answered_survey
        text_answer.answer = answer
        text_answer.save()


class ChoiceQuestionForm(QuestionForm):
    def __init__(self, *args, **kwargs):
        super(ChoiceQuestionForm, self).__init__(*args, **kwargs)

        choices = [(c.id, c.label) for c in self.question.choices.all()]

        # initial values

        initial_choices = []
        choice_answer = ChoiceAnswer.objects.filter(
            answered_survey=self.answered_survey,
            question=self.question,
        ).annotate(a=Count('answer')).filter(a__gt=0)

        # we have ChoiceAnswer instance
        if choice_answer:
            choice_answer = choice_answer[0]
            initial_choices = choice_answer.answer.all().values_list('id',
                                                                     flat=True)
            if self.question.multichoice is False:
                initial_choices = initial_choices[0]

        # default classes
        widget = forms.RadioSelect
        field_type = forms.ChoiceField
        inline_type = InlineRadios

        if self.question.multichoice:
            field_type = forms.MultipleChoiceField
            widget = forms.CheckboxSelectMultiple
            inline_type = InlineCheckboxes

        field = field_type(
            label=self.question.text,
            required=not self.question.optional,
            choices=choices,
            initial=initial_choices,
            widget=widget
        )

        self.fields['answer'] = field

        # Render choice buttons inline
        self.helper.layout = Layout(
            inline_type('answer')
        )

    def clean_answer(self):
        real_answer = self.cleaned_data.get('answer')

        # for single choice questions, the selected answer is a single string
        if type(real_answer) is not list:
            real_answer = [real_answer]
        return real_answer

    def save(self):
        if not self.is_valid():
            raise forms.ValidationError('Form is not valid')

        real_answer = self.cleaned_data.get('answer')

        if not real_answer:
            if self.fields['answer'].required:
                raise forms.ValidationError, 'Required'
            return

        choices = Choice.objects.filter(id__in=real_answer)

        # find ChoiceAnswer and filter in answer !
        choice_answer = ChoiceAnswer.objects.filter(
            answered_survey=self.answered_survey,
            question=self.question,
        )

        # we have ChoiceAnswer instance
        if choice_answer:
            choice_answer = choice_answer[0]

        if not choice_answer:
            # create a ChoiceAnswer
            choice_answer = ChoiceAnswer.objects.create(
                answered_survey=self.answered_survey,
                question=self.question
            )

        # re save out the choices
        choice_answer.answered_survey = self.answered_survey
        choice_answer.answer = choices
        choice_answer.save()


class Add_Survey_Form(forms.ModelForm):
    survey = forms.ModelChoiceField(
        queryset=Engagement_Survey.objects.all(),
        required=True,
        widget=forms.widgets.Select(),
        help_text='Select the Survey to add.')

    class Meta:
        model = Answered_Survey
        exclude = ('responder',
                   'completed',
                   'engagement',
                   'answered_on')


class Delete_Survey_Form(forms.ModelForm):
    id = forms.IntegerField(required=True,
                            widget=forms.widgets.HiddenInput())

    class Meta:
        model = Answered_Survey
        exclude = ('responder',
                   'completed',
                   'engagement',
                   'answered_on',
                   'survey')


class Delete_Eng_Survey_Form(forms.ModelForm):
    id = forms.IntegerField(required=True,
                            widget=forms.widgets.HiddenInput())

    class Meta:
        model = Engagement_Survey
        exclude = ('name',
                   'questions',
                   'description',
                   'active')


class CreateSurveyForm(forms.ModelForm):
    class Meta:
        model = Engagement_Survey
        exclude = ['questions']


class EditSurveyQuestionsForm(forms.ModelForm):
    questions = forms.ModelMultipleChoiceField(
        Question.objects.all(),
        required=True,
        help_text="Select questions to include on this survey.  Field can be used to search available questions.",
        widget=MultipleSelectWithPop(attrs={'size': '11'}))

    class Meta:
        model = Engagement_Survey
        exclude = ['name', 'description', 'active']


class CreateQuestionForm(forms.Form):
    type = forms.ChoiceField(choices=(("---", "-----"), ("text", "Text"), ("choice", "Choice")))
    order = forms.IntegerField(min_value=1, widget=forms.TextInput(attrs={'data-type': 'both'}))
    optional = forms.BooleanField(help_text="If selected, user doesn't have to answer this question",
                                  initial=False,
                                  required=False,
                                  widget=forms.CheckboxInput(attrs={'data-type': 'both'}))


class CreateTextQuestionForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'data-type': 'text'}),
                           label="Question Text",
                           help_text="The actual question.")

    class Meta:
        model = TextQuestion
        exclude = ['order', 'optional']


class MultiWidgetBasic(forms.widgets.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [forms.TextInput(attrs={'data-type': 'choice'}),
                   forms.TextInput(attrs={'data-type': 'choice'}),
                   forms.TextInput(attrs={'data-type': 'choice'}),
                   forms.TextInput(attrs={'data-type': 'choice'}),
                   forms.TextInput(attrs={'data-type': 'choice'}),
                   forms.TextInput(attrs={'data-type': 'choice'})]
        super(MultiWidgetBasic, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return pickle.loads(value)
        else:
            return [None, None, None, None, None, None]

    def format_output(self, rendered_widgets):
        return '<br/>'.join(rendered_widgets)


class MultiExampleField(forms.fields.MultiValueField):
    widget = MultiWidgetBasic

    def __init__(self, *args, **kwargs):
        list_fields = [forms.fields.CharField(required=True),
                       forms.fields.CharField(required=True),
                       forms.fields.CharField(required=False),
                       forms.fields.CharField(required=False),
                       forms.fields.CharField(required=False),
                       forms.fields.CharField(required=False)]
        super(MultiExampleField, self).__init__(list_fields, *args, **kwargs)

    def compress(self, values):
        return pickle.dumps(values)


class CreateChoiceQuestionForm(forms.Form):
    c_text = forms.CharField(widget=forms.Textarea(attrs={'data-type': 'choice'}),
                             label="Question Text",
                             help_text="The actual question.")
    multichoice = forms.BooleanField(required=False,
                                     initial=False,
                                     widget=forms.CheckboxInput(attrs={'data-type': 'choice'}),
                                     help_text="Can more than one choice can be selected?")

    answer_choices = MultiExampleField(required=False, widget=MultiWidgetBasic(attrs={'data-type': 'choice'}))

    class Meta:
        model = ChoiceQuestion
        exclude = ['order', 'optional', 'choices']


class EditQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = []


class EditTextQuestionForm(EditQuestionForm):
    class Meta:
        model = TextQuestion
        exclude = []


class EditChoiceQuestionForm(EditQuestionForm):
    choices = forms.ModelMultipleChoiceField(
        Choice.objects.all(),
        required=True,
        help_text="Select choices to include on this question.  Field can be used to search available choices.",
        widget=MultipleSelectWithPop(attrs={'size': '11'}))

    class Meta:
        model = ChoiceQuestion
        exclude = []


class AddChoicesForm(forms.ModelForm):
    class Meta:
        model = Choice
        exclude = []
