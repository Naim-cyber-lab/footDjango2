from django.shortcuts import render
from django.contrib.auth import authenticate

from django.shortcuts import redirect

from Equipes.models import Player
from Equipes.models import Group
from Equipes.models import Game
from Equipes.models import GameModel
from Equipes.models import CoachParams

from django.contrib.auth.models import User
from django.db import models

import random
from statistics import mean, variance
from math import sqrt

from collections import Counter

import matplotlib.pyplot as plt
import base64
from io import BytesIO

import json

def FromRankingToScore(ranking : int)->int:
    if(ranking == 0):
        return 0
    if(ranking == 1000):
        return 54
    if(ranking == 2000):
        return 42
    if(ranking == 3000):
        return 36
    if(ranking == 4000):
        return 18
    if(ranking == 1100):
        return 48
    if(ranking == 1110):
        return 42
    if(ranking == 1111):
        return 36
    if(ranking == 2200):
        return 36
    if(ranking == 2220):
        return 30
    if(ranking == 3300):
        return 24
    if(ranking == 100):
        return 54
    if(ranking == 200):
        return 36
    if(ranking == 300):
        return 18
    if(ranking == 111):
        return 36
    if(ranking == 110):
        return 45
    if(ranking == 220):
        return 27
    if(ranking == 10):
        return 54
    if(ranking == 20):
        return 18
    if(ranking == 11):
        return 36

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer,format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x,y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(8,5))
    plt.title('Score global des joueurs')
    plt.plot(x,y)
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.tight_layout()
    graph=get_graph()
    return graph


def get_chartPie(x):
    plt.switch_backend('AGG')
    plt.figure(figsize=(8,5))
    plt.title('Score global des joueurs')
    plt.hist(x)
    plt.tight_layout()
    graph=get_graph()
    return graph
#graph = get_plot([str(x) for x in range(1,len(myFinalData[2])+1)[::-1]],myFinalData[2][::-1])
def get_multiple_plot(List,theUltimateData):
    plt.switch_backend('AGG')
    plt.figure(figsize=(8,5))
    plt.title('Stat equipe')
    Date = [str(x) for x in range(1,len(theUltimateData[List[0]])+1)][::-1]
    count = 0
    for idPlayer in List:
        try :
            Score = theUltimateData[idPlayer][::-1]
    
            plt.plot(Date,Score,label=Player.objects.get(id=idPlayer).firstName + Player.objects.get(id=idPlayer).lastName )
        except :
            pass
        count += 1

    plt.legend()
    plt.xticks(rotation=45)
    plt.xlabel(idPlayer)
    plt.ylabel('Score')
    plt.tight_layout()
    graph=get_graph()
    return graph

def  StatGliss(request,ParamIdPlayer):
    #D'abord on va essayer de faire une stat glissé sur le joueur id=1
    joueur = Player.objects.get(id=ParamIdPlayer)
    #Il faut filtrer les groupes associés aux joueurs
    n=10 # au lieu de 10 il faurda mettre n le nb de matchs total
    groups = Group.objects.filter(player=joueur)[0:n] 
    listRankingPlayer = [group.ranking for group in groups]


    idUser = request.user.id
    currentTeamId = CoachParams.objects.get(user=idUser).currentTeam.id

    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]

    idGroupList = sorted(Counter([ x.id for x in Group.objects.filter(player__in=idListPlayer)]))[::-1]

    idGameList = list(Counter([ x.game.id for x in Group.objects.filter(id__in=idGroupList)]).keys())[::-1][0:10]
    nbGroupList = [Game.objects.get(id=x).numberGroups for x in idGameList]


    L=[]
    count = 0
    for nb in nbGroupList:
        L.append(idGroupList[count:count+nb])
        count+=nb

    V=[]
    for listGroup in L:
        H=[]
        for group in listGroup:
            H.append([x.id for x in Player.objects.filter(groups=group)])
        V.append(H)

    U=[]
    for x in V:
        W=[]
        for y in x:
            W.extend(y)
        U.append(W)

    
    RankingGroups = []
    for listGroup in L:
        K=[Group.objects.get(id=group).ranking for group in listGroup]
        RankingGroups.append(K)


    dataScorePlayer = {}
    for IdPlayerTeam in idListPlayer:
        ListScorePlayerAbscence = []
        for index,ListIdPlayer in enumerate(U):
            if IdPlayerTeam in ListIdPlayer:
                pass   
            else:
                ListScorePlayerAbscence.append(index)

        ListScorePlayer = []
        for listIdPlayerDouble,listRank in zip(V,RankingGroups):
            for index,listIdPlayer in enumerate(listIdPlayerDouble):
                if IdPlayerTeam in listIdPlayer:
                    ListScorePlayer.append(listRank[index])
        
        for indexAbscence in ListScorePlayerAbscence:
            ListScorePlayer.insert(indexAbscence,0)
        dataScorePlayer[IdPlayerTeam] = ListScorePlayer

    finalDataScorePlayer = {}
    for cle,valeur in dataScorePlayer.items():
        finalDataScorePlayer[cle] = [FromRankingToScore(u) for u in valeur]

    myFinalData = {}
    for cle,valeur in finalDataScorePlayer.items():
        myFinalData[cle] = createStatGliss(valeur,3,1)

    
    return get_plot(range(1,len(myFinalData[ParamIdPlayer])+1),myFinalData[ParamIdPlayer])


