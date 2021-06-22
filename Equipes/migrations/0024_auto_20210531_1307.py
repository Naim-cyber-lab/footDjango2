# Generated by Django 3.2.3 on 2021-05-31 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Equipes', '0023_auto_20210531_1227'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='gameModel',
        ),
        migrations.AddField(
            model_name='gamemodel',
            name='model',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Equipes.game'),
        ),
    ]
