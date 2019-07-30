# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OrderAndVisit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospital',
            name='img',
            field=models.ImageField(verbose_name='图片', upload_to='static/img/hosinfo/'),
        ),
    ]