def handleEquality(listAttendance,numberGroups):
    if(len(listAttendance) % int(numberGroups) == 0):
        return ([],listAttendance)
    elif(len(listAttendance) % int(numberGroups) == 1):
        listScore = [int(Player.objects.get(id=int(idPlayer)).globalScore) for idPlayer in listAttendance]
        data = {}
        for score,idPlayer in zip(listScore,listAttendance):
            data[idPlayer]=score
        dataSortedTuple = sorted(data.items(), key=lambda t: t[1]) #on trie le dictionnaire par valeurs de maniere croissante. On aura alors un tuple trié
        dataSorted = {}
        for idPlayer,score in dataSortedTuple:
            dataSorted[idPlayer] = score
        i=0
        listIdPlayer=[]
        listIdPlayerWait=[]
        for idPlayer,score in dataSorted.items():
            if(i==0):
                listIdPlayerWait.append(int(idPlayer))
            if(i!=0):
                listIdPlayer.append(idPlayer)
            i=i+1
        return (listIdPlayerWait,listIdPlayer)
    elif(len(listAttendance) % int(numberGroups) == 2):
        listScore = [int(Player.objects.get(id=int(idPlayer)).globalScore) for idPlayer in listAttendance]
        data = {}
        for score,idPlayer in sorted(zip(listScore,listAttendance)):
            data[idPlayer]=score
        dataSortedTuple = sorted(data.items(), key=lambda t: t[1]) #on trie le dictionnaire par valeurs de maniere croissante. On aura alors un tuple trié
        dataSorted = {}
        for idPlayer,score in dataSortedTuple:
            dataSorted[idPlayer] = score
        i=0
        listIdPlayer=[]
        listIdPlayerWait=[]
        for idPlayer,score in dataSorted.items():
            if(i<2):
                listIdPlayerWait.append(int(idPlayer))
            if(i>=2):
                listIdPlayer.append(idPlayer)
            i=i+1
        return (listIdPlayerWait,listIdPlayer)
    elif(len(listAttendance) % int(numberGroups) == 3):
        listScore = [int(Player.objects.get(id=int(idPlayer)).globalScore) for idPlayer in listAttendance]
        data = {}
        for score,idPlayer in zip(listScore,listAttendance):
            data[idPlayer]=score
        dataSortedTuple = sorted(data.items(), key=lambda t: t[1]) #on trie le dictionnaire par valeurs de maniere croissante. On aura alors un tuple trié
        dataSorted = {}
        for idPlayer,score in dataSortedTuple:
            dataSorted[idPlayer] = score
        i=0
        listIdPlayer=[]
        listIdPlayerWait=[]
        for idPlayer,score in dataSorted.items():
            if(i<3):
                listIdPlayerWait.append(int(idPlayer))
            if(i>=3):
                listIdPlayer.append(idPlayer)
            i=i+1
        return (listIdPlayerWait,listIdPlayer)
    else:
        return ([],listAttendance)


def scroreId(idPlayer)->int:#Prend en entré l'id d'un joueur et donne en sortie le score de ce joueuer
    return int(Player.objects.get(id=idPlayer).globalScore)


def nameId(idPlayer)->str:#Prend en entré l'id d'un joueur et donne en sortie le nom et prenom du joueur
    return str(str(Player.objects.get(id=idPlayer).firstName) +" "+ str(Player.objects.get(id=idPlayer).lastName))

# how to go through every attribute of my object ?
# model_instance._meta.get_fields()
def get_boolean_field_values(model_instance) -> list:
    if not model_instance:
        return None
    listTrueAttribute = []
    data = {}
    for field in model_instance._meta.get_fields():
        if isinstance(field, models.BooleanField):
            data[field.name] = getattr(model_instance, field.name)
            if getattr(model_instance, field.name):
                listTrueAttribute.append(field.name)  
    #return data
    return listTrueAttribute
# my_instance = MyModel.objects.get(id=1234)
# data = get_boolean_field_values(my_instance)

def searchScore(nameColumn,zipRankingNumberIdgameIdgamemodel) -> int: #Prend en paramètre la colonne (dans ModelGame) et nous donne en sortie le score associé à cette colonne. Pour simplifier la fonction en prend aussi le zipRankingNumberIdgameIdgamemodel qui permet d'avoir l'historique des jeux du joueur. L'id du joueur est donné dans le zip
    score = 0
    for rank,number,idGame,idGameModel in zipRankingNumberIdgameIdgamemodel: #A chaque itération on parcour un jeu
        if str(nameColumn) in list(idGameModel):
            if (number == 2): #Dans le cas de deux équipes
                if (rank==1):
                    score += 54
                if (rank == 2):
                    score += 18
                if(rank == 11):
                    score += 36
            if (number == 3): #Dans le cas de trois équipes
                if (rank==1):
                    score += 54
                if (rank == 2):
                    score += 36
                if (rank == 3):
                    score += 18
                if(rank == 111): # On est dans le cas de 1er / 1er / 1er
                    score += 36
                if(rank == 110): # On est dans le cas de 1er / 1er / 2eme
                    score += 45
                if(rank == 220): # On est dans le cas de 1er / 2eme / 2eme
                    score += 27 
            if (number == 4): #Dans le cas de deux équipes
                if (rank==1):
                    score += 54
                if (rank == 2):
                    score += 42
                if (rank == 3):
                    score += 30
                if (rank == 4):
                    score += 18
                if(rank == 1100): # On est dans le cas de 1/1/...
                    score += 48
                if(rank == 3300): # On est dans le cas de 1/2/3/3
                    score += 24
                if(rank == 2220): # On est dans le cas de 1/2/2/2
                    score += 30
                if(rank == 2200): # On est dans le cas de 1/2/2/3
                    score += 36
                if(rank == 1110): # On est dans le cas de 1/1/1/4
                    score += 42
                if(rank == 1111): # On est dans le cas de 1/1/1/1
                    score += 36
    return score

def rankingPlayer(idPlayer):
# On passe en argument l'id du joueur et la fonction nous ressort un zip du classement du joueur associe au nb d'équipe pour chacun des jeux auquels le jouer à participé 
    listRanking = [] # list qui contient le classement du joueur pour chacun de ses matchs.
    listNumberTeam = []
    listIdGame = []
    listOfListTrueGameModel = []
    objIdPlayer = Player.objects.get(id=idPlayer)
    groupsPlayer = Group.objects.filter(player=idPlayer)
    for group in groupsPlayer:
        listRanking.append(int(group.ranking))
        listNumberTeam.append(group.game.numberGroups) #group.game donne l'id du game associé
        listIdGame.append(group.game.id)
        listOfListTrueGameModel.append(get_boolean_field_values(group.game.gameModel))

    #On veut aussi ajouter le nombre d'equipe du jeu associé au classement
    return zip(listRanking[::-1][0:7],listNumberTeam[::-1][0:7],listIdGame[::-1][0:7],listOfListTrueGameModel[::-1][0:7])


def createTeam(listAttentance, numberGroups):
    listGroups = []
    if(len(listAttentance) % numberGroups == 0):
        for k in range (numberGroups):
            listGroups.append(listAttentance[int((len(listAttentance)/numberGroups))*k:int((len(listAttentance)/numberGroups))*(k+1)])
    return listGroups


