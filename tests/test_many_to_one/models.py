from email.policy import default
from django.db import models
from django.utils import timezone
from to_rest.decorators import restifyModel

# Create your models here.
@restifyModel
class Question(models.Model):
    question_text = models.CharField(max_length=200)

    def pub_date_default():
        return timezone.now()

    pub_date = models.DateTimeField('date published', default=pub_date_default)

@restifyModel
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


@restifyModel(customViewParams='CustomPermission')
class Question1(models.Model):
    question_text = models.CharField(max_length=200)

    def pub_date_default():
        return timezone.now()

    pub_date = models.DateTimeField('date published', default=pub_date_default)

@restifyModel(customViewParams='CustomPermission')
class Choice1(models.Model):
    question = models.ForeignKey(Question1, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)