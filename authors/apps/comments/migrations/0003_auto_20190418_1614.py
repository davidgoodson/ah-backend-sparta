# Generated by Django 2.2 on 2019-04-18 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_historicalcomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='article_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcomment',
            name='article_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]