def NouveauMatch(request):
    currentTeam = request.user.coachparams.currentTeam_id
    Players = Player.objects.filter(team=currentTeam)
    obj = request.user.coachparams.team.get(id=currentTeam)
    attendanceStringId = str(request.user.coachparams.team.get(id=currentTeam).attendance).split("/")
    attendanceIntId = []
    for idPlayer in attendanceStringId:
        attendanceIntId.append(int(idPlayer))
    if request.method == 'POST':
        attendance = []
        for player in Players:    
            if request.POST.get(str(player.id)):
                attendance.append(str(player.id))
        liste = "/".join(attendance)
        obj.attendance = liste
        obj.save()
        return redirect('/NouveauMatch/CaracteristiqueMatch/nbPlayer='+str(len(attendance)))
    return render(request, 'NouveauMatch.html', {'Players':Players,'ListeJoueurPresentId':attendanceIntId})


def NouveauMatchCaracteristiqueMatch(request,nbPlayer):
    nbPlayer = int(nbPlayer)
    if request.method == 'POST':
        numberGroups = request.POST.get('numberGroups')
        nameGame = request.POST.get('nameGame')
        return redirect('/NouveauMatch/CaracteristiqueMatch/EquipesClassement/numberGroups='+numberGroups+'/nameGame='+nameGame)
    return render(request, 'NouveauMatchCaracteristiqueMatch.html',{'nbPlayer':nbPlayer,"input":0})


