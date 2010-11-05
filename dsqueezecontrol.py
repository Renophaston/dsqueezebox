#!/usr/bin/env python
'''Control a Squeezebox from the command line.
USAGE:
    dsqueezecontrol.py <option> [...]
EXAMPLE:
    dsqueezecontrol.py -server sequoia -port 9100 -volup
'''
#### CONFIG ####
defaultserver      = 'sequoia'
defaultport        = 9090
defaultplayername  = 'KrisTouch'
defaultvolstep     = 5
#### END CONFIG ####

__author__ = "renophaston"
__date__  = "$Oct 23, 2010 10:26:55 AM$"
version = "0.1.1"

#### NOTES ####
# A .pyw extension should prevent pop-up console windows in Windows.
# TODO: remove sys, telnetlib imports after changeover to Player class
# TODO: remove extraneous funcs after changeover
# TODO: figure out a verbosity scheme
#### END NOTES ####

# for exit()
import sys
# for telnet
import telnetlib
# for command line handling
from optparse import OptionParser
# for percent encoding
#from urllib.parse import quote
import DSqueezebox # for Player class

def make_player(server, port, playername):
    '''Makes a proper player dictionary from arguments.'''
    playerindex = None # initialize this, in case something
    tn = telnetlib.Telnet(server, port)
    # get # of players connected (starting at 1, but indexes start at 0)
    tn.write(b'player count ?\n')
    response = tn.read_until(b'\n')
    playercount = int(response.split(b' ')[-1].rstrip().decode())
    # iterate through names until one matches
    for i in range(playercount):
        tn.write(b'player name ' + str(i).encode('ascii') + b' ?\n')
        response = tn.read_until(b'\n')
        if response.split(b' ')[-1].rstrip().decode() == playername:
            playerindex = str(i).encode('ascii');
    if playerindex == None: # we didn't find the name
        print ('Player name "' + playername + '" not found on ' + server + '.')
        tn.close()
        sys.exit()
    # get the playerid for the playername from the server
    tn.write(b'player id ' + playerindex + b' ?\n')
    response = tn.read_until(b'\n')
    tn.close()
    # The id is the last space-separated "word" in the response.
    # And we have to get rid of the trailing newline.
    playerid = response.split(b' ')[-1].rstrip()
    return {'server': server, 'port': port, 'playername': playername, \
            'playerid': playerid}

# The following take dictionary arguments (player) of form:
# {'server': servername, 'port': port, 'playername': playername}
def play(player):
    '''Starts a player playing if stopped or paused; otherwise does nothing.'''
    (server, port, playername, playerid) = (player['server'],
                                            player['port'],
                                            player['playername'],
                                            player['playerid'])
    if verbose: print ('Telling ' + playername + ' to play.')
    tn = telnetlib.Telnet(server, port)
    tn.write(playerid + b' play\n')
    response = tn.read_until(b'\n')
    if verbose: print ("Response from server: " + response.decode().rstrip())
    tn.close()

def pause(player):
    '''Pauses a player if playing; otherwise does nothing.'''
    (server, port, playername, playerid) = (player['server'],
                                            player['port'],
                                            player['playername'],
                                            player['playerid'])
    if verbose: print ('Pausing ' + playername + '.')
    tn = telnetlib.Telnet(server, port)
    tn.write(playerid + b' pause 1\n')
    response = tn.read_until(b'\n')
    if verbose: print ("Response from server: " + response.decode().rstrip())
    tn.close()

def unpause(player):
    '''Unpauses a player if paused; otherwise does nothing.'''
    (server, port, playername, playerid) = (player['server'],
                                            player['port'],
                                            player['playername'],
                                            player['playerid'])
    if verbose: print ('Unpausing ' + playername + '.')
    tn = telnetlib.Telnet(server, port)
    tn.write(playerid + b' pause 0\n')
    response = tn.read_until(b'\n')
    if verbose: print ("Response from server: " + response.decode().rstrip())
    tn.close()

def togglepause(player):
    '''Pauses a playing player; unpauses a paused one.'''
    # Check if paused first; don't play on stopped.
    (server, port, playername, playerid) = (player['server'],
                                            player['port'],
                                            player['playername'],
                                            player['playerid'])
    if verbose: print ('Toggling pause on ' + playername + '.')
    tn = telnetlib.Telnet(server, port)
    #tn.set_debuglevel(10)
    # first test to make sure its either playing or paused
    tn.write(playerid + b' mode ?\n')
    response = tn.read_until(b'\n')
    # mode is last "word" of response; remove newline
    mode = response.split(b' ')[-1].rstrip()
    if mode in (b'play', b'pause'):
        tn.write(playerid + b' pause\n')
        response = tn.read_until(b'\n')
        if verbose: print ("Response from server: " + response.decode().rstrip())
    else:
        print ("Not paused or playing, so I'm not toggling pause.")
    tn.close()

