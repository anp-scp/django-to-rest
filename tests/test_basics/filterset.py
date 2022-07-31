import django_filters
from test_basics.models import StudentWithFilterSetClassVSFilterSetField

class StudentWithFilterSetClassVSFilterSetFieldFilter(django_filters.FilterSet):
    class Meta:
        model = StudentWithFilterSetClassVSFilterSetField
        fields = ['year', 'discipline']
