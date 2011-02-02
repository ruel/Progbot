#!/usr/bin/python

'''
	Progbot.py
		-	A progressive IRC Bot written in Python

	Copyright (c) Ruel Pagayon <http://ruel.me>

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

class Progbot:
	'''
		This is the Progbot class. This functions like a regular
		IRC client. It requires a nick, server, channel, port,
		and owner nick name on initialization.
		
		Example:
		
		bot = Progbot('Progbot', 'irc.rizon.net', '#Progbot', '6667', 'Ruel')
	'''
	
	import socket
	
	Nick	= 'Progbot'
	Server	= 'irc.rizon.net'
	Channel	= '#Progbot'
	Port	= '6667'
	Owner	= 'Ruel'
	File	= 'responses.txt'
	
	_sock 		= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	_buffer 	= ''
	_source	= 'Anonymous'
	_target	= Channel
	_done 		= False
	_owner		= False
	
	def __init__(self, nck, serv, pt, chan, own):
		'''
			This will initialize the class variables.
			Acts as a constructor.
		'''
		self.Nick 		= nck
		self.Server		= serv
		self.Channel	= chan
		self.Port		= pt
		self.Owner		= own
		
	def Connect(self, verbose = False):
		'''
			This function uses sockets to connect to the remote
			IRC server. It accepts an optional variable, that makes
			the console window verbose (True or False).
		'''
		
		self._sock.connect((self.Server, int(self.Port)))
		self._sock.send("NICK " + self.Nick + "\r\n")
		self._sock.send("USER " + self.Nick + " " + self.Nick + " " + self.Nick + " :Progbot - Ruel.me\r\n")
		self._sock.send("JOIN " + self.Channel + "\r\n")
		while True:
			self._buffer = self._sock.recv(1024)
			if verbose:
				print self._buffer
			self._parseLine(self._buffer)
			if self._done:
				self._sock.close()
				break;
	
	def _parseLine(self, line):
		'''
			Parse every line, check for PING, or match responses.
		'''
		self._owner = False
		line = line.strip()
		words = line.split()
		self._checkOwn(words[0])
		self._pong(words)
		self._checkQuit(words)
		if words[1] == 'PRIVMSG':
			self._checkResponse(words, self.File)
		
	def _checkOwn(self, source):
		if source.find('!') != -1:
			nameStr = source.split('!')
			self._source = nameStr[0].lstrip(':')
			if self.Owner == self._source:
				self._owner = True
		
	def _checkResponse(self, words, file):
		'''
			This opens responses.txt file, and checks if the array is related to the items
			at the text file. This will actually eliminate confusing if-else blocks.
		'''
		
		import re
		
		self._target = words[2] if self.Nick != words[2] else self._source
		msg = ''
		for i in range(3, len(words)):
			msg += words[i] + ' '
		msg = msg.lstrip(':').rstrip(' ')
		fh = open(file, 'r')
		
		for line in fh:
			'''
				Loop through each line in the file.
			'''
			
			if line[0] == '#' or line == '' or line.find('~') == -1:
				continue
				
			config = line.split(' ~ ')
			matchStr = config[0]
			mType = config[1]
			msgStr = config[2]
			response = ''
			
			matchStr = matchStr.replace('%nick%', self._source)
			matchStr = matchStr.replace('%bnick%', self.Nick)
			matchStr = matchStr.replace('%source%', self._target)
			
			msgStr = msgStr.replace('%nick%', self._source)
			msgStr = msgStr.replace('%bnick%', self.Nick)
			msgStr = msgStr.replace('%source%', self._target)
			
			if matchStr.find('%m%') != -1:
				'''
					Check if there's a matching string.
				'''
				matchStr = matchStr.replace('%m%', '(.*)')
				match = re.search(matchStr, msg)
				
				if match:
					'''
						If there's a match
					'''
					msgStr = msgStr.replace('%m%', match.group(1).strip())
					matchStr = matchStr.replace('(.*)', match.group(1).strip())
					
			if matchStr == msg:
				'''
					Check if the case on the file, matches the current message.
				'''
				if mType == 'S':
					response = "PRIVMSG " + self._target + " :" + msgStr
				elif mType == 'A':
					response = "PRIVMSG " + self._target + " :" + chr(1) + "ACTION " + msgStr + chr(1)
				elif self._owner and mType == 'R':
					response = msgStr
				print response
				self._sock.send(response + "\r\n")
		
	def _pong(self, words):
		'''
			Respond to PING! That's one of the most important tasks to
			stay alive at the server.
		'''
		if words[0] == 'PING':
			self._sock.send("PONG " + words[1] + "\r\n")
	
	def _checkQuit(self, words):
		'''
			Quit the connection to the IRC Server.
		'''
		if words[1] == 'PRIVMSG':
			if  self._owner and words[3] == ':!q':
				self._sock.send("QUIT\r\n")
				self._done = True
		
'''
	END OF CODE
'''