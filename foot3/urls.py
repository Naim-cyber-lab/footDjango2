from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include


from . import views 


urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^NouveauMatch/$', views.NouveauMatch),
    url(r'^NouveauMatch/CaracteristiqueMatch/nbPlayer=(?P<nbPlayer>[0-9])$', views.NouveauMatchCaracteristiqueMatch),
    url(r'^NouveauMatch/CaracteristiqueMatch/EquipesClassement/numberGroups=(?P<numberGroups>[0-9]+)/nameGame=(?P<nameGame>[a-zA-Z0-9]+)/$', views.NouveauMatchCaracteristiqueMatchEquipeClassement),
    url(r'^FeedbackJeux/$', views.FeedbackJeux),
    url(r'^FeedbackJeux/idGame=(?P<idGame>[0-9]+)', views.FeedbackJeuxBase), #on va mettre un parametre nomme pour pouvoir traiter l'enregistrement du jeu
    url(r'^StatistiqueGame/$', views.StatistiqueGame),
    url(r'^HistoriqueJeu/$', views.HistoriqueJeu),
    url(r'^Assiduite/$', views.Assiduite),
    url(r'GraphEquipe/$',views.GraphEquipe),
    url(r'StatGliss/$',views.StatGliss),
    url(r'^StatistiqueGame/idTeam=(?P<idTeam>[0-9]+)', views.FeedbackJeuxBaseTeam),
    url(r'register/', include('register.urls')),
    url(r'Equipes/', include('Equipes.urls')),
]
