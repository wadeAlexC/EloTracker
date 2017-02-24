import sys
import os
import datetime
import plotly
import plotly.plotly as py
from plotly.graph_objs import *
from plotly.exceptions import PlotlyRequestError as reqErr


#Records a match by writing it to each existing player's file
def recordMatch(teamList, teamScoreList, gametype, prevPlayerElos, newPlayerElos):
    curDir = os.path.dirname(os.path.realpath("__file__"))
    playerDir = os.path.join(curDir, "players")

    playerInd = 0
    teamInd = 0
    #For each team in the teamList
    for team in teamList:
        #And for each player on the team
        for player in team:

            #Read the player's file
            fileLines = []
            try:

                firstLine = ""
                with os.fdopen(os.open(playerDir + "/" + player.lower() + ".txt", os.O_RDONLY), "r") as playerFileReader:
                    firstLine = playerFileReader.readline()
                    fileLines = playerFileReader.readlines()

                newLineInd = firstLine.find("\n")
                if newLineInd != -1:
                    firstLine = firstLine[:newLineInd]

                for i in range(len(fileLines)):
                    newLineInd = fileLines[i].find("\n")
                    if newLineInd != -1:
                        fileLines[i] = fileLines[i][:newLineInd]

                #Update the player's elo for gametype using newPlayerElos[playerInd]
                if len(firstLine) > 0:
                    eloStrArr = firstLine.split("/")
                    for i in range(len(eloStrArr)):
                        if eloStrArr[i][:len(gametype)].lower() == gametype.lower():
                            eloStrArr[i] = gametype.capitalize() + ":" + str(newPlayerElos[playerInd])

                    firstLine = "/".join(eloStrArr)
                #

                #Get a datetime stamp and construct the string that will be written to file
                dateAndTime = datetime.datetime.now()
                timestamp = str(dateAndTime.year) + "/" + str(dateAndTime.month) + "/" + str(dateAndTime.day) + "/" + str(dateAndTime.hour)\
                                                                                        + "/" + str(dateAndTime.minute) + "/" + str(dateAndTime.second)
                if teamScoreList[teamInd] == 1:
                    fileLines.append(timestamp + ": " + str(team) + " beat " + str(teamList[:teamInd] + teamList[teamInd + 1:])
                                     + " at " + gametype + "[" + str(prevPlayerElos[playerInd]) + "/" + str(newPlayerElos[playerInd]) + "]")
                elif teamScoreList[teamInd] == 0.5:
                    fileLines.append(timestamp + ": " + str(team) + " tied " + str(teamList[:teamInd] + teamList[teamInd + 1:])
                                     + " at " + gametype + "[" + str(prevPlayerElos[playerInd]) + "/" + str(newPlayerElos[playerInd]) + "]")
                elif teamScoreList[teamInd] == 0:
                    fileLines.append(timestamp + ": " + str(team) + " lost to " + str(teamList[:teamInd] + teamList[teamInd + 1:])
                                     + " at " + gametype + "[" + str(prevPlayerElos[playerInd]) + "/" + str(newPlayerElos[playerInd]) + "]")
                else:
                    print("Unexpected error - weird team score type" + str(teamScoreList))
                    return
                #

                fileLines.insert(0, firstLine)

                #Write the changes to file
                with os.fdopen(os.open(playerDir + "/" + player.lower() + ".txt", os.O_WRONLY), "w") as playerFileWriter:
                    playerFileWriter.write("\n".join(fileLines))

                playerInd += 1
            except Exception as err:
                print(player + " not found, continuing")
                playerInd += 1
                continue
        teamInd += 1


