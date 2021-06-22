from django.shortcuts import render
from django.contrib.auth import authenticate

from django.shortcuts import redirect

from django.db import models


from .models import Player
from .models import Player
from .models import Group
from .models import Game
from .models import GameModel
from .models import CoachParams

import matplotlib.pyplot as plt
from statistics import mean
import base64
from io import BytesIO

from collections import Counter
# tuto pour avoir acces a des trucs rapidement
# id de l'equipe en cours : request.user.coachparams.currentTeam.id

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
                    if rank == 10:
                        L.append(54)
                    if rank == 20:
                        L.append(18)
                    if rank == 11:
                        L.append(36)
                if len(list(dico.keys())) == 3:# On est dans le cas de 3 groupes
                    if rank == 100:
                        L.append(54)
                    if rank == 200:
                        L.append(18)
                    if rank == 300:
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


def createStatGliss(listScore : list,f,t)->list:
    listRankingPlayerFenetre = []
    i=0
    for k in range(len(listScore)):
        if len(listScore[i:]) < f:
            break
        listRankingPlayerFenetre.append(mean(sorted(listScore[i:i+f])[t:])) 
        i += 1
    return listRankingPlayerFenetre


def  StatGliss(request,ParamIdPlayer):
    #D'abord on va essayer de faire une stat glissé sur le joueur id=1
    joueur = Player.objects.get(id=ParamIdPlayer)
    #Il faut filtrer les groupes associés aux joueurs
    n=10 # au lieu de 10 il faurda mettre n le nb de matchs total
    groups = Group.objects.filter(player=joueur)[0:n] 
    listRankingPlayer = [group.ranking for group in groups]


    #ATTENTION !!!!!! Ici, il faudra convertir les ranking en classement et savoir lorsq'un joueur a ete abscent mettre un score de 0
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
        myFinalData[cle] = createStatGliss(valeur,CoachParams.objects.get(currentTeam=currentTeamId).fenetre,CoachParams.objects.get(currentTeam=currentTeamId).tolerance)
    
    for idPlayer,listScore in myFinalData.items():
        ply = Player.objects.get(id=idPlayer)
        ply.globalScore = mean(listScore)
        ply.save()

    theUltimateData = {}
    
    for cle,valeur in myFinalData.items():
        I = []
        count = 0
        for x in valeur:
            Y = list(Counter(sorted([score[count] for id,score in myFinalData.items()])))
            I.append(len(Y) - Y.index(valeur[count]))
            count += 1
        theUltimateData[cle] = I

    
    return (get_plot(range(1,len(myFinalData[ParamIdPlayer])+1),myFinalData[ParamIdPlayer]),get_plot([str(x) for x in range(1,len(theUltimateData[ParamIdPlayer])+1)],sorted([str(x) for x in theUltimateData[ParamIdPlayer]])[::-1]))

def get_multiple_plot(List,PIPIList):
    plt.switch_backend('AGG')
    plt.figure(figsize=(8,5))
    plt.title('Title')
    count = 0
    for idPlayer in List:
        Date = []
        Score = []
            
        for date,score in ListScoreDatePlayer(idPlayer,PIPIList[count]).items():
            Date.append(date)
            Score.append(score)
        plt.plot(Date,Score,label=Player.objects.get(id=idPlayer).firstName + Player.objects.get(id=idPlayer).lastName )
        count += 1

    plt.legend()
    plt.xticks(rotation=45)
    plt.xlabel(idPlayer)
    plt.ylabel('Score')
    plt.tight_layout()
    graph=get_graph()
    return graph


