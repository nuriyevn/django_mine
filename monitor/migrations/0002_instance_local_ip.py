# Generated by Django 3.2.9 on 2021-11-29 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='local_ip',
            field=models.TextField(default='192.168.1.1'),
            preserve_default=False,
        ),
    ]