#Calculates the chance user given players will win or lose in a given gametype, and records the data of a given match if requested.
def calculateElo(gametype, eloConst):
    #Get lists of existing players and games
    existingPlayers = getPlayers()
    existingGametypes = getGameTypes()

    # First, check to make sure the gametype entered is an existing gametype
    gameExists = False
    for game in existingGametypes:
        if gametype.lower() == game.lower():
            gameExists = True

    if not gameExists:
        print("Gametype %s not found." %(gametype))
        return
    #

    # Then, get the number of players, teamsize, and whether or not to allow half points for the gametype
    numPlayers = -1
    teamsize = -1
    allowHalfPoints = ""
    try:
        curDir = os.path.dirname(os.path.realpath("__file__"))
        gameDir = os.path.join(curDir, "gametypes")

        with os.fdopen(os.open(gameDir + "/" + gametype.lower() + ".txt", os.O_RDONLY), "r") as gameFileReader:
            gameInfoArr = gameFileReader.readline().split('/')
            numPlayers = int(gameInfoArr[0])
            teamsize = int(gameInfoArr[1])
            allowHalfPoints = gameInfoArr[2]

        if numPlayers == -1 or teamsize == -1 or allowHalfPoints == "":
            print("Unexpected Error.")
            return
    except Exception as err:
        print(err)
        return
    #

    """
    Prompts the user to enter the player names or elos they want to calculate, then creates two lists of their
    names and Elos, substituting in generated names of form "Player-n" for any input that is not a player, but is
    instead an Elo score
    """
    inputTeamList = []
    inputPlayerList = []
    inputPlayerEloList = []
    inputTeamEloList = []
    numTeams = (int)(numPlayers / teamsize) #safe cast - numplayers % teamsize is always 0
    print("Players:")
    for i in range(numTeams):
        inputTeamList.append([])
        inputTeamEloList.append(0)
        for j in range(teamsize):
            userInput = input("Enter Team %s, Player %s name or Elo:" %(str(i + 1), str(j + 1)))

            try: #if the userInput can be converted to a float, the user has input Elo instead of a name
                isEloNum = float(userInput)
                playerStr = "T" + str(i + 1) + "Player-" + str(j + 1)
                inputTeamList[i].append(playerStr)
                inputPlayerEloList.append(isEloNum)
                inputPlayerList.append(playerStr)
                inputTeamEloList[i] += isEloNum
            except:
                #Otherwise, we need to check that the player given by user input exists
                if not userInput.capitalize() in existingPlayers:
                    print("Player %s not found." %(userInput))
                    return

                #If they exist, append them to the inputTeamList and get their elo to append to the inputPlayerEloList and inputTeamEloList
                inputTeamList[i].append(userInput.capitalize())
                inputPlayerList.append(userInput.capitalize())

                #getPlayerElo(name,gametype) returns a string of the form "Gametype:Elo", so we need to grab the relevant number and convert it to a float
                #We then append this to the inputPlayerEloList
                eloNum = getPlayerElo(userInput, gametype)[0].split("\n")[1][len(gametype + ":"):]
                playerElo = float(eloNum)
                inputPlayerEloList.append(playerElo)
                inputTeamEloList[i] += playerElo

        #for each combined team elo, get the average using teamsize
        inputTeamEloList[i] /= teamsize

    """"""
    print("PLAYERS: " + str(inputPlayerList))
    print("TEAMS: " + str(inputTeamList))

    #Create a list of adjusted Player Elos for the Elo calculation:
    inputAdjTeamElos = []
    for teamElo in inputTeamEloList:
        inputAdjTeamElos.append(10 ** (teamElo / 400))
    #

    #From this, we can calculate the expected scores for the matchup:
    inputExpectTeamScore = []
    adjTeamEloSum = sum(inputAdjTeamElos)
    print("Expected Scores: ")
    for i in range(len(inputAdjTeamElos)):
        expectedScore = inputAdjTeamElos[i] / adjTeamEloSum
        inputExpectTeamScore.append(expectedScore)
        print(str(inputTeamList[i]) + ": " + str(expectedScore))
    #

    #The user now knows the probability each player will win. If they want to calculate Elo change from a win, give them the option to do so here:
    if not input("To input player scores and calculate Elo difference, enter 'cont'. Enter anything else to return to the main command line:") == "cont":
        return
    #

    #Prompt the user to enter actual scores for each team
    teamActualScores = []
    hasEnteredCorrectScore = False
    for team in inputTeamList:
        hasEnteredCorrectScore = False
        while(not hasEnteredCorrectScore):
            try:
                score = float(input("Enter score for team %s:" %(str(team))))
                if score == 0.5 and allowHalfPoints == "n":
                    print("Half points are not allowed for this gametype. Please enter a different score.")
                    continue
                if score != 0 and score != 1 and score != 0.5:
                    print("Unknown score entered. Please enter a valid score.")
                    continue

                teamActualScores.append(score)
                hasEnteredCorrectScore = True
            except:
                print("Invalid score type. Please enter a valid score.")
                continue

        #If there are two teams, the second team's score will just be 1 minus the previous team's score
        if numTeams == 2:
            teamActualScores.append(1 - teamActualScores[0])
            break
    #

    #Calculate the Elo point difference for each team given their actual scores and their expected scores
    teamEloPointDiff = []
    print("Elo point differences by team:")
    for i in range(len(inputTeamList)):
        diff = eloConst * (teamActualScores[i] - inputExpectTeamScore[i])
        teamEloPointDiff.append(diff)
        print(str(inputTeamList[i]) + ": " + str(diff))
    #

    #Find the difference in Elo for each team given original elo and point difference
    newTeamElos = []
    for i in range(len(inputTeamEloList)):
        newTeamElos.append(inputTeamEloList[i] + teamEloPointDiff[i])

    #

    #If teams are larger than 1, allocate individual player elo differences based on their proportion of average team elo
    indivPlayerEloDiff = []
    print("Individual player Elo differences:")
    if teamsize != 1:
        ind = 0
        for i in range(len(inputTeamList)):
            teamEloSum = inputTeamEloList[i] * teamsize
            for j in range(len(inputTeamList[i])):
                diff = teamEloPointDiff[i] * (inputPlayerEloList[ind] / teamEloSum)
                indivPlayerEloDiff.append(diff)
                print(inputPlayerList[ind] + ": " + str(diff))
                ind += 1

    else:
        for elo in teamEloPointDiff:
            indivPlayerEloDiff.append(elo)

    print("PLAYERS: " + str(inputPlayerList))
    print("INDIV PLAYER ELO DIFF: " + str(indivPlayerEloDiff))
    #

    #Get the new individual player Elos
    newIndivElos = []
    print("New Player Elos:")
    for i in range(len(indivPlayerEloDiff)):
        newElo = inputPlayerEloList[i] + indivPlayerEloDiff[i]
        newIndivElos.append(newElo)
        print(inputPlayerList[i] + ": " + str(newElo))
    #

    #Now, ask the user whether they want to record the information or not:
    if not input("If you would like to record these scores, enter 'rec'. Enter anything else to discard:") == "rec":
        print("Game discarded.")
        return

    #Passes the team list, scores, gametype, previous player elo list, and new player elo list
    recordMatch(inputTeamList, teamActualScores, gametype, inputPlayerEloList, newIndivElos)
    #


