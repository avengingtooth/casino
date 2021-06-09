import socket
import os
import pickle
import random
import pandas as pd
import csv
from player  import Player
from games import Game


## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
ip_address = socket.gethostbyname(hostname)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((ip_address, 65535))
s.listen()

streak = 0
win = 0
restart = 1
continueGame = True
restart = True

def child(clientsocket):
    pickle_in = open("dict.pickle","rb")
    user = pickle.load(pickle_in)
    player = Player(clientsocket,user)
    player.loginExchange()
    df = pd.DataFrame.from_dict(user, orient='index')['balance'] # convert dict to dataframe
    df.to_csv('Leaderboard.csv') # write dataframe to file
    print(user)
    pickle_out = open("dict.pickle","wb")
    pickle.dump(user, pickle_out)
    pickle_out.close()
    print('\nA new child ',  os.getpid())
    gameMenu(player, user)
   
def parent():
    while True:
        clientsocket, address = s.accept()
        newpid = os.fork()
        if newpid == 0:
            child(clientsocket)
        else:
            pids = (os.getpid(), newpid)
            print("parent: %d, child: %d\n" % pids)


def gameMenu(player, user):
    restart = True
    username = player.username
    gameObject = Game(player)
    while restart == True:
        #LOBBY
        player.send("""\n
What game do you want to play?

Rules (0),
Leaderboard (1),
Blackjack (2),
Roulette (3),
Coin Flip (4),
Leave Casino (100)""")
        game = int(player.receive())
        print(game)
        #GAME LAUNCH
        if game == 0:
            isint = False
            while isint == False:
                player.send('\nWhat game do you need the rules to?' + '\n' + 'Blackjack (1), Roulette (2), Coin Flip (3)?')
                try:
                    rules = int(player.receive())
                    isint = True
                except:
                    isnit = False
                    
            if rules == 1:
                print('blackjack rules')
                player.send("""
The goal of blackjack is to get as close as possible to having of 21 points.
In this game, each card is worth the value on the card
Other than the heads which are all worth 10 points.
You start the round with 2 cards and at your turn, you can
Hit -> draw another card
Stand -> and not draw again.
If you win against the CPU the gains are 2:1
If you win with a blackjack (a score of 21) the gains are 2.5:1
""")

            elif rules == 2:
                print('roulette rules')
                player.send("""
The goal of roulette is to guess where a ball which is spinned on a roulette will land and to bet accordingly.
There are many different types of bets with different gains
These are described when you open the game.""")

            elif rules == 3:
                print('flip the coin rules')
                player.send("""
The goal of coin flip is to guess which side of the coin the coin will land on
-> Heads
-> Tails
The gains are 2:1 
""")

                player.send('Are you done?')
                msg = player.receive()
        if game == 1:
            player.send('Leaderboard: ')
            player.leaderboard()

        elif game == 2:
            player.send('Blackjack: ')
            gameObject.blackjack()
        elif game == 3:
            player.send('Roulette: ')
            gameObject.roulette()

        elif game == 4:
            player.send('Coin Flip: ')
            gameObject.coin_toss()

        elif game == 100:
            player.send('You left the casino!')
            restart = False
            os._exit(0)
parent()