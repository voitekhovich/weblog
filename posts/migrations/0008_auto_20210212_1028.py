# Generated by Django 2.2.9 on 2021-02-12 10:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20210211_0823'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('pub_date',)},
        ),
    ]
