# EloTracker
A command line tool that allows you to calculate and track Elo ratings for players for any game.

<h3>How to use this tool:</h3>
-Install the latest version of Python 3 and upgrade pip
-This project uses an API called plotly. In order to use the graph function, you have to sign up for an account and get an API key. When you get the API key, head to the bottom of the main.py file and replace the username and API_Key with your plotly username and API_Key. The API is free to use, but limited to 50 graphs per day.
-Navigate to the directory you downloaded the program to
-Next, do 'pip install plotly'
-Finally, enter 'python main.py'

<h3>Command List and Features:</h3>

<strong>help</strong> 

-Brings up a screen explaining each command


<strong>exit</strong> 

-Stops the program 


<strong>mkplayer PlayerName</strong> 

-If the Player with name 'PlayerName' does not exist, creates a new player with 1400 Elo in each existing gametype.


<strong>mkgame gametype numPlayers teamSize halfPointsAllowed('y'/'n')</strong> 

-Creates a new gametype with name 'gametype', number of players 'numPlayers', team size 'teamSize', and whether 0.5 is allowed as a score ('y' or 'n'). 

-Example command: 'mkgame chess 2 1 y' creates a gametype called 'chess' with 2 players, a team size of 1, and half points allowed in scores. 

-Invoking this command will automatically update all existing players with default 1400 Elo in this gametype. 


<strong>calc gametype</strong> 

-Prompts the user to input player names or Elo numbers, then calculates win probability as well as their post game elo

-Note that when asking for scores, valid scores are 1 or 0, or if Half points are allowed for a gametype, 0.5 


 <strong>games</strong> 
 
 -Displays a list of all existing gametypes 
 
 
 <strong>players</strong> 
 
 -Displays a list of all added players. 
 
 
<strong>info gametype</strong> 

-Displays information about a specific gametype 


<strong>delgame gametype</strong> 

-Deletes a gametype and removes player Elo from that type. 


<strong>elo PlayerName</strong> 

-Displays that player's elo for all gametypes 


<strong>elo PlayerName gametype</strong> 

-Displays a player's elo for the listed gametype 


<strong>del PlayerName</strong> 

-Deletes a player along with their match history


<strong>hist PlayerName</strong> 

-Displays a list of the games this player has played 


<strong>eloset PlayerName gametype eloNum</strong> 

-Sets 'PlayerName's' elo in 'gametype' to 'eloNum'.


<strong>seteloconst number</strong> 

-Sets the maximum points gained or lost in a match to 'number'. 


<strong>eloconst</strong> 

-Displays the current elo constant, which is the maximum number of points gained or lost in a match, 


<strong>graph playerName gametype</strong> 

-Shows a graph containing a progression of the player's elo in a gametype. 

-playerName can be substituted for 'all' to graph all players, and gametype can be substituted for 'all' to graph all gametypes 

-Note that this command requires a valid API username and Key to work, as well as a connection to the internet. The graph will open in a browser window.



<h3>About:</h3>
I made this project to teach myself Python. Except for the graph function, it's entirely command line based, but I may make an iOS or Android app for it at some point.