#Returns a string representing the player's Elo in all gametypes, or if a specific one is requested, just that one is returned.
def getPlayerElo(playerName, gametype):
    returnAllPlayers = (playerName.lower() == "all")

    toReturn = []

    playersToGet = []
    if returnAllPlayers:
        playersToGet = getPlayers()
    else:
        playersToGet.append(playerName.lower())

    try:
        curDir = os.path.dirname(os.path.realpath("__file__"))
        playerDir = os.path.join(curDir, "players")

        #For each player to get,
        for player in playersToGet:
            # Read the player file
            if os.path.isfile(playerDir + "/" + player.lower() + ".txt"):
                playerFileD = os.open(playerDir + "/" + player.lower() + ".txt", os.O_RDONLY)
                with os.fdopen(playerFileD, "r") as playerFileReader:
                    eloArr = playerFileReader.readline().split("/")

                if gametype == "":  # if no gametype was passed to the method, append a string containing all gametypes
                    eloStr = "\n".join(eloArr).rstrip()
                    if eloStr == "":
                        return ["No elo found"]
                    toReturn.append(player + ":\n" + eloStr + "\n=======")
                else: #Otherwise, append the string corresponding to the passed gametype
                    for eloListing in eloArr:
                        if eloListing[:len(gametype)].lower() == gametype.lower():
                            if eloListing == "":
                                return ["No elo found"]
                            toReturn.append(player.lower() + ":\n" + eloListing + "\n=======")

                if len(toReturn) == 0:
                    return ["Gametype %s not found" % (gametype)]


            else:
                return ["Player %s not found." % (player)]

        return toReturn

    except Exception as err:
        print(err)
        return []


#Sets the elo for player 'playerName' in game type 'gametype' to number 'eloStr'
def setElo(playerName, gametype, eloStr):
    elo = 0
    try:
        elo = float(eloStr)
        if elo <= 0: #Don't allow Elo values less than 0
            print("Elo is too low. Please enter a value above 0.")
            return

    except Exception:
        print(eloStr + " is not a number.")
        return

    #Get a list of existing gametypes, and make sure 'gametype' is in it
    gametypes = getGameTypes()
    doesGameExist = False
    for game in gametypes:
        if game.lower() == gametype.lower():
            doesGameExist = True

    if doesGameExist == False:
        print("Gametype %s not found." %(gametype))
        return
    #

    #Read the player file
    curDir = os.path.dirname(os.path.realpath("__file__"))
    playerDir = os.path.join(curDir, "players")
    lines = []

    try:
        with os.fdopen(os.open(playerDir + "/" + playerName.lower() + ".txt", os.O_RDONLY), "r") as playerFileReader:
            lines = playerFileReader.readlines()
    except Exception:
        print("Player %s not found." %(playerName))
        return

    lineArr = []
    if not lines == []:
        lineArr = lines[0].split("/")

    #Parse the Elo line, and set the elo for the correct gametype
    for i in range(len(lineArr)):
        if lineArr[i][:len(gametype)].lower() == gametype.lower():
            lineArr[i] = gametype.capitalize() + ":" + str(elo)

    #Rejoin the list and write to file
    lines[0] = "/".join(lineArr)
    newLineInd = lines[0].find("\n")
    if not newLineInd == -1:
        lines[0] = lines[0][:newLineInd]

    with os.fdopen(os.open(playerDir + "/" + playerName.lower() + ".txt", os.O_WRONLY), "w") as playerFileWriter:
        toWrite = "\n".join(lines)
        playerFileWriter.write(toWrite)