# Create your views here.
def searchScore(nameColumn,zipRankingNumberIdgameIdgamemodel) -> float: #Prend en paramètre la colonne (dans ModelGame) et nous donne en sortie le score associé à cette colonne. Pour simplifier la fonction en prend aussi le zipRankingNumberIdgameIdgamemodel qui permet d'avoir l'historique des jeux du joueur. L'id du joueur est donné dans le zip
    score = 0
    v=0
    
    for rank,idGameModel in zipRankingNumberIdgameIdgamemodel: #A chaque itération on parcour un jeu
        if str(nameColumn) in list(idGameModel):
            if (rank==10):
                v += 1
                score += 54
            if (rank == 20):
                v += 1
                score += 18
            if(rank == 11):
                v += 1
                score += 36
            if (rank==100):
                v += 1
                score += 54
            if (rank == 200):
                v += 1
                score += 36
            if (rank == 300):
                v += 1
                score += 18
            if(rank == 111): # On est dans le cas de 1er / 1er / 1er
                score += 36
                v += 1
            if(rank == 110): # On est dans le cas de 1er / 1er / 2eme
                score += 45
                v += 1
            if(rank == 220): # On est dans le cas de 1er / 2eme / 2eme
                score += 27
                v += 1
            if (rank==1000):
                score += 54
                v += 1
            if (rank == 2000):
                score += 42
                v += 1
            if (rank == 3000):
                score += 30
                v += 1
            if (rank == 4000):
                score += 18
                v += 1
            if(rank == 1100): # On est dans le cas de 1/1/...
                score += 48
                v += 1
            if(rank == 3300): # On est dans le cas de 1/2/3/3
                score += 24
                v += 1
            if(rank == 2220): # On est dans le cas de 1/2/2/2
                score += 30
                v += 1
            if(rank == 2200): # On est dans le cas de 1/2/2/3
                score += 36
                v += 1
            if(rank == 1110): # On est dans le cas de 1/1/1/4
                score += 42
                v += 1
            if(rank == 1111): # On est dans le cas de 1/1/1/1
                score += 36
                v += 1
    if v==0:
        return score
    else:
        return score/v


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
    return listTrueAttribute


def rankingPlayer(idPlayer,idTeam):
# On passe en argument l'id du joueur et la fonction nous ressort un zip du classement du joueur associe au nb d'équipe pour chacun des jeux auquels le jouer à participé 
    listRanking = [] # list qui contient le classement du joueur pour chacun de ses matchs.
    listOfListTrueGameModel = []
    objIdPlayer = Player.objects.get(id=idPlayer)
    groupsPlayer = Group.objects.filter(player=idPlayer)

    
    
    for group in groupsPlayer:
        listRanking.append(int(group.ranking))
        listOfListTrueGameModel.append(get_boolean_field_values(group.game.gameModel))

    #On veut aussi ajouter le nombre d'equipe du jeu associé au classement
    return zip(listRanking[::-1][0:CoachParams.objects.get(currentTeam=idTeam).nbMatch**2],listOfListTrueGameModel[::-1][0:CoachParams.objects.get(currentTeam=idTeam).nbMatch**2])


# Create your views here.
def ListesEquipes(request):

  # ACCES au variable de session avec request.user et on a acces aux différents attributs de l'utilisateur qui est connécté
    # objects.select_related('country', 'country_state', 'city')
    MyTeams = request.user.coachparams.team.all()
    if request.method == 'POST':
      currentTeamp = int(request.POST.get("currentTeam"))
      request.user.coachparams.currentTeam_id = currentTeamp
      request.user.coachparams.save()
      return redirect ('/NouveauMatch/')
    return render(request, 'ListesEquipes.html',{'MyTeams':MyTeams, 'equipeActuelle' : request.user.coachparams.currentTeam.id})

    #Appuie sur l'équipe et doit ajouter sur la table utilisateur sur la colonne Equipe en cours lel nom de l'équipe qu'il a séléctionné


def PlayerInGroup(idGroup)->list:
    return  [player.id for player in Player.objects.filter(groups=idGroup)]