def NouveauMatchCaracteristiqueMatchEquipeClassement(request,numberGroups,nameGame):
    currentTeam = request.user.coachparams.currentTeam_id
    obj = request.user.coachparams.team.get(id=currentTeam)
    StringAttendance = obj.attendance
    ListIdAttendance = StringAttendance.split("/")
    # ListPlayerAttandance = []
    
    # for idplayer in ListIdAttendance:
    #     ListPlayerAttandance.append(str(Player.objects.get(id=int(idplayer)).firstName))

    
    ListIdAttendance = [int(player) for player in ListIdAttendance]
    ListPlayerAttandance = [str(Player.objects.get(id=int(idplayer)).firstName) for idplayer in ListIdAttendance]
        
    
    NewListIdAttendance = handleEquality(ListIdAttendance,int(numberGroups))[1]
    listRandomTeamId = []
    for y in range(10):
        random.shuffle(NewListIdAttendance)
        ListIdAttendance = [int(player) for player in ListIdAttendance]
        ListPlayerAttandance = [str(Player.objects.get(id=int(idplayer)).firstName) for idplayer in ListIdAttendance]
        L = createTeam(NewListIdAttendance, int(numberGroups))
        #handleEquality(ListIdAttendance,numberGroups)[1]
        #L = createTeam(ListIdAttendance, int(numberGroups))
        listRandomTeamId.append(L) #Liste de 10 équipes différentes (avec le String) ( liste de liste)
        listGroupsString = L
        listGroupsId = L
        listeClassement = range(1,len(listGroupsId)+1)
    
    py0= handleEquality(ListIdAttendance,int(numberGroups))[0]
    py1=handleEquality(ListIdAttendance,int(numberGroups))[1]


    scoreRandomTeamMistake = [] #Liste de liste qui va contenir le score de tous les joueurs pour toutes les équipes
    for subRandomTeamId in listRandomTeamId:#Creation d'une liste mais au lieu de mettre tous les joueurs, on met le score de tous les joueurs
        #A partir de maintenant on travail sur une equipe
        for subTeamId in subRandomTeamId:
            #A partir de maintenant on travail sur une couleur
            scoreSubTeam = [scroreId(idPlayer) for idPlayer in subTeamId] #on travail ici sur l'id du joueur
            scoreRandomTeamMistake.append(scoreSubTeam)
        
    z=0
    scoreRandomTeam = []
    for p in range(int(len(scoreRandomTeamMistake)/int(numberGroups))):
        scoreRandomTeam.append(list(scoreRandomTeamMistake[int(int(numberGroups)*z):int(int(numberGroups)*(z+1))]))
        z = z+1

    #Maintenant, pour toutes les couleurs des equipes, il faut faire la moyenne

    meanRandomTeamMistake = [] #Liste qui contient la moyenne du score des joueurs pour les différentes équipes
    for subRandomTeamId in scoreRandomTeam:#Creation d'une liste mais au lieu de mettre tous les joueurs, on met le score de tous les joueurs
        #A partir de maintenant on travail sur une equipe
        for subTeamId in subRandomTeamId:
            #A partir de maintenant on travail sur une couleur
            meanSubTeam = mean(subTeamId) #on travail ici sur l'id du joueur
            meanRandomTeamMistake.append(meanSubTeam)
    
    meanRandomTeam = []
    z=0
    for p in range(int(len(meanRandomTeamMistake)/int(numberGroups))):
        meanRandomTeam.append(meanRandomTeamMistake[int(int(numberGroups)*z):int(int(numberGroups)*(z+1))])
        z = z+1

    #Maintenant, pour toutes les moyennes il faut faire la variance
    variancee = []
    for x in meanRandomTeam:
        variancee.append(sqrt(variance(x)))

    indexVariance = 0
    for index,x in enumerate(variancee):
        if(x==min(variancee)):
            indexVariance = index

    selectedTeam = listRandomTeamId[indexVariance]

    listColor = ['red','blue','green','marron','yellow','purple','orange']
    listColorAdjusted = []
    dictionnaryNonRanked = {}
    dictionnaryRanked = {}
    
    u=0
    for color in listColor:
        if u<len(listGroupsString):
            listColorAdjusted.append(color)
            u += 1

    
    listGroupsStringMistake = []
    for team in selectedTeam:
        for idPlayer in team:
            listGroupsStringMistake.append(nameId(int(idPlayer)))

    listGroupString = []
    z=0
    for p in range(int(numberGroups)):
        listGroupString.append(listGroupsStringMistake[int(len(NewListIdAttendance)/int(numberGroups)*z):int(len(NewListIdAttendance)/int(numberGroups))*(z+1)])
        z = z+1

    
    
    meanRandomTeamSelected = meanRandomTeam[indexVariance]

    link = sorted(zip(meanRandomTeamSelected,selectedTeam))
    
    h=0
    if(len(handleEquality(ListIdAttendance,int(numberGroups))[0]) != 0):
        for score,team in link:
            team.append(handleEquality(ListIdAttendance,int(numberGroups))[0][h])
            if h<len(handleEquality(ListIdAttendance,int(numberGroups))[0])-1:
                h+=1
            else:
                break
    
    finalSelectedTeam = []
    for score,team in link:
        finalSelectedTeam.append(team)
    
    finalSelectedTeamString = []

    for team in finalSelectedTeam:
        teamString = ['' for k in range(len(team))]
        for k in range(len(team)):
            teamString[k] = nameId(team[k])
        finalSelectedTeamString.append(teamString)

    tuple_ListColor_ListGroupsId = zip(listColor,finalSelectedTeam)
    tuple_ListColor_ListGroupsString = zip(listColor,finalSelectedTeamString)
    for color,team in tuple_ListColor_ListGroupsId:
        dictionnaryNonRanked[color] = team

    if request.method == 'POST':
        if 'championnat' not in request.POST:
            if(numberGroups==2):
                if request.POST.get("22"):
                    return('hjbk.html') #ca va générer une erreur et c'est normale car pour 2 équipes le "22" ne peut jamais etre remplie (dans l'ideal il faudrait l'eneleer à l'affichae )

            listColorRanked = []
            listTeamRanked = []
            for k in listeClassement:
                for j in listeClassement:
                    if request.POST.get(str(str(k)+str(j))):
                        listColorRanked.append(request.POST.get(str(str(k)+str(j))))
            for color in listColorRanked:
                dictionnaryRanked[color] = dictionnaryNonRanked[color]

            # First, we create the game object.
            g1 = Game.objects.create(nameGame = nameGame, numberGroups=numberGroups)

            # Then we have to link the game with all the rankings and link all the rankings to the players
            numberGroups = int(numberGroups)
            rank=1
            for color, listTeamId in dictionnaryRanked.items():
                # First, we create a group object that we link to a game
                if(numberGroups == 2):
                    if (request.POST.get(str("1"+"2"))!=""):
                        #dans ce cas il y a un cas d'égalité et le range des deux équipes doit etre de 11
                        grp = Group(ranking = 11, game=g1)
                    else:
                        #Dans ce cas il n'y a pas d'égalité
                        if(rank==1):
                            grp = Group(ranking = 10, game=g1)
                        if(rank==2):
                            grp = Group(ranking = 20, game=g1)
                if(numberGroups == 3):
                    if(request.POST.get("1"+"2") and request.POST.get("13")): # On est dans le cas de 1er / 1er / 1er
                        grp = Group(ranking = 111, game=g1)
                    elif(request.POST.get("12") and not request.POST.get("13")): # 1er / 1er / 3eme
                        if(rank == 1):
                            grp = Group(ranking = 110, game=g1)
                        if(rank == 2):
                            grp = Group(ranking = 110, game=g1)
                        if(rank == str(3)):
                            grp = Group(ranking = 300, game=g1)
                    elif(request.POST.get("22")): # On est dans le cas 1er / 2eme / 2eme
                        if(rank==1):
                            grp = Group(ranking = 100, game=g1)
                        if(rank==2):
                            grp = Group(ranking=220, game=g1)
                        if(rank==3):
                            grp = Group(ranking=220, game=g1)

                    else: #Alors il n'y a pas eu d'égalité
                        if(rank==1):
                            grp = Group(ranking = 100, game=g1)
                        if(rank==2):
                            grp = Group(ranking = 200, game=g1)
                        if(rank==3):
                            grp = Group(ranking = 300, game=g1)
                if(numberGroups == 4):
                    if(request.POST.get("12") and request.POST.get("22")): #On est dans le cas 1/1/3/3
                        if(rank == 1):
                            grp = Group(ranking=1100, game=g1)
                        if(rank == 2):
                            grp = Group(ranking=1100, game=g1)
                        if(rank == 3):
                            grp = Group(ranking=3300, game=g1)
                        if(rank == 4):
                            grp = Group(ranking=3300, game=g1)
                    elif(request.POST.get("12") and request.POST.get("22")): #On est dans le cas 1/2/2/4
                        if(rank == 1):
                            grp = Group(ranking=1000, game=g1)
                        if(rank == 2):
                            grp = Group(ranking=2200, game=g1)
                        if(rank == 3):
                            grp = Group(ranking=2200, game=g1)
                        if(rank == 4):
                            grp = Group(ranking=4000, game=g1)
                    elif(request.POST.get("22") and request.POST.get("23")): #On est dans le cas 1/2/2/2
                        if(rank == 1):
                            grp = Group(ranking=1000, game=g1)
                        if(rank == 2):
                            grp = Group(ranking=2220, game=g1)
                        if(rank == 3):
                            grp = Group(ranking=2220, game=g1)
                        if(rank == 4):
                            grp = Group(ranking=2220, game=g1)
                    elif(request.POST.get("12")): #On est dans le cas 1/1/3/4
                        if(rank == 1):
                            grp = Group(ranking=1100, game=g1)
                        if(rank == 2):
                            grp = Group(ranking=1100, game=g1)
                        if(rank == 3):
                            grp = Group(ranking=3000, game=g1)
                        if(rank == 4):
                            grp = Group(ranking=4000, game=g1)

                    elif(request.POST.get("12") and request.POST.get("13")): #On est dans le cas 1/1/1/4
                        if(rank == 1):
                            grp = Group(ranking=1110, game=g1)
                        if(rank == 2):
                            grp = Group(ranking=1110, game=g1)
                        if(rank == 3):
                            grp = Group(ranking=1110, game=g1)
                        if(rank == 4):
                            grp = Group(ranking=4000, game=g1)

                    elif(request.POST.get("12")  and request.POST.get("13")  and request.POST.get("14")): #On est dans le cas 1/1/1/1
                        grp = Group(ranking=1111, game=g1)

                    else: #Alors il n'y a pas eu d'égalité
                        if(rank==1):
                            grp = Group(ranking = 1000, game=g1)
                        if(rank==2):
                            grp = Group(ranking = 2000, game=g1)
                        if(rank==3):
                            grp = Group(ranking = 3000, game=g1)
                        if(rank==4):
                            grp = Group(ranking=4000,game=g1)

                grp.save()
                # Now we have to link the group to all players
                for idPlayer in listTeamId:
                    grp.player.add(Player.objects.get(id=int(idPlayer)))
                grp.save()
                rank = rank + 1
            return redirect('/NouveauMatch/')

    f=0
    dataColorTeamChampionnat = {}
    for color in listColorAdjusted:
        dataColorTeamChampionnat[color] = [x for x in listColorAdjusted[f+1:len(listColor)]]
        f += 1

    dataColorTeamChampionnat_js = json.dumps(dataColorTeamChampionnat)
    # ResultMatch = []
    # if request.method=='POST':
    #     if 'championnat' in request.POST:
    #         for color,listColor in dataColorTeamChampionnat.items():
    #             for AColor in listColor:
    #                 ResultMatch.append(request.POST.get(str(color)+str(AColor)))
    # dataTeamChampionnat = {}
    # for color in listColorAdjusted:
    #     listCleColor = []
    #     for result in ResultMatch:
    #         if color == result:
    #             listCleColor.append(1)
    #     dataTeamChampionnat[color] = len(listCleColor)

    

    return render(request, 'NouveauMatchCaracteristiqueMatchEquipeClassement.html',{
        'dataColorTeamChampionnat':dataColorTeamChampionnat,
        'dataColorTeamChampionnat_js':dataColorTeamChampionnat_js,
        #'dataTeamChampionnat':dataTeamChampionnat.items(),
        #'ResultMatch':ResultMatch,
        'dataColorTeamChampionnat':dataColorTeamChampionnat.items(),
        'listColorAdjusted':listColorAdjusted,
        'finalSelectedTeamString':finalSelectedTeamString,
        'finalSelectedTeam':finalSelectedTeam,
        'link':link,
        'meanRandomTeamSelected':meanRandomTeamSelected,
        'py0':py0,'py1':py1,
        'listGroupsStringMistake':listGroupsStringMistake,
        'listGroupString':listGroupString,
        'selectedTeam':selectedTeam,
        'indexVariance':indexVariance,'variancee':variancee,'meanRandomTeam':meanRandomTeam,
        'scoreRandomTeam':scoreRandomTeam,'ListIdAttendance':ListIdAttendance,
        'listRandomTeam':listRandomTeamId,'tupleColorGroup':tuple_ListColor_ListGroupsString ,
        'listeClassement':listeClassement,'listColorAdjusted':listColorAdjusted,
        'dictionnaryRanked':dictionnaryRanked,'dictionnaryNonRanked':dictionnaryNonRanked, 
        'nbgrp':numberGroups})


