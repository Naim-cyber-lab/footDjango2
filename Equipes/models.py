from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    attendance = models.CharField(max_length=256)
    teamName = models.CharField(max_length=256)


    #utilisateur = models.ManyToManyField(CoachParams,related_name='team', blank=True)


class CoachParams(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    currentTeam = models.ForeignKey(Team, on_delete=models.CASCADE)
    team = models.ManyToManyField(Team,related_name="coachParams",blank=True)
    fenetre = models.IntegerField()
    nbMatch = models.IntegerField()
    tolerance = models.IntegerField()


class Player(models.Model):
    lastName = models.CharField(max_length=256)
    firstName = models.CharField(max_length=256)
    heigth = models.IntegerField()
    weight = models.IntegerField()
    VMA = models.IntegerField()
    placeOnField = models.CharField(max_length=256)
    globalScore = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    birth = models.DateField()

class GameModel(models.Model):
    nameGame = models.CharField(max_length=255)
    offLineYes = models.BooleanField(default=False)
    offLineNo = models.BooleanField(default=False)
    goalKeeperYes = models.BooleanField(default=False)
    goalKeeperNo = models.BooleanField(default=False)
    synthetiqueDry = models.BooleanField(default=False)
    synthetiqueWet = models.BooleanField(default=False)
    stabiliseDry = models.BooleanField(default=False)
    stabiliseWet = models.BooleanField(default=False)
    grassDry = models.BooleanField(default=False)
    grassWet = models.BooleanField(default=False)
    otherField = models.BooleanField(default=False)
    goal11 = models.BooleanField(default=False)
    goal7 = models.BooleanField(default=False)
    goalSmall = models.BooleanField(default=False)
    goalEmbut = models.BooleanField(default=False)
    goalNone = models.BooleanField(default=False)
    goalOther = models.BooleanField(default=False)
    TB1_3= models.BooleanField(default=False) # Peut faire entre 1 et 3 touchés de balle
    TB_2 = models.BooleanField(default=False) # Peut faire exactement 2 touchés de balle
    TB_free = models.BooleanField(default=False) # Libre dans les touchés de balle
    #game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    DimensionGrand = models.BooleanField(default=False)
    DimensionMoyen = models.BooleanField(default=False)
    DimensionPetit = models.BooleanField(default=False)
    

class Game(models.Model):
    nameGame = models.CharField(max_length=255)
    numberGroups = models.IntegerField()
    dateGame = models.DateField(auto_now_add=True)
    completed = models.IntegerField(default=0)
    gameModel = models.ForeignKey(GameModel, on_delete=models.CASCADE, null=True)


class Group(models.Model):
    ranking = models.IntegerField()
    player = models.ManyToManyField(Player, related_name="groups", blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    