#Either adds a default elo to each player if the value of modified is 'added', or removes the elo listing if the value is anything else
def updatePlayerElos(gametype, modified):
    print("Updating elos...")
    curDir = os.path.dirname(os.path.realpath("__file__"))
    playerDir = os.path.join(curDir,"players")
    players = getPlayers()
    if modified == "added":
        # For each player, read the lines in the file
        for player in players:
            lines = []
            firstLine = ""
            with os.fdopen(os.open(playerDir + "/" + player.lower() + ".txt", os.O_RDONLY), "r") as playerFileReader:
                firstLine = playerFileReader.readline()
                lines = playerFileReader.readlines()

            #Remove the newline from the end of the first line
            newLineInd = firstLine.find("\n")
            if newLineInd != -1:
                firstLine = firstLine[:newLineInd]
            #Insert the new gametype, and insert the first line in the first index of lines
            firstLine += gametype.capitalize() + ":1400/\n"
            lines.insert(0, firstLine)
            #

            #Then, write the changes to the player file
            with os.fdopen(os.open(playerDir + "/" + player.lower() + ".txt", os.O_WRONLY), "w") as playerFileWriter:
                playerFileWriter.write("".join(lines))

    else: #modified = "removed"
        #For each player, read the lines in the file
        for player in players:
            lines = []
            with os.fdopen(os.open(playerDir + "/" + player.lower() + ".txt", os.O_RDONLY), "r") as playerFileReader:
                lines = playerFileReader.readlines()

            #If the file is not empty, split the first line with '/', separating the different gametypes
            if not lines == []:
                lineArr = lines[0].split("/")
                for line in lineArr:
                    if line[:len(gametype)].lower() == gametype.lower():
                        lineArr.remove(line) #Remove the line containing the gametype to be removed
                #Then rejoin the list and write back to the file
                lines[0] = "/".join(lineArr)

            with os.fdopen(os.open(playerDir + "/" + player.lower() + ".txt", os.O_WRONLY), "w") as playerFileWriter:
                playerFileWriter.write("".join(lines))
                playerFileWriter.truncate()


