# ScrabbleBot

## User Guide ##

Start a new event by typing `!reset`.  Warning, this deletes all game results recorded for the current event.

Next, players sign in with `!signin` and sign out with `!signout`.  This toggles their `p.attend` status.

`!start` is used to begin an event once all players have signed in, it will generate byes and split players into groups if necessary.

Players report their scores using `!result p1 s1 p2 s2`

To see the current standings, anyone can type `!summary`

Finally, to see the game-by-game results, anyone can type `!getresults`

## Developer Guide: Details of data structures in club.py ##

### The actual data structures ###

1. `players`  
  This is a list of ALL players who play at the club.  A new player that joins a tournament will have to get added to this list.  The list is maintained in human readable players.json, so you can add one with the gui or with a text editor.  It is a list of Player objects.  
  See the start_event() (!start) function.
  
1. `results`  
  This is a dictionary { id : Result object } .  Think of a result as a tally slip for one game to record who won, who played, and what the score was.   The results are numbered so there's a convenient way to delete just one of them in case it is misentered.  
  If a player has a bye, then the result is recorded as a game vs BYE with a score of 0-0. 
    
1. `byes`  
   This is a list of player names, ie `byes = ["P7","P2","P3"]`  The nth entry represents the `player.name` who has the nth bye.  In this example of a three round event, P7 has the first bye, P2 the next, and P3 the final.
   
### The virtual data structures ###

1. `ScoreCard`  
   This represents a summary of one player's experience in the current event.  It has a summary of their games, their total wins and total spread etc.  A scorecard knows who they have played already.  ScoreCards are recomputed when needed by scanning all the `results` data, via the `get_scorecards()` function.
  
1. `attendees`  
  This is not a data structure per se, but it's a filtered subset of players.  Players who have joined the current tournament are marked by `p.attend = True`.  It is computed on-the-fly when needed.
  
#   W o r d _ G a m e _ D I s c o r d _ B o t  
 