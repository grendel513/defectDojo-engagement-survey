from django.utils.translation import ugettext_lazy as _
from django.utils import six
from django_filters import FilterSet, CharFilter, BooleanFilter, ChoiceFilter

from .models import Engagement_Survey, Question


class SurveyFilter(FilterSet):
    name = CharFilter(lookup_type='icontains')
    description = CharFilter(lookup_type='icontains')
    active = BooleanFilter()

    class Meta:
        model = Engagement_Survey
        exclude = ['questions']


class QuestionTypeFilter(ChoiceFilter):
    def any(self, qs, name):
        return qs.all()

    def text_question(self, qs, name):
        return qs.filter(**{
            'polymorphic_ctype__name': 'text question',
        })

    def choice_question(self, qs, name):
        return qs.filter(**{
            'polymorphic_ctype__name': 'choice question',
        })

    options = {
        '': (_('Any'), any),
        1: (_('Text Question'), text_question),
        2: (_('Choice Question'), choice_question),
    }

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [
            (key, value[0]) for key, value in six.iteritems(self.options)]
        super(QuestionTypeFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = ''
        return self.options[value][1](self, qs, self.name)


class QuestionFilter(FilterSet):
    text = CharFilter(lookup_type='icontains')
    type = QuestionTypeFilter()

    class Meta:
        model = Question
        exclude = ['polymorphic_ctype', 'created', 'modified', 'order']
