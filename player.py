import os
import sys
import pickle
import pandas as pd
import smtplib
import random
from collections import OrderedDict
from operator import getitem
from games import Game
class Player():
    def __init__(self, clientsocket, user):
        self.clientsocket = clientsocket
        self.username = ""
        self.password = ""
        self.streak = 0
        self.bet = 0
        self.streak = 0
        self.win = 0
        self.logged = False
        self.username = ''
        self.user = user
        self.receiver = 0
    def pickleUser(self):
        pickle_out = open("dict.pickle","wb")
        pickle.dump(self.user, pickle_out)
        pickle_out.close()

    def findUser(self):
        founduser = False
        while founduser == False:
            self.send('Whats your username?\nIf you dont remember type (exit)')
            self.username = self.receive()
            print(self.username)
            if self.username == 'exit':
                print('exiting')
                self.loginExchange()

            else:
                try:
                    self.username = (self.user[self.username]['username'])
                    founduser = True
                    print(self.username)
                    print('username checked')
                    self.findPassword()

                except:
                    self.send('This account does not exist\n')

    def findPassword(self):
        correctpsw = False
        while correctpsw == False:
            self.send('\nwhats your password? (do not choose an important password)\nIf you dont remember type (exit)')
            self.password = self.receive()

            if self.password == self.user[self.username]['password']:
                self.send('Login successful!')
                self.balance = self.user[self.username]['balance']
                correctpsw = True
                self.logged = True
            else:
                self.send('incorrect password\n')
                if self.password == 'exit':
                    self.loginExchange()


    def checkMail(self):
        check = False
        while check == False:
            self.tries = 0
            self.send('what is your email?')
            self.receiver = self.receive()
            try:
                self.receiver = (self.user[self.receiver]['email'])
                print('this email already has an account')
                self.findPassword()

            except:
                check = False
                while check == False:
                    verify = False
                    sentCode = random.randint(1111,9999)
                    content = '\nVerification code: \n' + str(sentCode)
                    mail = smtplib.SMTP('smtp.gmail.com', 587)
                    mail.ehlo()
                    mail.starttls()
                    email = os.environ.get('CASINO_EMAIL')
                    OurPassword = os.environ.get('CASINO_PASSWORD')
                    mail.login(email, OurPassword)
                    mail.sendmail(email, self.receiver, content)
                    mail.close()
                    print(self.receiver)
                    while verify == False:
                        self.send('A verification code has been sent to your email please enter the code, if you didnt receive the mail type (exit):')
                        verification = self.receive()
                        if verification == 'exit' or self.tries == 3:
                            verify = True
                        elif int(verification) == (sentCode):
                            self.send('Your email has been verified')
                            self.user[self.username].update({'email': self.receiver})
                            verify = True
                            check = True
                            self.pickleUser()
                        self.tries += 1
                    mail.close()
         
    def logIn(self):
        print(self.user)
        while self.logged == False:
            self.findUser()
        self.send('\nWelcome to the Casino ' + self.username + ' ! Have fun')

        self.loginExchange()

    def createAccount(self):
        print(self.user)
        self.correct = 0
        confirm = ''
        self.send('pick a username:')
        self.username = self.receive()
        try:
            self.username = (self.user[self.username]['username'])
            self.send('this username is already in use is it yours y/n?')
            confirm = str(self.receive())
            if confirm == 'y':
                self.logIn()
            else:
                self.send('please choose another username:')
        except:
            self.send('your username is ' + self.username)
            self.user[self.username]={'username': self.username, 'email': self.receiver, 'balance': 500, 'password': 0, 'bet': 0}
            self.send('please choose a password:')
            password = self.receive()
            self.user[self.username].update({'password': password})
            self.checkMail()
            print (self.user[self.username])
            self.logIn()

    def loginExchange(self):
        print(self.user)
        while self.logged == False:
            self.send("""
        Do you want to create an account (1)
                        or
        Log in to an existing account(2)?""")
            try:
                createLogIn = int(self.receive())
                if createLogIn == 1:
                    self.createAccount()

                elif createLogIn == 2:
                    self.logIn()
            
            except:
                self.loginExchange()

    def send(self, msg):
        self.clientsocket.send(bytes(msg, "utf-8"))

    def receive(self):
        msg = self.clientsocket.recv(1024)
        return (msg.decode().lower())


    def restart(self):
        #RESTART
        self.send('Do you want to restart y/n?')
        restart = self.receive()
        if restart != 'y' or restart != 'yes':
            msg = self.receive()
            print('hello')
        else:
            self.gameLogic()
    
    #SET BET
    #Returns value of the bet as an int
    def set_bet(self):
        print(self.username)
        balance = self.balance
        bet = 0
        bet_placed = False
        if balance > 0:
            while bet_placed == False:
                isint = False
                while isint == False:
                    self.send(f'balance: {balance} \n')
                    try:
                        self.send('How much do you want to bet:')
                        bet = int(self.receive())
                        isint = True
                    except:
                        isint = False
                if bet > balance:
                    self.send('u broke af\n')
                else:
                    if bet!= 0:
                        self.send('gambling les go\n')
                    bet_placed = True

        else:
            self.send('u broke\n')
        return(bet)

    #SCORES
    def scores(self, bet, win):
        #LOST BET
        if win == -1:
            self.streak = 0
            self.send('\nDefeat')
        elif win == 0:
            self.send('\nTie')
        else:
            self.streak +=1
            self.send('\nVictory')

        self.balance += bet*win

        #STREAK
        if self.streak == 3:
            self.balance += 50
            self.streak = 0
        
        self.send(f'\nbalance:{self.balance} \nstreak: {self.streak}\n')
        self.user[self.username].update({'balance': self.balance})
        self.pickleUser()
        self.leaderboard()

    def leaderboard(self):
        user = OrderedDict(sorted(self.user.items(), reverse = True,
            key = lambda x: getitem(x[1], 'balance')))
        df = pd.DataFrame.from_dict(user, orient='index')['balance']
        df.to_csv('Leaderboard.csv')
        df = pd.read_csv('Leaderboard.csv')
        leaderboard = str(df)
        self.send(str(df))