def FeedbackJeux(request):
    AfficheJeu = Game.objects.filter(completed=0)
    return render(request, 'FeedbackJeux.html', {'AfficheJeu' : AfficheJeu})


def FeedbackJeuxBase(request,idGame):
    if request.method == 'POST':
        # D'abord on recupere puis enregistre le jeu
        gameObj = Game.objects.get(id=idGame)
        gameObj.completed = 1
        
        #Maintenant on créé le model de jeu
        cible = request.POST.get('Cible')
        gardien = request.POST.get('Gardien')
        Revêtement_de_jeu = request.POST.get('Revêtement_de_jeu')
        Nbr_de_touches = request.POST.get('Nbr_de_touches')
        Hors_Jeu = request.POST.get('Hors_Jeu')
        Dimension = request.POST.get('Dimension')
        newGameModel = GameModel.objects.create(
            **{cible : True},
            **{gardien : True},
            **{Revêtement_de_jeu : True},
            **{Nbr_de_touches : True},
            **{Hors_Jeu : True},
            **{Dimension : True},
        )
        gameObj.gameModel = newGameModel
        gameObj.save()
       
        #Puis on relie le model de jeu avec le jeu en question
        return redirect('/FeedbackJeux/')
    return render(request,'FeedbackJeuxBase.html')


