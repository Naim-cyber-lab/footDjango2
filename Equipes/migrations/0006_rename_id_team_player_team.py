# Generated by Django 3.2.3 on 2021-05-26 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Equipes', '0005_player'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='id_team',
            new_name='team',
        ),
    ]
