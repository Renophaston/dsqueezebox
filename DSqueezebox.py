# for exit()
import sys
# for telnet
import telnetlib

class Player:
	'''A class that represents a Squeezebox player.'''
	# TODO: so far it just finds itself on the server
	
	def __init__(self, server, port, playername):
		self.server = server
		self.port = port
		self.playername = playername
		# init to None, in case we don't find the named player
		self.playerindex = None
		
		# we have to make sure the named player exists and get its ID.
		tn = telnetlib.Telnet(self.server, self.port)
		
		# get num of players connected (starts at 1)
		tn.write(b'player count ?\n') # b makes it a byte array rather than unicode
		response = tn.read_until(b'\n')
		# this line will throw a ValueError if not an int
		playercount = int (response.split(b' ')[-1].rstrip().decode())
		for i in range(playercount): # iterate through players
			# see what the name for each player index is
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
		self.playerid = response.split(b' ')[-1].rstrip()