from datetime import date

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def JoueursCree(request):

    idUser = request.user.id
    idTeam = CoachParams.objects.get(user=idUser).currentTeam.id



    idListPlayer = [ player.id for player in Player.objects.filter(team=idTeam)]

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

    idJoueur = -1 
    firstName_lastName = ''
    firstName = ''
    lastName = ''
    weight = ''
    VMA =''
    heigth = ''
    placeOnField = ''
    Remarques = ''
    AfficheJoueurs = Player
    #form = JoueursForm()
    Date_de_naissance = ''
    objectJoueur = ''
    ok=''
    age=''
    idUser = request.user.id
    currentTeamId = CoachParams.objects.get(user=idUser).currentTeam.id

    # Selection de l'id des joueurs appartenant à l'équipe
    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]
    firstNameListPlayer = [ player.firstName for player in Player.objects.filter(team=currentTeamId)]
    lastNameListPlayer = [ player.lastName for player in Player.objects.filter(team=currentTeamId)]
    postListPlayer = [ player.placeOnField for player in Player.objects.filter(team=currentTeamId)]

    idfNlNp = zip(idListPlayer,firstNameListPlayer,lastNameListPlayer,postListPlayer)

    firstName_lastName_concat = [str(player.firstName) + " " + str(player.lastName) for player in Player.objects.filter(team=currentTeamId) ]

    # Selection de l'id des joueurs appartenant à l'équipe
    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]
    if request.method == "POST":
        if not request.POST.get('heigth'): #On est dans le cas d'un VALIDER
        #if not request.POST.get('firstName_lastName'):
            firstName_lastName = request.POST.get('firstName_lastName').split(" ")
            if(request.POST.get('firstName_lastName') not in firstName_lastName_concat):
                return redirect('/Equipes/JoueursCree/')

            if(len(firstName_lastName) != 2):
                return redirect('/Equipes/JoueursCree/')

            #presenceJoueur = int(finalData[Player.objects.filter(firstName=firstName).filter(lastName=lastName)[0].id])
            if(len(firstName_lastName) == 2 ):
                objectJoueur = Player.objects.filter(firstName=str(firstName_lastName[0])).filter(lastName=str(firstName_lastName[1]))
                for joueur in objectJoueur:
                    idJoueur = joueur.id
                    firstName = str(joueur.firstName)
                    lastName = str(joueur.lastName)
                    weight = str(joueur.weight)
                    VMA = str(joueur.VMA)
                    heigth = str(joueur.heigth)
                    placeOnField = str(joueur.placeOnField)
                    Date_de_naissance = str(joueur.birth)
                    age = calculate_age(joueur.birth)
                    #Remarques = str(joueur.Remarques)
        
        
        
        
        else: #On est dans le cas d'un modifier
            if 'statPlayerModif' in request.POST:
                firstName_lastName = request.POST.get("firstName_lastName").split(" ")
                for joueur in Player.objects.filter(firstName=firstName_lastName[0]).filter(lastName=firstName_lastName[1]):
                    joueur.weight = int(request.POST.get('weight'))
                    joueur.VMA = int(request.POST.get('VMA'))
                    joueur.heigth = int(request.POST.get('heigth'))
                    if (request.POST.get('placeOnField') == 'Attaquant' or request.POST.get('placeOnField') == 'Milieu' or request.POST.get('placeOnField') == 'Defenseur' or request.POST.get('placeOnField') == 'Gardien'):
                        joueur.placeOnField = str(request.POST.get('placeOnField'))
                    #joueur.Remarques = str(request.POST.get('Remarques'))
                    joueur.save()

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

    chartPie = ''

    #Construction du dictionnaire pour la barre de rechercher

    Players = Player.objects.all()

    persons = []
   
    for player in Players:
        data = {}
        data['name']=str(str(player.firstName)+" "+str(player.lastName))
        persons.append(data)

    if request.method == 'POST':
        if 'statPlayer' in request.POST:
            if not request.POST.get('firstName_lastName'):
                return redirect('/Equipes/JoueursCree/')
            firstName_lastName = request.POST.get('firstName_lastName').strip(" ").title().split(" ") #on retire les espaces en debut et fin de chaine et on ajoute les majuscules au prénom et nom s'ils on ete oublie
            if(len(firstName_lastName)!=2):
                return redirect('/Equipes/JoueursCree/')
            objectJoueur = Player.objects.filter(firstName=str(firstName_lastName[0])).filter(lastName=str(firstName_lastName[1]))
            if not objectJoueur: 
                return redirect('/Equipes/JoueursCree/')
            for joueur in objectJoueur:
                zipRankingNumberIdgameIdgamemodel = rankingPlayer(joueur.id)
                zipRankingNumberIdgameIdgamemodel2 = rankingPlayer(joueur.id)
            for rank,number,idGame,idGameModel in zipRankingNumberIdgameIdgamemodel:
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

            # ON FAIT LES GRAPHS
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

            Date = []
            Score = []
            for date,score in ListScoreDatePlayer(joueur.id,PIPI).items():
                Date.append(date)
                Score.append(score)
            data = {}


            chartPie = get_chartPie(Score)
    return render(request, 'JoueursCrees.html', {
        'chartPie':chartPie,
        'finalData':finalData.items(),
        'idJoueur': idJoueur,
        'firstName_lastName_concat':firstName_lastName_concat,
        'idfNlNp':idfNlNp,
        'objectJoueur' : objectJoueur, 'firstName':firstName ,'lastName':lastName, 'weight' : weight, 'VMA' : VMA,'heigth' : heigth,'placeOnField' : placeOnField, 'Date_de_naissance' : Date_de_naissance,'Remarques' : Remarques,
        'scoreGoalKeeperYes':scoreGoalKeeperYes,
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

        'persons':persons})
   
