'''
Created on Feb 16, 2015

@author: jay7958
'''
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.models import TimeStampedModel
from polymorphic import PolymorphicModel

from dojo.models import Engagement


class Question(PolymorphicModel, TimeStampedModel):
    '''
        Represents a question.
    '''

    class Meta:
        ordering = ['order']

    order = models.PositiveIntegerField(default=1,
                                        help_text='The render order')

    optional = models.BooleanField(
        default=False,
        help_text="If selected, user doesn't have to answer this question")

    text = models.TextField(blank=False, help_text='The question text')

    def __unicode__(self):
        return self.text


class TextQuestion(Question):
    '''
    Question with a text answer
    '''

    def get_form(self):
        '''
        Returns the form for this model
        '''
        from forms import TextQuestionForm
        return TextQuestionForm


class Choice(TimeStampedModel):
    '''
    Model to store the choices for multi choice questions
    '''

    order = models.PositiveIntegerField(default=1)

    label = models.TextField(default="")

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.label


class ChoiceQuestion(Question):
    '''
    Question with answers that are chosen from a list of choices defined
    by the user.
    '''

    multichoice = models.BooleanField(default=False,
                                      help_text="Select one or more")

    choices = models.ManyToManyField(Choice)

    def get_form(self):
        '''
        Returns the form for this model
        '''

        from forms import ChoiceQuestionForm
        return ChoiceQuestionForm


class Answer(PolymorphicModel, TimeStampedModel):
    ''' Base Answer model
    '''
    question = models.ForeignKey(Question)

#     content_type = models.ForeignKey(ContentType)
#     object_id = models.PositiveIntegerField()
#     content_object = generic.GenericForeignKey('content_type', 'object_id')
    answered_survey = models.ForeignKey('Answered_Survey',
                                        null=False,
                                        blank=False)


class TextAnswer(Answer):
    answer = models.TextField(
        blank=False,
        help_text='The answer text')

    def __unicode__(self):
        return self.answer


class ChoiceAnswer(Answer):
    answer = models.ManyToManyField(
        Choice,
        help_text='The selected choices as the answer')

    def __unicode__(self):
        if len(self.answer.all()):
            return unicode(self.answer.all()[0])
        else:
            return 'No Response'


# meant to be a abstract survey, identified by name for purpose
class Engagement_Survey(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False,
                            editable=True)
    description = models.TextField(editable=True)
    questions = models.ManyToManyField(Question)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Engagement Survey"
        verbose_name_plural = "Engagement Surveys"

    def __unicode__(self):
        return self.name


# meant to be an answered survey tied to an engagement
class Answered_Survey(models.Model):
    # tie this to a specific engagement
    engagement = models.ForeignKey(Engagement, related_name='engagement',
                                   null=False, blank=False, editable=True)
    # what surveys have been answered
    survey = models.ForeignKey(Engagement_Survey)
    # who answered it
    responder = models.ForeignKey(User, related_name='responder',
                                  null=True, blank=True, editable=True,
                                  default=None)
    completed = models.BooleanField(default=False)
    answered_on = models.DateField(null=True)

    class Meta:
        verbose_name = "Answered Engagement Survey"
        verbose_name_plural = "Answered Engagement Surveys"

    def __unicode__(self):
        return self.survey.name
