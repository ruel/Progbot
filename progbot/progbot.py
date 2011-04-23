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

import re

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
	_last		= ''
	_source		= 'Anonymous'
	_target		= Channel
	_done 		= False
	_owner		= False
	_flood		= False
	_flood2		= False
	
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
		self._sock.send("NICK %s\r\n" % self.Nick )
		self._sock.send("USER %s %s %s :Progbot - Ruel.me\r\n" % (self.Nick, self.Nick, self.Nick))
		self._sock.send("JOIN %s\r\n" % self.Channel)
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
		self._checkSayChan(words)
		self._checkQuit(words)
		self._checkKick(words)
		
		if words[1] == 'PRIVMSG':
			self._checkResponse(words, self.File)
		
	def _checkOwn(self, source):
		if source.find('!') != -1:
			nameStr = source.split('!')
			self._source = nameStr[0].lstrip(':')
			if self.Owner == self._source:
				self._owner = True
		
	def _checkResponse(self, words, rfile):
		'''
			This opens responses.txt file, and checks if the array is related to the items
			at the text file. This will actually eliminate confusing if-else blocks.
		'''		
		self._target = words[2] if self.Nick != words[2] else self._source
		msg = ''
		for i in range(3, len(words)):
			msg += words[i] + ' '
		msg = msg.lstrip(':').rstrip(' ')
		fh = open(rfile, 'r')
		
		for line in fh:
			'''
				Loop through each line in the file.
			'''
			
			if line[0] == '#' or line == '' or not '~' in line:
				continue
				
			matchStr, mType, msgStr = line.split(' ~ ', 3)
			
			matchStr = matchStr.replace('%nick%', self._source)
			matchStr = matchStr.replace('%bnick%', self.Nick)
			matchStr = matchStr.replace('%source%', self._target)
			
			msgStr = msgStr.replace('%nick%', self._source)
			msgStr = msgStr.replace('%bnick%', self.Nick)
			msgStr = msgStr.replace('%source%', self._target)
			
			if '%m%' in matchStr:
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
					response = "PRIVMSG %s :%s" % (self._target, msgStr)
				elif mType == 'A':
					response = "PRIVMSG %s :%sACTION %s%s" % (self._target, chr(1), msgStr, chr(1))
				elif self._owner and mType == 'R':
					response = msgStr
				print response
				
				# Check if the last response is the same as the present
				if response == self._last:
					self._flood = True
				else:
					self._flood = False
					self._flood2 = False
					
				# Flooding Protection
				if self._flood:
					if not self._flood2:
						self._sock.send("PRIVMSG %s :Nope, you can't flood me.\r\n" % self._target)
						self._flood2 = True
				else:
					self._sock.send("%s\r\n" % response)
				
				# Copy the last response
				self._last = response
		
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
	
	def _checkSayChan(self, words):
		'''
			Talk to the specified channel.
		'''
		if words[1] == 'PRIVMSG' and words[2] == self.Nick:
			
			if 	self._owner and words[3] == ':!say':
				
				# Merge the words to one string
				full = ' '.join(words)
				
				# Check if the structure is valid
				regex = re.search(':!say #(\w+) (.+)', full)
				if regex:
					chan = regex.group(1)
					message = regex.group(2)
					self._sock.send("PRIVMSG #%s :%s\r\n" % (chan, message))
	
	def _checkKick(self, words):
		'''
			Auto rejoin when kicked
		'''
		if 	words[1] == 'KICK' and words[3] == self.Nick:
			self._sock.send("JOIN %s\r\n" % words[2])
			
'''
	END OF CODE
'''