# for exit()
import sys
# for telnet
import telnetlib

class Player:
	'''A class that represents a Squeezebox player.'''
	# TODO: so far it just finds itself on the server
	# TODO: need to deal with errors (currently it doesn't at all)
	
	# TODO: also make one with the ID/MAC address
	def assign(self, server, playername, port=9090):
		'''Assigns this Player object to a player on the network.
		server: the server the player is attached to
		playername: the simple name of the player, like "KrisTouch"
		port (default: 9090): the TELNET port the server is listening on
		'''
		self.server = server
		self.playername = playername
		self.port = port
		# init to None, in case we don't find the named player
		self.playerindex = None
		self.id = None # stored as byte array when we get one
		
		# we have to make sure the named player exists and get its ID.
		tn = telnetlib.Telnet(self.server, self.port) # TODO: errors
		
		# get num of players connected (starts at 1)
		tn.write(b'player count ?\n') # b makes it a byte array rather than unicode
		response = tn.read_until(b'\n')
		# this line will throw a ValueError if not an int
		playercount = int (response.split(b' ')[-1].rstrip().decode())
		
		for i in range(playercount): # iterate through players
			# see what the name for each player index is
			# the text we're sending should look like: "player name # ?"
			tn.write(b'player name ' + str(i).encode('ascii') + b' ?\n')
			
			response = tn.read_until(b'\n')
			if response.split(b' ')[-1].rstrip().decode() == self.playername:
				self.playerindex = str(i).encode('ascii');
		
		if self.playerindex == None: # we didn't find the name
			print ('Player name "' + playername + '" not found on ' + server + '.')
			tn.close()
			sys.exit() # TODO: probably a better way to do this
		# get the playerid for the playername from the server
		tn.write(b'player id ' + self.playerindex + b' ?\n')
		response = tn.read_until(b'\n')
		
		tn.close()
		
		# The id is the last space-separated "word" in the response.
		# And we have to get rid of the trailing newline.
		self.id = response.split(b' ')[-1].rstrip()