def StatistiqueGame(request):
    MyTeams = request.user.coachparams.team.all()
    taille=1
    zipRankingNumberIdgameIdgamemodel = ''
    zipRankingNumberIdgameIdgamemodel2 = ''
    score = 0
    scoreGoalKeeperYes = 0
    scoreGoalKeeperNo = 0
    scoreOffLineYes = 0
    scoreOffLineNo = 0
    scoreSynthetiqueDry = 0
    scoreSynthetiqueWet = 0
    scoreStabiliseDry = 0
    scoreStabiliseWet = 0
    scoreGrassDry = 0
    scoreGrassWet = 0
    scoreOtherField = 0
    scoreGoal11 = 0
    scoreGoal7 = 0
    scoreGoalEmbut = 0
    scoreGoalNone = 0
    scoreGoalOther = 0
    scoreTB1_3 = 0
    scoreTB_2 = 0
    scoreTB_free = 0
    scoreGoalSmall = 0

    #Construction du dictionnaire pour la barre de rechercher

    Players = Player.objects.all()

    persons = []
   
    for player in Players:
        data = {}
        data['name']=str(str(player.firstName)+" "+str(player.lastName))
        persons.append(data)

    if request.method == 'POST':
        if 'statPlayer'  in request.POST:
            firstName_lastName = request.POST.get('firstName_lastName').strip(" ").title().split(" ") #on retire les espaces en debut et fin de chaine et on ajoute les majuscules au prénom et nom s'ils on ete oublie
            if(len(firstName_lastName)!=2):
                return redirect('/StatistiqueGame/')
            objectJoueur = Player.objects.filter(firstName=str(firstName_lastName[0])).filter(lastName=str(firstName_lastName[1]))
            if not objectJoueur:
                return redirect('/StatistiqueGame/')
            for joueur in objectJoueur:
                zipRankingNumberIdgameIdgamemodel = rankingPlayer(joueur.id)
                zipRankingNumberIdgameIdgamemodel2 = rankingPlayer(joueur.id)
            for rank,number,idGame,idGameModel in zipRankingNumberIdgameIdgamemodel:
                if (number == 2): #Dans le cas de deux équipes
                    if (rank==10):
                        score += 54
                    if (rank == 20):
                        score += 18
                    if(rank == 11):
                        score += 36
                if (number == 3): #Dans le cas de trois équipes
                    if (rank==100):
                        score += 54
                    if (rank == 200):
                        score += 36
                    if (rank == 300):
                        score += 18
                    if(rank == 111): # On est dans le cas de 1er / 1er / 1er
                        score += 36
                    if(rank == 110): # On est dans le cas de 1er / 1er / 2eme
                        score += 45
                    if(rank == 220): # On est dans le cas de 1er / 2eme / 2eme
                        score += 27 
                if (number == 4): #Dans le cas de deux équipes
                    if (rank==1000):
                        score += 54
                    if (rank == 2000):
                        score += 42
                    if (rank == 3000):
                        score += 30
                    if (rank == 4000):
                        score += 18
                    if(rank == 1100): # On est dans le cas de 1/1/...
                        score += 48
                    if(rank == 3300): # On est dans le cas de 1/2/3/3
                        score += 24
                    if(rank == 2220): # On est dans le cas de 1/2/2/2
                        score += 30
                    if(rank == 2200): # On est dans le cas de 1/2/2/3
                        score += 36
                    if(rank == 1110): # On est dans le cas de 1/1/1/4
                        score += 42
                    if(rank == 1111): # On est dans le cas de 1/1/1/1
                        score += 36

        # On met dans la table Player le score du joueur
            if Player.objects.get(id=joueur.id):
                taille = len(list(zip(rankingPlayer(joueur.id))))
                ply = Player.objects.get(id=joueur.id)
                ply.globalScore = score/taille #On fait la moyennHJKKJHJKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKe sur les 7 derniers matchs
                ply.save()
                
            if joueur.id:
                scoreGoalKeeperYes = searchScore('goalKeeperYes', rankingPlayer(joueur.id))
                scoreGoalKeeperNo = searchScore('goalKeeperNo', rankingPlayer(joueur.id))
                scoreOffLineYes = searchScore('offLineYes', rankingPlayer(joueur.id))
                scoreOffLineNo = searchScore('offLineNo', rankingPlayer(joueur.id))
                scoreSynthetiqueDry = searchScore('synthetiqueDry', rankingPlayer(joueur.id))
                scoreSynthetiqueWet = searchScore('synthetiqueWet', rankingPlayer(joueur.id))
                scoreStabiliseDry = searchScore('stabiliseDry', rankingPlayer(joueur.id))
                scoreStabiliseWet = searchScore('stabiliseWet', rankingPlayer(joueur.id))
                scoreGrassDry = searchScore('grassDry', rankingPlayer(joueur.id))
                scoreGrassWet = searchScore('grassWet', rankingPlayer(joueur.id))
                scoreOtherField = searchScore('otherField', rankingPlayer(joueur.id))
                scoreGoal11 = searchScore('goal11', rankingPlayer(joueur.id))
                scoreGoal7 = searchScore('goal7', rankingPlayer(joueur.id))
                scoreGoalEmbut = searchScore('goalEmbut', rankingPlayer(joueur.id))
                scoreGoalNone = searchScore('goalNone', rankingPlayer(joueur.id))
                scoreGoalOther = searchScore('goalOther', rankingPlayer(joueur.id))
                scoreTB1_3 = searchScore('TB1_3', rankingPlayer(joueur.id))
                scoreTB_2 = searchScore('TB_2', rankingPlayer(joueur.id))
                scoreTB_free = searchScore('TB_free', rankingPlayer(joueur.id))
                scoreGoalSmall = searchScore('goalSmall', rankingPlayer(joueur.id))

    if request.method == 'POST':
        if 'StatTeam' in request.POST:
            return redirect('/StatistiqueGame/idTeam='+str(request.POST.get('currentTeam')))


    return render(request, 'StatistiqueGame.html',
    {'scoreGoalKeeperYes':scoreGoalKeeperYes,
    'scoreGoalSmall':scoreGoalSmall,
    'scoreTB_free':scoreTB_free,
    'scoreTB_2':scoreTB_2,
    'scoreTB1_3':scoreTB1_3,
    'scoreGoalOther':scoreGoalOther,
    'scoreGoalNone':scoreGoalNone,
    'scoreGoalEmbut':scoreGoalEmbut,
    'scoreGoal7':scoreGoal7,
    'scoreGoal11':scoreGoal11,
    'scoreOtherField':scoreOtherField,
    'scoreGrassWet':scoreGrassWet,
    'scoreGrassDry':scoreGrassDry,
    'scoreStabiliseWet':scoreStabiliseWet,
    'scoreStabiliseDry':scoreStabiliseDry,
    'scoreSynthetiqueWet':scoreSynthetiqueWet,
    'scoreSynthetiqueDry':scoreSynthetiqueDry,
    'scoreOffLineNo':scoreOffLineNo,
    'scoreOffLineYes':scoreOffLineYes,
    'scoreGoalKeeperNo':scoreGoalKeeperNo,
    'zipRankingNumberIdgameIdgamemodel':zipRankingNumberIdgameIdgamemodel2 ,
     'score':score/taille,
     
     'MyTeams':MyTeams,
     'persons':persons})

    
def FeedbackJeuxBaseTeam(request,idTeam):
    listScore = []
    listFirstName_LastName = []
    data = {}
    searchCara = ''
    dataCara = {}
    Players = Player.objects.filter(team=idTeam)
    for player in Players:
        data[str(str(player.firstName)+str(player.lastName))] = int(player.globalScore)
    
    dataSorted = sorted(data.items(), key=lambda t: t[1])

    for name,score in dataSorted:
        listScore.append(int(score))
        listFirstName_LastName.append(str(name))

    ZipScoreName = zip(listScore[::-1],listFirstName_LastName[::-1]) 
    if request.method == 'POST':
        listScore = []
        listFirstName_LastName = []
        searchCara = str(request.POST.get("searchCara"))
        dataCara = {}
        for player in Players:
            dataCara[str(str(player.firstName)+str(player.lastName))] = int(searchScore(searchCara, rankingPlayer(player.id)))
    
        dataSorted = sorted(dataCara.items(), key=lambda t: t[1])

        for name,score in dataSorted:
            listScore.append(int(score))
            listFirstName_LastName.append(str(name)) 
        ZipScoreName = zip(listScore[::-1],listFirstName_LastName[::-1])
    return render(request, 'FeedbackJeuxBaseTeam.html', {'searchCara':searchCara,'dataCara':dataCara,'ZipScoreName':ZipScoreName})


def HistoriqueJeu(request):
    idUser = request.user.id
    currentTeamId = CoachParams.objects.get(user=idUser).currentTeam.id

    # Selection de l'id des joueurs appartenant à l'équipe
    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]

    # Selection des groupes associés aux joueurs séléctionnés.
    #Table.objects.filter(column__in=your_list)
    idGroupList = [ x.id for x in Group.objects.filter(player__in=idListPlayer)]

    # Selection des jeux associés aux groupes
    #Counter(list).keys()
    idGameList = list(Counter([ x.game.id for x in Group.objects.filter(id__in=idGroupList)]).keys())

    # Selection des modelsGame associés aux jeux
    idGameModelList = [x.gameModel.id for x in Game.objects.filter(id__in=idGameList)]

    ## Selection des caractéristique des jeux
    L=[]
    i=0
    for idGameModel in idGameModelList:
        U=[]
        U.append(str(Game.objects.get(id=idGameList[i]).dateGame).split("-"))
        for x in get_boolean_field_values(GameModel.objects.get(id=idGameModel)):
            U.append(x)
        L.append(U)
        i+=1
    return render(request,'Historique.html',{'listBlue':["offLineYes","goalKeeperYes"],'listRed':["offLineNo","goalKeeperNo"],'currentTeamId':currentTeamId,'idListPlayer':idListPlayer,'idGroupList':idGroupList,'idGameList':idGameList,'idGameModelList':idGameModelList,'L':L[::-1]})

    
