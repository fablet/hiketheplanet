# -*- coding: utf-8 -*-

from django import forms
from django.db import models

from factory.fuzzy import FuzzyText


class TestParentModel(models.Model):
    foo = models.CharField(max_length=15, default=FuzzyText(length=5))

    class Meta:
        app_label = 'mixins'


class TestChildModel(models.Model):
    foo = models.ForeignKey(TestParentModel)
    bar = models.CharField(max_length=15, default=FuzzyText(length=5))

    class Meta:
        app_label = 'mixins'


class TestParentForm(forms.ModelForm):

    class Meta:
        model = TestParentModel
        fields = ['foo']


TestChildFormset = forms.inlineformset_factory(TestParentModel, TestChildModel,
                                               fields=('bar',))
