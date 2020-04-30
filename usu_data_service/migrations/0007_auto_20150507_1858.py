# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import usu_data_service.models


class Migration(migrations.Migration):

    dependencies = [
        ('usu_data_service', '0006_auto_20150507_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfile',
            name='file',
            field=models.FileField(upload_to=usu_data_service.models.get_upload_path),
        ),
    ]
