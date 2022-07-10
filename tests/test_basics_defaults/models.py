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
        return "[name={}]".format(self.name)

