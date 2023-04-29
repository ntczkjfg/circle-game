from Common_Variables import *
from Game import Game

"""
Game modes:  
* Endless (current mode)
* Collect all the yellows
* Countdown timer to get all yellows
* Countdown timer, pure survival 

Powerups:  
* Additional time (For timed modes)

Work out displaying active powerups on user clearer
Add additional game over conditions to account for game modes above
Add menu
Add help screen
Better turtle icon
Better magnet icon
2x powerup icon
Placeholder icon (?)
Invulnerability needs to be displayed better
Shield radius decreases with timer until it vanishes

Fix collisions when yellow balls growing
Fix shoving balls against walls
"""

if __name__ == '__main__':
    while True:
        newGame = Game()
        newGame.start()