#Displays a graph showing a player's elo history in a certain gametype. If playerName is "all", all players will be graphed.
#If gametype is "all", all gametypes will be graphed
def graph(playerName, gametype):
    #Get the current existing players and games and store them in a list
    playerList = getPlayers()
    gametypes = getGameTypes()
    #

    """
    Get a list of players to plot. If the player input 'all' for playerName, playersToPlot = playerList
    Otherwise, check to see if the input player name exists, and then add that to playersToPlot
    """
    playersToPlot = []
    if playerName == "all":
        playersToPlot = playerList
    else:
        doesPlayerExist = False
        for i in range(len(playerList)):
            if playerName.lower() == playerList[i].lower():
                doesPlayerExist = True

        if not doesPlayerExist:
            print("Player %s not found." % (playerName))
            return
        else:
            playersToPlot.append(playerName)
    #

    """
    Get a list of games to plot. If the player input 'all' for gametype, gametypesToPlot = gametypes
    Otherwise, check to see if the input gametype exists, and then add that to gametypesToPlot
    """
    gametypesToPlot = []
    if gametype == "all":
        gametypesToPlot = gametypes
    else:
        doesGameExist = False
        for i in range(len(gametypes)):
            if gametype.lower() == gametypes[i].lower():
                doesGameExist = True

        if not doesGameExist:
            print("Gametype %s not found." % (gametype))
            return
        else:
            gametypesToPlot.append(gametype)
    #

    """
    playerHistArr is a multidimensional list. The first level corresponds to a player, the second level corresponds to a gametype,
    and the third level corresponds to the player's recorded history for that gametype
    """
    playerHistArr = []
    for i in range(len(playersToPlot)):
        #For each player, append a new empty list. Each index at playerHist[index] corresponds to a player
        playerHistArr.append([])
        print("PLAYER: " + str(playersToPlot[i]))
        for j in range(len(gametypesToPlot)):
            #For each gametype, append a new empty list. Each index at playerHist[playerInd][index] corresponds to a gametype
            playerHistArr[i].append([])
            print("GAME: " + str(gametypesToPlot[j]))
            #playerHistArr[playerInd][gameInd][index] now contains a list containing the entries in player history for that gametype
            histStr = getPlayerHist(playersToPlot[i], gametypesToPlot[j])
            if not histStr == "":
                playerHistArr[i][j] = histStr

    """
    Now, parse the data in playerHistArr:
    For each history entry, parse the date from the date string and append it to the xVals list
    For each entry, also parse the final Elo attained and append that to the yVals list
    """
    dataList = []
    playerInd = 0
    gameInd = 0
    for i in range(len(playerHistArr)):
        for j in range(len(playerHistArr[i])):
            if len(playerHistArr[i][j]) > 0:
                print(str(playerHistArr[i][j]))
            if playerHistArr != []:
                xVals = []
                yVals = []
                for entry in playerHistArr[i][j]:
                    entryArr = entry.split(":")
                    timeStampArr = entryArr[0].split("/")
                    scoreArr = entryArr[1].split(" ")
                    score = scoreArr[len(scoreArr) - 1].split("[")[1].split("/")[1].split("]")[0]
                    xVals.append(datetime.datetime(year=int(timeStampArr[0]), month=int(timeStampArr[1]),
                                                   day=int(timeStampArr[2]),
                                                   hour=int(timeStampArr[3]), minute=int(timeStampArr[4]),
                                                   second=int(timeStampArr[5])))
                    yVals.append(float(score))

                plot = Scatter(
                    name=playersToPlot[i] + ": " + gametypesToPlot[j],
                    x=xVals,
                    y=yVals
                )
                #For each plot created, append it to the dataList
                dataList.append(plot)

    #Finally, create a Data object and plot
    data = Data(dataList)
    print(str(data))
    py.plot(data, filename='EloPlot')


#Key/value pair class to more easily sort players by Elo
class KVPair(object):
    def __init__(self, name, elo):
        self.name = name
        try:
            self.elo = float(elo)
        except Exception as err:
            print("Error: " + err)

    def __str__(self):
        return self.name + ": " + str(self.elo)


#Returns a list of players and their Elos in gametype, ranked from highest to lowest.
#Players must have greater than or equal to minPlayed number of games in a gametype to be listed.
def rank(gametype, minPlayed):
    gametypes = getGameTypes()
    playerList = getPlayers()
    doesGameExist = False
    for game in gametypes:
        if game.lower() == gametype.lower():
            doesGameExist = True

    if not doesGameExist:
        return ["Gametype %s not found." %(gametype)]

    toReturn = []
    curDir = os.path.dirname(os.path.realpath("__file__"))
    playerDir = os.path.join(curDir, "players")

    for player in playerList:
        #For each player, get their history for a gametype. First check to make sure they have the minimum number of games played
        #Then add them to the toReturn list to be sorted by Elo
        playerHist = getPlayerHist(player, gametype)
        if not len(playerHist) < int(minPlayed):
            eloArr = getPlayerElo(player,gametype)[0].split('\n')
            eloNum = eloArr[1][len(gametype + ":"):]
            toReturn.append(KVPair(player, eloNum))

    # Somehow this understood what I wanted, and it did it, too. Nice.
    #Sorts the toReturn list based on the self.elo field of the KVPair class
    toReturn = sorted(toReturn, key=lambda player: player.elo)

    return toReturn



#Returns a list containing each entry of a player's history pertaining to a gametype
#If gametype == "all", this will contain a list of every entry in their history
def getPlayerHist(playerName, gametype):
    displayAllGametypes = gametype.lower() == "all"
    #Get a list of current existing players and games
    gametypeList = getGameTypes()
    playerList = getPlayers()

    #Determine whether the input gametype exists
    if not displayAllGametypes:
        doesGameExist = False
        for i in range(len(gametypeList)):
            if gametype.lower() == gametypeList[i].lower():
                doesGameExist = True

        if not doesGameExist:
            print("Gametype %s not found." %(gametype))
            return []
    #

    #Determine whether the inupt player exists
    doesPlayerExist = False
    for i in range(len(playerList)):
        if playerName.lower() == playerList[i].lower():
            doesPlayerExist = True

    if not doesPlayerExist:
        print("Player %s not found." %(playerName))
        return []
    #

    curDir = os.path.dirname(os.path.realpath("__file__"))
    playerDir = os.path.join(curDir, "players")

    fileLines = []
    returnLines = []
    try:
        #Read the lines from the player file, excluding the first line
        with os.fdopen(os.open(playerDir + "/" + playerName.lower() + ".txt", os.O_RDONLY), "r") as playerFileReader:
            fileLines = playerFileReader.readlines()[1:]

        #If we want to display all gametypes, simply return the list here
        if displayAllGametypes:
            return fileLines

        #Otherwise, for each entry pertaining to the gametype we are looking for, append that entry to another list
        for i in range(len(fileLines)):
            if fileLines[i].lower().find(gametype.lower()) != -1:
                returnLines.append(fileLines[i])

    except Exception as err:
        print(err)
        return []

    if len(returnLines) == 0:
        return []

    #Remove the newline characters from the returned list
    newLineInd = returnLines[len(returnLines) - 1].find("\n")
    if  newLineInd != -1:
        returnLines[len(returnLines) - 1] = returnLines[len(returnLines) - 1][:newLineInd]
    #

    return returnLines


