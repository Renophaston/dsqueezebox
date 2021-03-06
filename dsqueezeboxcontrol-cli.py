#!/usr/bin/env python
"""Control a Squeezebox from the command line.
"""

# for command line handling
from optparse import OptionParser
import DSqueezebox  # for Server class

# CONFIG
defaultserver = 'sequoia'
defaultplayername = 'KrisTouch'
defaultvolstep = 5
# END CONFIG

__author__ = "renophaston"
version = "0.2.2"

# NOTES
# A .pyw extension should prevent pop-up console windows in Windows.
# todo: figure out a verbosity scheme
# END NOTES


def main():
    # Deal with command line args
    parser = OptionParser(version="%prog " + version)
    parser.add_option("--server", dest="server",
                      default=defaultserver,
                      help="specify the SERVER [default: %default]")
    parser.add_option("--port", dest="port",
                      help="specify the http PORT")
    parser.add_option("--playername", dest="playername",
                      default=defaultplayername,
                      help="specify the name of the player "
                      "[default: %default]")
    parser.add_option("--playerid", "--id", dest="playerid",
                      help="specify the playerid (usually the MAC address)")
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
                      help="encourage messages", default=False)

    (options, args) = parser.parse_args()

    if args:  # there shouldn't be any extra args
        parser.error("Unknown arguments: " + str(args))

    # Create a Server object
    if options.port:
        server = DSqueezebox.Server(options.server, options.port)
    else:
        server = DSqueezebox.Server(options.server)
    
    # Get playerid
    if options.playerid:
        playerid = options.playerid
    else:
        playerid = server.get_id(options.playername)
        
    # Go through the commands and do each that is called
    if options.play:
        server.play(playerid)
    if options.pause:
        server.pause(playerid)
    if options.unpause:
        server.unpause(playerid)
    if options.togglepause:
        server.togglepause(playerid)
    if options.stop:
        server.stop(playerid)
    if options.previous:
        server.skip(playerid, -1)
    if options.next:
        server.skip(playerid, 1)
    if options.volup:
        server.change_volume(playerid, defaultvolstep)
    if options.voldown:
        server.change_volume(playerid, -defaultvolstep)


# This stuff only runs if this module is run by name (i.e. not imported)
if __name__ == '__main__':
    main()
