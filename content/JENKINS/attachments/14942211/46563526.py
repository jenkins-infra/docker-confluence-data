##############################################################
# Delete the hudson application server in WebSphere Application Server
# that was created by the createHudsonServer.py script.
#
# Author: Chris Graham - chrisgwarp@gmail.com
#
##############################################################

print "------------------------------------------------------------------------"
print "deleteHudsonServer.py - Started"

execfile('wsadminlib.py')

#enableDebugMessages()

##############################################################
# Program Entry Point
##############################################################

successful = 1

try:
    # Specify the node and server names to be used.
    nodeName = "inet3Node01"
    serverName = "hudson"

    print "Stopping Server: %s on %s" % (serverName, nodeName)
    stopServer( nodeName, serverName )

    print "Deleting Hudson Virtual Host: %s" % (serverName)
    deleteVirtualHost( serverName )

    print "Deleting Hudson Server: %s on %s" % (serverName, nodeName)
    deleteServerByNodeAndName( nodeName, serverName )

    # Now save the configuration
    saveAndSync()

    print "------------------------------------------------------------------------"
    print "deleteHudsonServer.py - Finished - SUCCESSFULLY"
    print "------------------------------------------------------------------------"

except:
    print "------------------------------------------------------------------------"
    print "deleteHudsonServer.py - Finished - UNSUCCESSFULLY!!!"
    print "------------------------------------------------------------------------"
    successful = 0

if successful == 0:
    raise RuntimeError("FAILED")