#Removes a player file from the "players" directory
def removePlayer(playerName):
    confirm = input("You are about to delete %s. Type 'yes' to continue, and anything else to cancel." %(playerName))
    if confirm == "yes":
        curDir = os.path.dirname(os.path.realpath("__file__"))
        playerDir = os.path.join(curDir, "players")
        try:
            os.remove(playerDir + "/" + playerName.lower() + ".txt")
        except Exception:
            print("Player %s not found." %(playerName))


#Reads the gametype file, if it exists, and returns a string with the game's player number, team size, and whether or not half points are allowed in scoring
def getGametypeInfo(gametype):
    curDir = os.path.dirname(os.path.realpath("__file__"))
    gameDir = os.path.join(curDir, "gametypes")

    gameFileLines = []
    try:
        with os.fdopen(os.open(gameDir + "/" + gametype.lower() + ".txt", os.O_RDONLY), "r") as playerFileReader:
            gameFileLines = playerFileReader.readline().split("/")
    except:
        print("Gametype %s not found." %(gametype))
        return

    return "Gametype %s: \n ======= \n Number of players: %s \n Team size: %s \n Half Points: %s" \
           %(gametype, str(gameFileLines[0]), str(gameFileLines[1]), str(gameFileLines[2]))


#Removes a gametype from the "gametypes" directory, and calls updatePlayerElos with the "removed" flag
def removeGameType(gametype):
    confirm = input("You are about to delete %s. Type 'yes' to continue, and anything else to cancel." % (gametype))
    if confirm == "yes":
        curDir = os.path.dirname(os.path.realpath("__file__"))
        gamesDir = os.path.join(curDir, "gametypes")
        try:
            os.remove(gamesDir + "/" + gametype.lower() + ".txt")
            updatePlayerElos(gametype, "removed")
        except Exception:
            print("Gametype %s not found." %(gametype))


#Returns a list of existing gametypes
def getGameTypes():
    curDir = os.path.dirname(os.path.realpath("__file__"))
    gameDir = os.path.join(curDir, "gametypes")
    ret = []
    for f in os.listdir(gameDir):
        ret.append(f.title()[:f.title().find('.')])
    return ret


#Creates a new game type if it does not already exist
def makeNewGameType(name, numplayers, teamsize, allowHalfPoints):
    existingPlayers = getPlayers()
    try: #Check if numplayers and teamsize are integers, and that teamsize can be evenly divded into numplayers
        if (int(numplayers) % int(teamsize) != 0) or (int(numplayers) <= int(teamsize)):
            print("Team size must be evenly divisible into number of players")
            return

    except:
        print("Invalid syntax for command 'calc'. Please see 'help' for more information.")
        return

    try: #Check to make sure the gametype name is not a number
        float(name)
        print("Invalid character entered: game name can not be a number.")
        return
    except Exception:
        try:
            if name.lower() == "all":
                print("'all' is not a valid name for a gametype.")
                return

            for i in range(len(existingPlayers)):
                if existingPlayers[i].lower() == name.lower():
                    print("%s is already a player name. Please try a different name." %(existingPlayers[i]))
                    return

            if int(numplayers) <= 1:
                print("Invalid number of players.")
                return

            if int(teamsize) <= 0:
                print("Invalid teamsize: must be greater than or equal to 1")
                return

        except Exception:
            print("Invalid character entered. See 'help' for syntax.")
            return

        #Now create the gamefile and write information to it:
        curDir = os.path.dirname(os.path.realpath('__file__'))
        gameDir = os.path.join(curDir, "gametypes")

        allowHalfPointsStr = "y"
        if not allowHalfPoints == "y":
            allowHalfPointsStr = "n"

        if not os.path.isfile(gameDir + "/" + name.lower() + ".txt"):
            gameFile = os.open(gameDir + "/" + name.lower() + ".txt", os.O_CREAT | os.O_WRONLY)
            os.write(gameFile, str.encode(numplayers + "/" + teamsize + "/" + allowHalfPointsStr))
            os.close(gameFile)
            updatePlayerElos(name, "added")
        else:
            print("Gametype %s already exists!" % (name))
            return


