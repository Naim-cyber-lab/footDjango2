
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include #, handler404

from . import views  #on importe tous ce qu'on a mis dans le module views

urlpatterns = [
    #url(r'^$', views.JoueursCree), #On considere ici que l'url commence par Equipes
    url(r'^ListesEquipes/$', views.ListesEquipes),
        url(r'^JoueursCree/$', views.JoueursCree),
        url(r'^StatistiqueEquipe/$', views.StatistiqueEquipe),
        url(r'^Joueur1/$', views.Joueur1),
        url(r'^Assiduite/$', views.Assiduite),
        url(r'ParamEquipe/$',views.ParamEquipe),
        url(r'^Joueur2/idPlayer=(?P<idPlayer>[0-9]+)', views.Joueur2),

 ]
