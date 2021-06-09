import random
import os
import sys
user = {}
class Game:
    def __init__(self, player):
        self.restart = 'y'
        print(self.restart)
        self.player = player
        self.win = 0
        self.restart = True
        print(self.restart)

    def wantToRestart(self):
        self.player.send('Do you want to restart y/n?')
        self.restart = self.player.receive()
        print('entered restart')
        if self.restart == 'y' or self.restart == 'yes':
            print('is restarting')
            self.restart = True

        else:
            self.restart = False
            print('ending loop')
        print('exiting restart')
        print(self.restart)
        return(self.restart)
    

    # BLACKJACK
    def blackjack(self):
        print('blackjack started')
        self.restart = True
        self.cpulistloc = 0
        self.cpuhand = 0
        self.cpulistloc = 0
        self.totalpoints = 0

        self.deck = []
        for c in range(4):
            for i in range (1,10):
                self.deck.append(i)
            for tens in range(4):
                self.deck.append(10)

        while self.restart == True:
            print('entered game loop')
            self.nb_cards_taken = 2
            random.shuffle(self.deck)
            end = 0
            self.listloc = 0
            self.cpulistloc = 0
            self.cpuhand = 0
            self.betValue = self.player.set_bet()
            print('in loop')
            self.userhand()

            while self.totalpoints < 22 and end == 0:
                self.player.send('hit or stand?')
                choice = self.player.receive()

                if choice == "hit" or choice== "h":
                    self.nb_cards_taken += 1

                elif choice == "stand"or choice== "s":
                    self.player.send('stand')
                    end = 1
                else:
                    self.player.send('check ur spelling')
                self.userhand()

            self.cpulistloc = self.listloc
            while self.cpuhand < 17:
                self.cpuhandcal()

            if self.cpuhand > 21 or self.totalpoints > 21:
                if self.totalpoints > 21:
                    self.win = -1

                else:
                    self.win = 1
                    
            else:
                if self.cpuhand > self.totalpoints:
                    self.win = -1

                elif self.totalpoints == 21:
                    self.win = 1.5

                elif self.totalpoints > self.cpuhand:
                    self.win = 1
                    
                else:
                    self.win = 0
                    
            self.player.send('your hand: ' + str(self.totalpoints)+'\n')
            self.player.send('cpu hand ' + str(self.cpuhand))
            self.player.scores(self.betValue, self.win)
            self.restart = (self.wantToRestart())
    def userhand(self):
        self.listloc = 0
        self.totalpoints = 0
        for i in range (self.nb_cards_taken):
            self.player.send('\ncard ' + str(self.listloc + 1) + ': ' + str(self.deck[self.listloc]))
            self.totalpoints += int(self.deck[self.listloc])
            self.listloc += 1
        self.player.send('\ntotal points ' + str(self.totalpoints) + '\n')

    def cpuhandcal(self):
        self.cpulistloc += 1
        self.cpuhand += int(self.deck[self.cpulistloc])

    #COIN FLIP
    def coin_toss(self):
        self.restart = True
        while self.restart == True:
            betValue = self.player.set_bet()
            self.player.send('Heads or Tails?')
            bet_coin = self.player.receive()
            result_coin = random.randint(1,2)
            if bet_coin == 'heads'and result_coin == 1 or bet_coin == 'h' and result_coin == 1:
                self.player.send('The coin landed on heads')
                win = 1

            elif bet_coin == 'tails'and result_coin == 2 or bet_coin == 't' and result_coin == 2:
                self.player.send('The coin landed on tails')
                win = 1

            else:
                if result_coin == 1:
                    self.player.send('The coin landed on heads')

                else:
                    self.player.send('The coin landed on tails')

                win = -1
            
            self.player.scores(betValue, win)
            self.restart = (self.wantToRestart())

    #ROULETTE
    def roulette(self):
        self.restart = True
        while self.restart == True:
            bet_choice = 0
            while bet_choice == 0:
                isint = 0
                while isint == 0:
                    self.player.send("""
(1) straight -> bet on one number  / bet X 36
(2) basket -> bet on 0,1,2,3       / bet X 8
(3) color -> bet on red            / bet X 2
(4) color -> bet on black          / bet X 2
(5) odd/even -> bet on odd         / bet X 2
(6) odd/even -> bet on even        / bet X 2
(7) halves -> bet on 1-18          / bet X 2
(8) halves -> bet on 19-36         / bet X 2
(9) dozens -> bet on 1-12          / bet X 3
(10)dozens -> bet on 13-24         / bet X 3
(11)dozens -> bet on 25-36         / bet X 3
""")

                    try:
                        self.player.send('What type of bet do you want?')
                        bet_type = int(self.player.receive())
                        isint = 1
                    except:
                        isint = 0
                if 0 < bet_type < 14:
                    bet_choice = 1
            betValue = self.player.set_bet()

            if bet_type == 3 or bet_type == 4:
                color = random.randint(1,2)
                if color == 1:
                    self.player.send('The color is red')
                else:
                    self.player.send('The color is black')
                if color == 1 and bet_type == 3:
                    self.win = 1
                elif color == 2 and bet_type == 4:
                    self.win = 1
                else:
                    self.win = -1
                self.player.scores(betValue, self.win)

            else:
                number = random.randint(1,36)
                if bet_type == 1:
                    self.player.send('Pick a number between 1-36:')
                    decoded = int(self.player.receive())
                    if number == decoded:
                        self.win = 36
                    else:
                        self.win = -1
                elif bet_type == 5 or bet_type == 6:
                    if (number % 2) == 0:
                        odd = 1
                        self.player.send('The number ' + str(number) +(' is odd'))
                    else:
                        odd = 0
                        self.player.send('The number ' + str(number) + (' is even'))

                    if bet_type == 5 and odd == 1:
                        self.win = 1
                    elif bet_type == 6 and odd == 0:
                        self.win = 1
                    else:
                        self.win = -1

                elif bet_type == 7 or bet_type == 8:
                    if number > 18 and bet_type == 7:
                        self.win = 1
                    if number < 18 and bet_type == 8:
                        self.win = 1
                    else:
                        self.win = -1

                elif bet_type == 9 or bet_type == 10 or bet_type == 11:
                    if number < 13 and bet_type == 9:
                        self.win = 2
                    elif number > 24 and bet_type == 11:
                        self.win = 2
                    elif 12<number<25 and bet_type == 10:
                        self.win = 2
                    else:
                        self.win = -1

                elif bet_type == 2:
                    if -1 < number < 4:
                        self.win = 8
                    else:
                        self.win = -1

                self.player.send('The number landed on is ' + str(number))
                self.player.scores(betValue, self.win)
            self.restart = (self.wantToRestart())
        print(self.restart)