#Creates a new player (if the player does not already exist) with name PlayerName and sets their Elo for all existing gametypes to 1400
def makeNewPlayer(playerName):
    gametypeList = getGameTypes()
    try:
        float(playerName)
        print("Invalid player name: player name can not be a number.")
    except Exception:
        if playerName.lower() == "all":
            print("'all' is an invalid name for a player.")
            return

        for i in range(len(gametypeList)):
            if gametypeList[i].lower() == playerName.lower():
                print("%s shares a name with a gametype. Please try a different name." %(playerName))
                return

        try:
            #Create a string with default elo containing each gametype
            eloString = ""
            gametypes = getGameTypes()
            for game in gametypes:
                eloString += game + ":1400/"
            #

            #Create a player file and write the elo string to it. Fails to write if the player already exists.
            curDir = os.path.dirname(os.path.realpath("__file__"))
            playerDir = os.path.join(curDir, "players")

            if not os.path.isfile(playerDir + "/" + playerName.lower() + ".txt"):
                playerFile = os.open(playerDir + "/" + playerName.lower() + ".txt", os.O_CREAT | os.O_WRONLY)
                os.write(playerFile, str.encode(eloString))
                os.close(playerFile)
            else:
                print("Player %s already exists!" % (playerName))
            #

        except Exception:
            print("There is already a player with that name")


#Returns a list of existing players by parsing player file titles in the "players" directory
def getPlayers():
    playerList = []
    try:
        curDir = os.path.dirname(os.path.realpath("__file__"))
        playerDir = os.path.join(curDir, "players")
        for f in os.listdir(playerDir):
            playerList.append(f.title()[:f.title().find('.')])

        return playerList
    except Exception as err:
        print(err)


#Displays a standard error message prompting the user to try their command again
def displayIncorrectCommand(command):
    print("Incorrect syntax for '%s' command. See 'help' for more information." %(command))


#Called when the user inputs 'help'. Prints a list of all possible commands and an explanation for each
def printCommands():
    print("COMMANDS: \n========")
    print("'help' - brings up this screen \n =")
    print("'exit' - stops the program \n =")
    print("'calc gametype' - Prompts the user to input player names or Elo numbers, then calculates win probability as well as their post game elo")
    print("-Note that when asking for scores, valid scores are 1 or 0, or if Half points are allowed for a gametype, 0.5 \n =")
    print("'mkplayer PlayerName' - If the Player with name 'PlayerName does not exist, creates a new player with 1400 Elo in each existing gametype. \n =")
    print("'games' - Displays a list of all existing gametypes \n =")
    print("'info gametype' - Displays information about a specific gametype \n =")
    print("'mkgame gametype numPlayers teamSize halfPointsAllowed('y'/'n')' - Creates a new gametype with name 'gametype', number of players" +
          " 'numPlayers', team size 'teamSize', and whether 0.5 is allowed as a score ('y' or 'n'). ")
    print("-Example command: 'mkgame chess 2 1 y' creates a gametype called 'chess' with 2 players, a team size of 1, and half points allowed in scores. ")
    print("-Invoking this command will automatically update all existing players with default 1400 Elo in this gametype. \n =")
    print("'delgame gametype' - Deletes a gametype and removes player Elo from that type. \n =")
    print("'players' - Displays a list of all added players. \n =")
    print("'elo PlayerName' - Displays that player's elo for all gametypes \n =")
    print("'elo PlayerName gametype' - Displays a player's elo for the listed gametype \n =")
    print("'elo all' - Displays every existing player's elo separated by player name \n =")
    print("'rank gametype' - Displays every existing player and their elo in gametype, ranked from highest to lowest. \n")
    print("-A player must have minimum 5 games player in gametype to be listed. \n =")
    print("'rank gametype minPlayed' - Does the same as 'rank gametype', but with minimum minPlayed games to be listed. \n =")
    print("'del PlayerName' - Deletes a player along with their match history \n =")
    print("'hist PlayerName' - Displays a list of the games this player has played \n =")
    print("'eloset PlayerName gametype eloNum' - Sets 'PlayerName's' elo in 'gametype' to 'eloNum'. \n =")
    print("'seteloconst number' - Sets the maximum points gained or lost in a match to 'number'. \n =")
    print("'eloconst' - Displays the current elo constant, which is the maximum number of points gained or lost in a match, \n =")
    print("'graph playerName gametype' - Shows a graph containing a progression of the player's elo in a gametype. \n")
    print("-playerName can be substituted for 'all' to graph all players, and gametype can be substituted for 'all' to graph all gametypes \n =")