def PlayerInGroup(idGroup)->list:
    return  [player.id for player in Player.objects.filter(groups=idGroup)]


def Assiduite(request):
    idUser = request.user.id
    currentTeamId = CoachParams.objects.get(user=idUser).currentTeam.id

    # Selection de l'id des joueurs appartenant à l'équipe
    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]

    # Selection des groupes associés aux joueurs séléctionnés.
    #Table.objects.filter(column__in=your_list)
    idGroupList = [ x.id for x in Group.objects.filter(player__in=idListPlayer)]

    # Selection des jeux associés aux groupes
    #Counter(list).keys()
    idGameList = list(Counter([ x.game.id for x in Group.objects.filter(id__in=idGroupList)]).keys())

    # Selection des modelsGame associés aux jeux
    idGameModelList = [x.gameModel.id for x in Game.objects.filter(id__in=idGameList)]

    ## Selection des caractéristique des jeux
    L=[]
    i=0
    for idGameModel in idGameModelList:
        U=[]
        U.append(str(Game.objects.get(id=idGameList[i]).dateGame))
        for x in get_boolean_field_values(GameModel.objects.get(id=idGameModel)):
            U.append(x)
        L.append(U)
        i+=1

    #Objectif : savoir quels joueurs etaient associé à un jeu quand on connait son id (idGameModel)
    listIdGroup = []
    for idGame in idGameList:
        F=[]
        for idGroup in idGroupList:
            if (int(Group.objects.get(id=idGroup).game.id) == idGame):
                F.append(idGroup)
        listIdGroup.append(F)

    ListePlayerId = []
    for liste in listIdGroup:
        O = []
        for idGroup in liste:
            O.append(PlayerInGroup(idGroup))
        ListePlayerId.append(O)


    ListePlayerIdConcatene = []
    for liste in ListePlayerId:
        P=[]
        for listeGroupId in liste:
            for playerId in listeGroupId:
                P.append(playerId)
        ListePlayerIdConcatene.append(P)
        
    DateGame = [str(Game.objects.get(id=idGame).dateGame) for idGame in idGameList ]

    zipDateGame_ListePlayerIdConcatene = zip(DateGame,ListePlayerIdConcatene)

    data = {}
    for date,liste in zipDateGame_ListePlayerIdConcatene:
        data2 = {}
        data2[date] = liste
        try:
            data[date] = data[date] + data2[date]
        except:
            data[date] = data2[date]

    finalData = {}
    for idPlayer in idListPlayer:
        presence = 0
        for date,liste in data.items():
            if idPlayer in liste:
                presence += 1
        #finalData[idPlayer] = presence/len(list(data.keys()))
        finalData[idPlayer] =  len(list(data.keys())) - int(presence)


    return render(request, 'Assiduite.html',{'idListPlayer':idListPlayer,'idGroupList':idGroupList,'idGameModelList':idGameModelList,'idGameList':idGameList,'listIdGroup':listIdGroup,'ListePlayerId':ListePlayerId,'ListePlayerIdConcatene':ListePlayerIdConcatene,'DateGame':DateGame,'zipDateGame_ListePlayerIdConcatene':zipDateGame_ListePlayerIdConcatene,'data':data,'finalData':finalData})



def ScoreIdGame(idGame:int):#Donne les scoueurs associés à l'id d'un game
    data = {}
    groups = Group.objects.filter(game=idGame) # Il s'agit des groupes associés au game
    for group in groups:
        #data.append(group.ranking)
        L=[]
        for player in Player.objects.filter(groups=group):
            L.append(player.id)
        #data.append(L)
        try :
            data[group.ranking] = data[group.ranking] + L
        except:
            data[group.ranking] = L
    return data

def ListScoreDatePlayer(idPlayer :int,zipDateDico):
    data = {}
    for date,dico in zipDateDico:
        L=[]
        for rank,listIdPlayer in dico.items():
            if idPlayer in listIdPlayer:
                if len(list(dico.keys())) == 2:# On est dans le cas de 2 groupes
                    if rank == 1:
                        L.append(54)
                    if rank == 2:
                        L.append(18)
                    if rank == 11:
                        L.append(36)
                if len(list(dico.keys())) == 3:# On est dans le cas de 3 groupes
                    if rank == 1:
                        L.append(54)
                    if rank == 2:
                        L.append(18)
                    if rank == 3:
                        L.append(36)
                    if rank == 110:
                        L.append(45)
                    if rank == 111:
                        L.append(36)
                    if rank == 220:
                        L.append(27)
                if len(list(dico.keys())) == 4:# On est dans le cas de 4 groupes
                    L.append(54)
            else:
                pass
        if date in list(data.keys()):
            u = data[date]
            data[date] = u + L
        else:
            data[date] = L

    finalData = {}  
    for date,liste in data.items():
        if len(liste) != 0:
            finalData[date] = mean(liste)

    return finalData



def GraphEquipe(request):
    idUser = request.user.id
    currentTeamId = CoachParams.objects.get(user=idUser).currentTeam.id

    # Selection de l'id des joueurs appartenant à l'équipe
    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]

    # Selection des groupes associés aux joueurs séléctionnés.
    #Table.objects.filter(column__in=your_list)
    idGroupList = [ x.id for x in Group.objects.filter(player__in=idListPlayer)]

    # Selection des jeux associés aux groupes
    #Counter(list).keys()
    idGameList = list(Counter([ x.game.id for x in Group.objects.filter(id__in=idGroupList)]).keys())
    POPO = [ScoreIdGame(idGame) for idGame in idGameList]
    

    DateGame = [str(Game.objects.get(id=idGame).dateGame) for idGame in idGameList ]
    #nbGroupGame = [Group.objects.filter(game=idGame).numberGroups for idGame in idGameList ]
    PIPI = zip(DateGame,POPO)
    PIPI2 = zip(DateGame,POPO)
    PIPI3 = zip(DateGame,POPO)

    Date = []
    Score = []
    for date,score in ListScoreDatePlayer(1,PIPI).items():
        Date.append(date)
        Score.append(score)
    chart = get_plot(Date,Score)
    data = {}


    chartPie = get_chartPie(Score)

    G=[12,10]
    MultipleChart = get_multiple_plot(G,[zip(DateGame,POPO) for k in range(len(G))])

    return render(request, 'GraphEquipe.html',{
        'MultipleChart':MultipleChart,
        'chartPie':chartPie,
        'chart':chart,
        'ListScoreDatePlayer':ListScoreDatePlayer(1,PIPI),
        'data':data,
        'POPO':POPO,
        'idListPlayer':idListPlayer,
        'DateGame':DateGame,
        'idGameList':idGameList,
        'PIPI':list(PIPI2)})


