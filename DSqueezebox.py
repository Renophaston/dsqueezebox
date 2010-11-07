# for telnet
import telnetlib

class DSPlayer:
    '''A class that represents a Squeezebox player.'''
    # TODO: need to deal with errors (currently it doesn't at all)
    
    def __init__(self):
        self.playername = None
        self.playerid = None
        self.server = None
        self.playerid = None # stored as byte array when we get one
        
    def attach_by_name(self, server, playername, telnetport=9090, httpport=9000):
        '''Assigns this Player object to a player on the network.
        server: the server the player is attached to
        playername: the simple name of the player, like "KrisTouch"
        telnetport (default: 9090): the TELNET port the server is listening on
        Returns None if it can't find the player.
        '''
        self.server = server
        self.playername = playername
        self.set_telnetport(telnetport)
        self.set_httpport(httpport)
        # init to None, in case we don't find the named player
        self.playerindex = None
        
        # we have to make sure the named player exists and get its ID.
        tn = telnetlib.Telnet(self.server, self.telnetport) # TODO: errors
        
        # get num of players connected (starts at 1)
        tn.write(b'player count ?\n')
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
            return None;

        # get the playerid for the playername from the server
        tn.write(b'player id ' + self.playerindex + b' ?\n')
        response = tn.read_until(b'\n')
        
        tn.close()
        
        # The id is the last space-separated "word" in the response.
        # And we have to get rid of the trailing newline.
        self.playerid = response.split(b' ')[-1].rstrip()
        return True

    def attach_by_id(self, server, playerid, telnetport=9090, httpport=9000):
        '''Assigns this Player object to a player on the network.
        server: the server the player is attached to
        id: the id of the player; usually the MAC address
        telnetport (default: 9090): the TELNET port the server is listening on
        Returns None if it can't find the player.
        '''
        self.server = server
        self.set_telnetport(telnetport)
        self.set_httpport(httpport)
        
        # the playerid is stored as a byte array
        if type(playerid) == bytes:
            self.playerid = playerid
        elif type(playerid) == str:
            self.playerid = playerid.encode('ascii')
        else:
            return False
        
        # we have to make sure the named player exists and get its ID.
        tn = telnetlib.Telnet(self.server, self.telnetport) # TODO: errors
        
        # we make sure the player exists and get its playername
        tn.write(b'player name ' + self.playerid + b' ?\n')
        response = tn.read_until(b'\n')
        if len((response.split(b' '))) == 3: # we didn't find it
            print ('Cannot find a player with id ' + self.playerid.decode() + '.')
            return None
        # otherwise, we have the name:
        self.playername = response.split(b' ')[-1].rstrip().decode()
        
        tn.close()
        return True
        
    def is_attached(self):
        '''Returns True if attached to a player, otherwise returns False'''
        if self.playername and self.playerid:
            return True
        else:
            return False
            
    def set_telnetport(self, newport):
        if type(newport) == int and 0 <= newport <= 65535:
            self.telnetport = newport
            return True
        return False
        
    def set_httpport(self, newport):
        if type(newport) == int and 0 <= newport <= 65535:
            self.httpport = newport
            return True
        return False
            
    def play(self):
        '''Starts a player playing if stopped or paused; otherwise does nothing.'''
        if self.is_attached():
            print ('Telling ' + self.playername + ' to play.')
            tn = telnetlib.Telnet(self.server, self.telnetport)
            tn.write(self.playerid + b' play\n')
            response = tn.read_until(b'\n')
            print ("Response from server: " + response.decode().rstrip())
            tn.close()
            return True
        else:
            return False
    
    def pause(self):
        '''Pauses a player if playing; otherwise does nothing.'''
        if self.is_attached():
            print ('Pausing ' + self.playername + '.')
            tn = telnetlib.Telnet(self.server, self.telnetport)
            tn.write(self.playerid + b' pause 1\n')
            response = tn.read_until(b'\n')
            print ("Response from server: " + response.decode().rstrip())
            tn.close()
            return True
        else:
            return False
    
    def unpause(self):
        '''Unpauses a player if paused; otherwise does nothing.'''
        if self.is_attached():
            print ('Unpausing ' + self.playername + '.')
            tn = telnetlib.Telnet(self.server, self.telnetport)
            tn.write(self.playerid + b' pause 0\n')
            response = tn.read_until(b'\n')
            print ("Response from server: " + response.decode().rstrip())
            tn.close()
            return True
        else:
            return False
            
    def toggle_pause(self):
        '''Pauses a playing player; unpauses a paused one.'''
        if self.is_attached():
            print ('Toggling pause on ' + self.playername + '.')
            tn = telnetlib.Telnet(self.server, self.telnetport)
            
            # first test to make sure its either playing or paused
            tn.write(self.playerid + b' mode ?\n')
            response = tn.read_until(b'\n')
            # mode is last "word" of response; remove newline
            mode = response.split(b' ')[-1].rstrip()
            if mode in (b'play', b'pause'): # it's playing or paused
                tn.write(self.playerid + b' pause\n') # toggle pause
                response = tn.read_until(b'\n')
                print ("Response from server: " + response.decode().rstrip())
            else:
                print ("Not paused or playing, so I'm not toggling pause.")
            tn.close()
            return True
        else:
            return False

    def stop(self):
        '''Stops a playing player; otherwise does nothing.'''
        if self.is_attached():
            print ('Stopping ' + self.playername + '.')
            tn = telnetlib.Telnet(self.server, self.telnetport)
            tn.write(self.playerid + b' stop\n')
            response = tn.read_until(b'\n')
            print ("Response from server: " + response.decode().rstrip())
            tn.close()
            return True
        else:
            return False
    
    def skip(self, amount):
        '''Skips in a playlist by amount.
        Positive is forward, negative is backward; zero does nothing.'''
        if self.is_attached():
            print ('Skipping ' + str(amount) + ' tracks on ' + self.playername + '.')
            if amount != 0:
                tn = telnetlib.Telnet(self.server, self.telnetport)
                tn.write(self.playerid + b' playlist index ' +
                        '{0:+}'.format(amount).encode('ascii') + b'\n')
                response = tn.read_until(b'\n')
                print ("Response from server: " + response.decode().rstrip())
                tn.close()
            return True
        else:
            return False
            
    def change_vol(self, amount):
        '''Changes a players volume by amount.
        Positive is louder, negative is quieter.'''
        if self.is_attached():
            print ('Changing volume on ' + self.playername + ' by ' + str(amount) + '.')
            if amount != 0:
                tn = telnetlib.Telnet(self.server, self.telnetport)
                tn.write(self.playerid + b' mixer volume ' +
                        '{0:+}'.format(amount).encode('ascii') + b'\n')
                response = tn.read_until(b'\n')
                print ("Response from server: " + response.decode().rstrip())
                tn.close()
            return True
        else:
            return False