"""
Waits for player input, parses the command or list of commands they input, and makes a response.
"""
def playerInput(eloConst):
    while True:
        commandArr = input("Enter a command, or multiple commands seperated by '|'. Enter 'help' for the command list\n").lower().split("|")
        exitProgram = False

        #For each command in the list they entered, parse and respond
        for command in commandArr:
            splitCommand = command.split(" ")

            #Commands:
            if splitCommand[0] == "help":
                printCommands()
            elif splitCommand[0] == "exit":
                #possibly make sure everything is saved? idk
                print("ending...")
                exitProgram = True
                break
            elif splitCommand[0] == "mkgame":
                if len(splitCommand) > 4:
                    makeNewGameType(splitCommand[1], splitCommand[2], splitCommand[3], splitCommand[4])
                elif len(splitCommand) > 3:
                    makeNewGameType(splitCommand[1], splitCommand[2], splitCommand[3], "")
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "calc":
                if len(splitCommand) < 2:
                    displayIncorrectCommand(splitCommand[0])
                else:
                    calculateElo(splitCommand[1], eloConst)
            elif splitCommand[0] == "elo": #pull up information on a player if the player exists
                if len(splitCommand) > 1:
                    if len(splitCommand) > 2:
                        for elo in getPlayerElo(splitCommand[1], splitCommand[2]):
                            print(elo)
                    else:
                        for elo in getPlayerElo(splitCommand[1], ""):
                            print(elo)
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "mkplayer":
                if len(splitCommand) > 1:
                    makeNewPlayer(splitCommand[1])
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "players":
                print(getPlayers())
            elif splitCommand[0] == "games":
                print(getGameTypes())
            elif splitCommand[0] == "info":
                if len(splitCommand) > 1:
                    print(getGametypeInfo(splitCommand[1]))
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "rank": #TODO fix amount of games played
                if len(splitCommand) > 2:
                    for player in rank(splitCommand[1], splitCommand[2]):
                        print(str(player))
                elif len(splitCommand) > 1:
                    for player in rank(splitCommand[1], 5):
                        print(str(player))
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "graph":
                if len(splitCommand) > 2:
                    try:
                        graph(splitCommand[1], splitCommand[2])
                    except reqErr as err:
                        print("Error: check internet connection.")
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "del":
                if len(splitCommand) > 1:
                    removePlayer(splitCommand[1])
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "delgame":
                if len(splitCommand) > 1:
                    removeGameType(splitCommand[1])
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "hist":
                toPrint = []
                if len(splitCommand) > 2:
                    toPrint = ("".join(getPlayerHist(splitCommand[1], splitCommand[2])))
                elif len(splitCommand) > 1:
                    toPrint = ("".join(getPlayerHist(splitCommand[1], "all")))
                else:
                    displayIncorrectCommand(splitCommand[0])
                if len(toPrint) > 0:
                    print(str(toPrint))
            elif splitCommand[0] == "eloset":
                if len(splitCommand) > 3:
                    setElo(splitCommand[1], splitCommand[2], splitCommand[3])
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "seteloconst":
                if len(splitCommand) > 1:
                    try:
                        eloConst = int(splitCommand[1])
                    except Exception:
                        print("That is not a valid number.")
                else:
                    displayIncorrectCommand(splitCommand[0])
            elif splitCommand[0] == "eloconst":
                print("Maximum number of points gained or lost in a match: " + str(eloConst))
            else:
                print("That is not a command.")
            #\Commands

        if exitProgram:
            break


#Checks for any command line arguments, and if an integer was input, sets the elo constant to that integer
def main(eloConst):
    if not (len(sys.argv) > 1):
        print("No argument found. K value set to default: " + str(eloConst))
    else:
        try:
            eloConst = int(sys.argv[1])
        except Exception:
            eloConst = input("That is not a number! Please enter a value for K:")

    playerInput(eloConst)

#First, check to make sure the gametypes and players directories are there:
if not os.path.exists("gametypes"):
    os.mkdir("gametypes")
if not os.path.exists("players"):
    os.mkdir("players")
#Invokes main() with a value of 100 for the eloConstant, and sets up username and api key for plotly graphing utility
plotly.tools.set_credentials_file(username='wadeAlexPy', api_key='dzF6qiIM7yMm017Pi5Fx')
main(100)
