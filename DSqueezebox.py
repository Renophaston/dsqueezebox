version = "0.2.1"

#### IMPORTS ####
import re

# for json
import json
import urllib.request

class Server:
    '''A class that interfaces with a Squeezebox server.'''
    # TODO: deal with errors (both exceptions and server responses)
    
    def __init__(self, servername='localhost', httpport=9000):
        self.servername = servername
        self.httpport = httpport
        self.set_jsonurl()

    ## PUBLIC methods
    
    def query_server(self, *args):
        '''Sends a JSON whatever to the server and returns the response as a JSONy dictionary.
        If the first arg is the playerid, it'll treat it as such, otherwise
        it'll just talk to the server.
        '''
        if re.search('^\w\w:\w\w:\w\w:\w\w:\w\w:\w\w$', args[0]):
            # we're affecting a player
            querydata = json.dumps({'id':1, 'method':'slim.request', 'params':[args[0], list(args)[1:]]})
        else:
            # we're just talking to the server
            querydata = json.dumps({'id':1, 'method':'slim.request', 'params':['-', list(args)]})
        
        #print (querydata)
        req = urllib.request.Request(self.jsonurl, querydata.encode())
        response = urllib.request.urlopen(req)
        
        return json.loads(response.read().decode())
        
    def set_server(self, servername, port=-1):
        '''Set server to servername; if port is omitted, it isn't changed.'''
        self.servername = servername
        if type(port) == int and 0 <= port <= 65535:
            self.httpport = port
        self.set_jsonurl()
        
    def get_id(self, playername):
        '''Takes a name ("JohnsTouch") and returns the playerid or False if it can't find it.'''
        response = self.query_server('players', 0, 99)
        for player in response['result']['players_loop']:
            if player['name'] == playername:
                return player['playerid']
        return False
    
    def get_name(self, playerid):
        '''Takes a playerid and returns the name or False.'''
        response = self.query_server('players', 0, 99)
        for player in response['result']['players_loop']:
            if player['playerid'] == playerid:
                return player['name']
        return False
    
    def get_player_mode(self, playerid):
        '''Returns player mode, e.g. 'pause', 'play', etc.'''
        response = self.query_server(playerid, 'mode', '?')
        return response['result']['_mode']

    def play(self, playerid):
        self.query_server(playerid, 'play')
        
    def pause(self, playerid):
        self.query_server(playerid, 'pause', 1)
        
    def unpause(self, playerid):
        self.query_server(playerid, 'pause', 0)
    
    def stop(self, playerid):
        self.query_server(playerid, 'stop')
    
    def togglepause(self, playerid):
        '''If player is paused or playing, toggle pause state.'''
        playermode = self.get_player_mode(playerid)
        if playermode == 'pause' or playermode == 'play':
            self.query_server(playerid, 'pause')
    
    def skip(self, playerid, amount):
        '''Skips amount of songs. Negative skips backward.'''
        if amount != 0:
            self.query_server(playerid, 'playlist', 'index', '{0:+}'.format(amount))
    
    def change_volume(self, playerid, amount):
        '''Changes volume by amount (i.e. not _to_ amount).'''
        if amount != 0:
            self.query_server(playerid, 'mixer', 'volume', '{0:+}'.format(amount))
        
    ## PRIVATE methods
        
    def set_jsonurl(self):
        self.jsonurl = 'http://' + self.servername + ':' + str(self.httpport) + '/jsonrpc.js'
