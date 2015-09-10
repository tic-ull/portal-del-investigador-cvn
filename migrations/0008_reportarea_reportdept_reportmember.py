# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150319_0929'),
        ('cvn', '0007_auto_20150724_1121'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, verbose_name='Code')),
                ('name', models.TextField(null=True, verbose_name='Name', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReportDept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16, verbose_name='Code')),
                ('name', models.TextField(null=True, verbose_name='Name', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReportMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cce', models.TextField(verbose_name='CCE Name', blank=True)),
                ('area', models.ForeignKey(to='cvn.ReportArea', null=True)),
                ('department', models.ForeignKey(to='cvn.ReportDept', null=True)),
                ('user_profile', models.OneToOneField(to='core.UserProfile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