def StatistiqueEquipe(request):

    idUser = request.user.id
    idTeam = CoachParams.objects.get(user=idUser).currentTeam.id



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
            dataCara[str(str(player.firstName)+str(player.lastName))] = searchScore(searchCara, rankingPlayer(player.id))
    
        dataSorted = sorted(dataCara.items(), key=lambda t: t[1])

        for name,score in dataSorted:
            listScore.append(int(score))
            listFirstName_LastName.append(str(name)) 
        ZipScoreName = zip(listScore[::-1],listFirstName_LastName[::-1])



        # ON FAIT LES GRAPHS
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



    G=[player.id for player in Players]
    MultipleChart = get_multiple_plot(G,[zip(DateGame,POPO) for k in range(len(G))])
    
    return render(request, 'FeedbackJeuxBaseTeam.html', {
        'G':G,'MultipleChart':MultipleChart,'searchCara':searchCara,'dataCara':dataCara,'ZipScoreName':ZipScoreName})


def Joueur1(request):

    idUser = request.user.id
    currentTeamId = CoachParams.objects.get(user=idUser).currentTeam.id

    # Selection de l'id des joueurs appartenant à l'équipe
    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]


    # Selection de l'id des joueurs appartenant à l'équipe
    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]
    L = [Player.objects.get(id=x) for x in idListPlayer]

    firstName_lastName_concat = [str(player.firstName) + " " + str(player.lastName) for player in Player.objects.filter(team=currentTeamId) ]

    Players = Player.objects.all()

    persons = []
   
    for player in Players:
        data = {}
        data['name']=str(str(player.firstName)+" "+str(player.lastName))
        persons.append(data)

    # Selection de l'id des joueurs appartenant à l'équipe
    idListPlayer = [ player.id for player in Player.objects.filter(team=currentTeamId)]
    if request.method == "POST":
        firstName_lastName = request.POST.get('firstName_lastName').split(" ")
        if(request.POST.get('firstName_lastName') not in firstName_lastName_concat):
            return redirect('/Equipes/Joueur1/')

        if(len(firstName_lastName) != 2):
            return redirect('/Equipes/Joueur1/')

        if(len(firstName_lastName) == 2 ):
            objectJoueur = Player.objects.filter(firstName=str(firstName_lastName[0])).filter(lastName=str(firstName_lastName[1]))
            for joueur in objectJoueur:
                idJoueur = joueur.id
                firstName = str(joueur.firstName)
                lastName = str(joueur.lastName)
                weight = str(joueur.weight)
                VMA = str(joueur.VMA)
                heigth = str(joueur.heigth)
                placeOnField = str(joueur.placeOnField)
                Date_de_naissance = str(joueur.birth)
                age = calculate_age(joueur.birth)
                 #Remarques = str(joueur.Remarques)
            return redirect ('/Equipes/Joueur2/idPlayer='+str(idJoueur))


    return render(request, 'Joueur1.html', {'L':L,'persons':persons})

import datetime