def Championnat(request,numberGroups):
    return render(request,'Championnat.html',{})

def createStatGliss(listScore : list,f,t,n)->list:
    listRankingPlayerFenetre = []
    i=0
    for k in range(len(listScore)):
        # if len(listScore[i:(i+1)*f]) < f:
        if len(listScore[i:]) < f:
            break
        listRankingPlayerFenetre.append(mean(sorted(listScore[i:i+f])[t:])) 
        i += 1
    return listRankingPlayerFenetre

def  StatGliss(request):

    #D'abord on va essayer de faire une stat glissé sur le joueur id=1
    joueur = Player.objects.get(id=1)
    #Il faut filtrer les groupes associés aux joueurs

    idUser = request.user.id
    currentTeamId = CoachParams.objects.get(user=idUser).currentTeam.id
    
    groups = Group.objects.filter(player=joueur)[0:CoachParams.objects.get(currentTeam=currentTeamId).nbMatch] 
    listRankingPlayer = [group.ranking for group in groups]


    

    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]

    idGroupList = sorted(Counter([ x.id for x in Group.objects.filter(player__in=idListPlayer)]))[::-1]

    idGameList = list(Counter([ x.game.id for x in Group.objects.filter(id__in=idGroupList)]).keys())[::-1][0:CoachParams.objects.get(currentTeam=currentTeamId).nbMatch]
    nbGroupList = [Game.objects.get(id=x).numberGroups for x in idGameList]


    L=[]
    count = 0
    for nb in nbGroupList:
        L.append(idGroupList[count:count+nb])
        count+=nb

    V=[]
    for listGroup in L:
        H=[]
        for group in listGroup:
            H.append([x.id for x in Player.objects.filter(groups=group)])
        V.append(H)

    U=[]
    for x in V:
        W=[]
        for y in x:
            W.extend(y)
        U.append(W)

    
    RankingGroups = []
    for listGroup in L:
        K=[Group.objects.get(id=group).ranking for group in listGroup]
        RankingGroups.append(K)


    dataScorePlayer = {}
    for IdPlayerTeam in idListPlayer:
        ListScorePlayerAbscence = []
        for index,ListIdPlayer in enumerate(U):
            if IdPlayerTeam in ListIdPlayer:
                pass   
            else:
                ListScorePlayerAbscence.append(index)

        ListScorePlayer = []
        for listIdPlayerDouble,listRank in zip(V,RankingGroups):
            for index,listIdPlayer in enumerate(listIdPlayerDouble):
                if IdPlayerTeam in listIdPlayer:
                    ListScorePlayer.append(listRank[index])
        
        for indexAbscence in ListScorePlayerAbscence:
            ListScorePlayer.insert(indexAbscence,0)
        dataScorePlayer[IdPlayerTeam] = ListScorePlayer

    finalDataScorePlayer = {}
    for cle,valeur in dataScorePlayer.items():
        finalDataScorePlayer[cle] = [FromRankingToScore(u) for u in valeur]

    myFinalData = {}
    for cle,valeur in finalDataScorePlayer.items():
        myFinalData[cle] = createStatGliss(valeur,CoachParams.objects.get(currentTeam=currentTeamId).fenetre,CoachParams.objects.get(currentTeam=currentTeamId).tolerance,CoachParams.objects.get(currentTeam=currentTeamId).nbMatch)
   
    theUltimateData = {}
    
    for cle,valeur in myFinalData.items():
        I = []
        count = 0
        for x in valeur:
            Y = list(Counter(sorted([score[count] for id,score in myFinalData.items()])))
            I.append(len(Y) - Y.index(valeur[count]))
            count += 1
        theUltimateData[cle] = I
        
    graph = get_plot([str(x) for x in range(1,len(myFinalData[12])+1)[::-1]],myFinalData[12][::-1])
    graph2 = get_plot([str(x) for x in range(1,len(theUltimateData[12])+1)],sorted([str(x) for x in theUltimateData[2]])[::-1])

    graphEquipe = get_multiple_plot([1,2],myFinalData)
    graphEquipeRank = get_multiple_plot([1,2],theUltimateData)


    for idPlayer,listScore in myFinalData.items():
        ply = Player.objects.get(id=idPlayer)
        ply.globalScore = mean(listScore)
        ply.save()

    if request.method == 'POST':
        if 'voirGraph' in request.POST:
            AjoutPlayer = []
            for id in idListPlayer:
                if request.POST.get(str(id)):
                    AjoutPlayer.append(id)
            if request.POST.get("Milieu"):
                AjoutPlayer.extend([x.id for x in Player.objects.filter(placeOnField="Milieu")])
            if request.POST.get("Attaquant"):
                AjoutPlayer.extend([x.id for x in Player.objects.filter(placeOnField="Attaquant")])
            graphEquipe = get_multiple_plot(list(Counter(AjoutPlayer)),myFinalData)
            graphEquipeRank = get_multiple_plot(list(Counter(AjoutPlayer)),theUltimateData)

    ## Affichage des joueurs en fonction de leur score
    listScore = []
    listFirstName_LastName = []
    data = {}
    searchCara = ''
    dataCara = {}
    Players = Player.objects.filter(team=currentTeamId)
    for player in Players:
        data[player] = int(player.globalScore)
    
    dataSorted = sorted(data.items(), key=lambda t: t[1],reverse=True)


    return render(request,'StatGliss.html',{'dataSorted':dataSorted,'graphEquipeRank':graphEquipeRank,'listObjPlayer': [ Player.objects.get(id=x) for x in idListPlayer],'graphEquipe':graphEquipe,'graph2':graph2,'theUltimateData':theUltimateData,'graph':graph,'myFinalData':myFinalData,'finalDataScorePlayer':finalDataScorePlayer,'dataScorePlayer':dataScorePlayer,'ListScorePlayerAbscence':ListScorePlayerAbscence,'RankingGroups':RankingGroups,'temp':list(zip(V,RankingGroups)),'ListScorePlayer1':ListScorePlayer,'U':U,'V':V,'L':L,'nbGroupList':nbGroupList,'idGroupList':idGroupList,'idGameList':idGameList,'idListPlayer':idListPlayer,'listRankingPlayer':listRankingPlayer})
