from django.db import models
from to_rest.decorators import restifyModel

# Create your models here.
@restifyModel
class Student(models.Model):
    name = models.CharField(max_length=75)
    discipline = models.CharField(max_length=10)
    program = models.CharField(max_length=10)

    def __str__(self):
        return "[name={} ; discipline={} ; program={}]".format(self.name, self.discipline, self.program)

@restifyModel
class System(models.Model):
    name = models.CharField(max_length=75)
    location = models.CharField(max_length=20)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)

    def __str__(self):
        return "[name={} ; location={}]".format(self.name, self.location)

@restifyModel
class Student1(models.Model):
    name = models.CharField(max_length=75)
    discipline = models.CharField(max_length=10)
    program = models.CharField(max_length=10)

    def __str__(self):
        return "[name={} ; discipline={} ; program={}]".format(self.name, self.discipline, self.program)

@restifyModel
class System1(models.Model):
    name = models.CharField(max_length=75)
    location = models.CharField(max_length=20)
    student = models.OneToOneField(Student1, models.CASCADE, null=True)

    def __str__(self):
        return "[name={} ; location={}]".format(self.name, self.location)