def stop(player):
    '''Stops a playing player; otherwise does nothing.'''
    (server, port, playername, playerid) = (player['server'],
                                            player['port'],
                                            player['playername'],
                                            player['playerid'])
    if verbose: print ('Stopping ' + playername + '.')
    tn = telnetlib.Telnet(server, port)
    tn.write(playerid + b' stop\n')
    response = tn.read_until(b'\n')
    if verbose: print ("Response from server: " + response.decode().rstrip())
    tn.close()

def skip(player, amount):
    '''Skips in a playlist by amount.
    Positive is forward, negative is backward; zero does nothing.'''
    (server, port, playername, playerid) = (player['server'],
                                            player['port'],
                                            player['playername'],
                                            player['playerid'])
    if verbose: print ('Skipping ' + str(amount) + \
                       ' tracks on ' + playername + '.')
    tn = telnetlib.Telnet(server, port)
    if amount != 0:
        tn.write(playerid + b' playlist index ' +
                 '{0:+}'.format(amount).encode('ascii') + b'\n')
    response = tn.read_until(b'\n')
    if verbose: print ("Response from server: " + response.decode().rstrip())
    tn.close()

def changevol(player, amount):
    '''Changes a players volume by amount.
    Positive is louder, negative is quieter.'''
    (server, port, playername, playerid) = (player['server'],
                                            player['port'],
                                            player['playername'],
                                            player['playerid'])
    if verbose: print ('Changing volume on ' + playername + \
                       ' by ' + str(amount) + '.')
    tn = telnetlib.Telnet(server, port)
    if amount != 0:
        tn.write(playerid + b' mixer volume ' +
                 '{0:+}'.format(amount).encode('ascii') + b'\n')
    response = tn.read_until(b'\n')
    if verbose: print ("Response from server: " + response.decode().rstrip())
    tn.close()

def main():
    # Deal with command line args
    parser = OptionParser(version="%prog " + version)
    parser.add_option("--server", dest="server",
                      default=defaultserver,
                      help="specify the SERVER [default: %default]")
    parser.add_option("--port", dest="port",
                      default=defaultport,
                      help="specify the PORT [default: %default]")
    parser.add_option("--playername", dest="playername",
                      default=defaultplayername,
                      help="specify the name of the player "
                      "[default: %default]")
    parser.add_option("--pause", dest="pause", action="store_true",
                      help="pause the player")
    parser.add_option("--play", dest="play", action="store_true",
                      help="start the player playing")
    parser.add_option("--unpause", dest="unpause", action="store_true",
                      help="unpause the player")
    parser.add_option("-t", "--togglepause", dest="togglepause",
                      action="store_true",
                      help="toggle the pause state of the player")
    parser.add_option("-s", "--stop", dest="stop", action="store_true",
                      help="stop the player")
    parser.add_option("-p", "--previous", dest="previous", action="store_true",
                      help="skip to the previous track")
    parser.add_option("-n", "--next", dest="next", action="store_true",
                      help="skip to the next track")
    parser.add_option("--volup", dest="volup", action="store_true",
                      help="raise the volume "
                      "[use --volchange for arbitrary changes]")
    parser.add_option("--voldown", dest="voldown", action="store_true",
                      help="lower the volume "
                      "[use --volchange for arbitrary changes]")
    parser.add_option("-q", "--quiet", dest="verbose", action="store_false",
                      help="suppress messages")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="encourage messages", default=verbose)

    (options, args) = parser.parse_args()

    if args: # there shouldn't be any extra args
        parser.error("Unknown arguments: " + str(args))

    # Create a Player object
    player = DSqueezebox.Player()
    if !player.attach_by_name(options.server, options.playername, options.port):
		print ("Can't find player.")
	else:
		print ("Attached to player.")

    # Go through the commands and do each that is called
    if options.play:
        player.play()
    if options.pause:
        player.pause()
    if options.unpause:
        player.unpause()
    if options.togglepause:
        player.togglepause()
    if options.stop:
        player.stop()
    if options.previous:
        player.skip(-1)
    if options.next:
        player.skip (1)
    if options.volup:
        player.changevol(defaultvolstep)
    if options.voldown:
        player.changevol(-defaultvolstep)

# This stuff only runs if this module is run by name (i.e. not imported)
if __name__ == '__main__':
    main()