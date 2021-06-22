# Generated by Django 3.2.3 on 2021-05-28 14:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Equipes', '0010_rename_utilisateur_userinformations'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoachParams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='team',
            name='utilisateur',
        ),
        migrations.AddField(
            model_name='team',
            name='attendance',
            field=models.CharField(default=None, max_length=256),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='UserInformations',
        ),
        migrations.AddField(
            model_name='coachparams',
            name='currentTeam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Equipes.team'),
        ),
        migrations.AddField(
            model_name='coachparams',
            name='team',
            field=models.ManyToManyField(blank=True, related_name='utilisateur', to='Equipes.Team'),
        ),
        migrations.AddField(
            model_name='coachparams',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
