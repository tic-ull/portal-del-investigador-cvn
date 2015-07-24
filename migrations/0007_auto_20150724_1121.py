# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cvn', '0006_auto_20150630_0852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cvn',
            name='status',
            field=models.IntegerField(verbose_name='Status', choices=[(0, b'Updated'), (1, b'Expired'), (2, b'Invalid Identity')]),
            preserve_default=True,
        ),
    ]
