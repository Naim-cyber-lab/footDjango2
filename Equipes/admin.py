from django.contrib import admin

from Equipes.models import *
# Register your models here.

@admin.register(CoachParams)
class CoachParamsAdmin(admin.ModelAdmin):
    pass

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass

@admin.register(GameModel)
class GameModelAdmin(admin.ModelAdmin):
    pass

