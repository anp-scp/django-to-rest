# Generated by Django 4.0.5 on 2022-07-31 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_basics', '0006_studentwithfiltersetclassvsfiltersetfield'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentWithCustomMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('year', models.IntegerField()),
            ],
        ),
    ]