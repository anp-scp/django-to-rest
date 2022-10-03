from django.db import models
from to_rest.decorators import restifyModel

# Create your models here.
@restifyModel
class Student(models.Model):
    name = models.CharField(max_length=75)
    friends = models.ManyToManyField("self")

    def __str__(self):
        return self.name
@restifyModel
class Course(models.Model):
    name = models.CharField(max_length=75)
    student = models.ManyToManyField(Student)

    def __str__(self):
        return self.name

@restifyModel
class Student1(models.Model):
    name = models.CharField(max_length=75)
    friends = models.ManyToManyField("self")

    def __str__(self):
        return self.name
@restifyModel
class Course1(models.Model):
    name = models.CharField(max_length=75)
    student = models.ManyToManyField(Student1)

    def __str__(self):
        return self.name