def from_dob_to_age(born):
    today = datetime.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def Joueur2(request,idPlayer):
    idPlayer = int(idPlayer)

    idUser = request.user.id
    idTeam = CoachParams.objects.get(user=idUser).currentTeam.id

    joueur = Player.objects.get(id=idPlayer)
    
    firstName = joueur.firstName
    lastName = joueur.lastName
    weight = joueur.weight
    VMA = joueur.VMA
    heigth = joueur.heigth
    placeOnField = joueur.placeOnField
    Date_de_naissance = joueur.birth
    Remarques = ''

    oi = rankingPlayer(idPlayer,idTeam)
                
    scoreGoalKeeperYes = searchScore('goalKeeperYes', rankingPlayer(idPlayer,idTeam))
    scoreGoalKeeperNo = searchScore('goalKeeperNo', rankingPlayer(idPlayer,idTeam))
    scoreOffLineYes = searchScore('offLineYes', rankingPlayer(idPlayer,idTeam))
    scoreOffLineNo = searchScore('offLineNo', rankingPlayer(idPlayer,idTeam))
    scoreSynthetiqueDry = searchScore('synthetiqueDry', rankingPlayer(idPlayer,idTeam))
    scoreSynthetiqueWet = searchScore('synthetiqueWet', rankingPlayer(joueur.id,idTeam))
    scoreStabiliseDry = searchScore('stabiliseDry', rankingPlayer(joueur.id,idTeam))
    scoreStabiliseWet = searchScore('stabiliseWet', rankingPlayer(joueur.id,idTeam))
    scoreGrassDry = searchScore('grassDry', rankingPlayer(joueur.id,idTeam))
    scoreGrassWet = searchScore('grassWet', rankingPlayer(joueur.id,idTeam))
    scoreOtherField = searchScore('otherField', rankingPlayer(joueur.id,idTeam))
    scoreGoal11 = searchScore('goal11', rankingPlayer(joueur.id,idTeam))
    scoreGoal7 = searchScore('goal7', rankingPlayer(joueur.id,idTeam))
    scoreGoalEmbut = searchScore('goalEmbut', rankingPlayer(joueur.id,idTeam))
    scoreGoalNone = searchScore('goalNone', rankingPlayer(joueur.id,idTeam))
    scoreGoalOther = searchScore('goalOther', rankingPlayer(joueur.id,idTeam))
    scoreTB1_3 = searchScore('TB1_3', rankingPlayer(joueur.id,idTeam))
    scoreTB_2 = searchScore('TB_2', rankingPlayer(joueur.id,idTeam))
    scoreTB_free = searchScore('TB_free', rankingPlayer(joueur.id,idTeam))
    scoreGoalSmall = searchScore('goalSmall', rankingPlayer(joueur.id,idTeam))

    #On fait les graphs
    chartPie = StatGliss(request,idPlayer)[0]
    graphRank = StatGliss(request,idPlayer)[1]

    

    if request.method == "POST": #On est dans le cas d'un modifier
        if 'statPlayerModif' in request.POST:
            joueur.weight = int(request.POST.get('weight'))
            joueur.VMA = int(request.POST.get('VMA'))
            joueur.heigth = int(request.POST.get('heigth'))
            joueur.placeOnField = str(request.POST.get('placeOnField'))
            joueur.save()
            return redirect('/Equipes/Joueur1/')

        
    return render(request, 'Joueur2.html', {
        'age':from_dob_to_age(joueur.birth),
        'chartPie':chartPie,
        'firstName':firstName ,'lastName':lastName, 'weight' : weight, 'VMA' : VMA,'heigth' : heigth,'placeOnField' : placeOnField, 'Date_de_naissance' : Date_de_naissance,'Remarques' : Remarques,
        'scoreGoalKeeperYes':scoreGoalKeeperYes,
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
        'score':joueur.globalScore,
        'graphRank':graphRank,
        'rankingPlayer':list(oi)
        })

def Assiduite(request):

    idUser = request.user.id
    idTeam = CoachParams.objects.get(user=idUser).currentTeam.id

    idListPlayer = [ player.id for player in Player.objects.filter(team=idTeam)]

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

    dataString = {}

    for id,abs in finalData.items():
        dataString[Player.objects.get(id=id).firstName + Player.objects.get(id=id).lastName ] = abs

    return render(request,'Assiduite.html',{'finalData':dataString.items()})
    
def ParamEquipe(request):
    idUser = request.user.id
    idTeam = CoachParams.objects.get(user=idUser).currentTeam.id

    idUser = request.user.id
    currentTeamId = CoachParams.objects.get(user=idUser).currentTeam.id
    
    obj = CoachParams.objects.get(currentTeam=currentTeamId)
    if request.method == 'POST':
        obj = CoachParams.objects.get(currentTeam=currentTeamId)
        obj.fenetre = int(request.POST.get("fenetre"))
        obj.tolerance = int(request.POST.get("tolerance"))
        obj.nbMatch = int(request.POST.get("nbMatch"))
        obj.save()

    return render(request,'ParamEquipe.html',{'obj':obj})