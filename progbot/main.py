#!/usr/bin/python

'''
	Main file, Progbot's implementation. Most of Progbot's functions
	are found on the class. So this is pretty self-explanatory.
'''

from progbot import Progbot

def main():
	'''
		I want to connect to irc.rizon.net, with the following options:
	'''
	
	ircNick 	= 'Progbot'
	ircServ 	= 'irc.rizon.net'
	ircPort 	= '6667'
	ircChan 	= '#Progbot'
	ircOwner 	= 'Ruel'
	fileName	= 'responses.txt'
	
	bot = Progbot(ircNick, ircServ, ircPort, ircChan, ircOwner)
	bot.File = fileName
	bot.Connect(True);
	
if __name__ == '__main__':
	main()