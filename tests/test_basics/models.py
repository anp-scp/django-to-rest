from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from to_rest.decorators import restifyModel

def is_valid_year(value):
    if value not in [1,2,3,4]:
        raise ValidationError(_('%(value)s is not correct year'), params={'value': value})

@restifyModel
class Student(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField(validators=[is_valid_year])
    
    def __str__(self):
        return "[name={}, year={}]".format(self.name, self.year)

@restifyModel(customViewParams='CustomSerializer')
class StudentWithCustomSerializer(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)

@restifyModel(customViewParams='CustomAuthAndPermission')
class StudentWithCustomAuthAndPermission(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)

@restifyModel(customViewParams='CustomThrottling')
class StudentWithCustomThrottling(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)

@restifyModel(customViewParams='CustomFiltering')
class StudentWithCustomFiltering(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    discipline = models.CharField(max_length=20)
    
    def __str__(self):
        return "[name={}]".format(self.name)

@restifyModel(customViewParams='CustomFiltering1')
class StudentWithFilterSetClassVSFilterSetField(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    discipline = models.CharField(max_length=20)
    
    def __str__(self):
        return "[name={}]".format(self.name)

@restifyModel(customViewParams='CustomListMethod')
class StudentWithCustomMethod(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    
    def __str__(self):
        return "[name={}]".format(self.name)

@restifyModel(customViewParams='CustomAction')
class StudentWithCustomAction(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    
    def __str__(self):
        return "[name={}]".format(self.name)