##############################################################
# Create an application server in WebSphere Application Server
# that is suitable to run Hudson.
#
# This script is written to create a server which is then
# configured to run Hudson.
# This has been sucessfully tested with multiple versions
# of Hudson under WAS 6.1 on AIX.
#
# Author: Chris Graham - chrisgwarp@gmail.com
#
##############################################################

print "------------------------------------------------------------------------"
print "createHudsonServer.py - Started"

execfile('wsadminlib.py')

#enableDebugMessages()

##############################################################
# Program Entry Point
##############################################################

#
# This script makes the following assumptions, if they are different, then edit as necessary.
#
# Description.                                  variable                default value
# ------------------------------------------    -------------------     ---------------
# Node Name on which server will be created.    nodeName                localhostNode01
# Appliction Server name.                       serverName              hudson
# Hudson Home Directory                         hudsonHome              /hudson/hudson

successful = 1

try:
    ##################################################
    # Configuration Variables. Edit as necessary.
    ##################################################
    
    # Specify the node and server names to be used.
    nodeName    = "localhostNode01"
    serverName  = "hudson"

    # Hudson Home directory, where it keeps it's configuration data and jobs.
    hudsonHome  = "/hudson/hudson"

    ##################################################
    # Configuration Script
    ##################################################

    # Now, create the server.
    print "Creating Hudson Server: %s on %s" % (serverName, nodeName)
    result = createServer( nodeName, serverName )
    print "Created Server: " + result

    # Need to set a custom property to enable filters.
    propertyName = "com.ibm.ws.webcontainer.invokefilterscompatibility"
    propertyValue = "true"

    print "Setting custom property: %s to %s" % (propertyName, propertyValue)
    setWebContainerCustomProperty( nodeName, serverName, propertyName, propertyValue )

    # Create a virtual host for it.
    print "Creating Virtual Host: %s" % (serverName)
    createVirtualHost( serverName )
    
    # Add a host alias for it.
    # You may need to edit this section, especially if you wish to add in multiple Virtual Host Aliases.
    # Eg: Add a virtual host entry for a server called hudson.yourcompany.com on IP address 10.1.2.3 on port 80.
    # Here we add both the Name and IP address as aliases.
    #print "Adding Host Alias: %s - 10.1.2.3:80" % (serverName)
    #addHostAlias( serverName, "10.1.2.3", 80 )
    #print "Adding Host Alias: %s - hudson.yourcompany.com:80" % (serverName)
    #addHostAlias( serverName, "hudson.yourcompany.com", 80 )
    #
    print "Adding Host Alias: %s - *:80" % (serverName)
    addHostAlias( serverName, "*", 80 )
    
    # Set the default virtual host name for the web container.    
    print "Setting Default Virtual Host Name: %s " % (serverName)
    setWebContainerDefaultVirtualHostName(nodeName, serverName, serverName)

    # Set the HUDSON_HOME and user.timezone properties. These are done as JVM generic arguments.
    print "Setting JVM Properties"
    setJvmProperty(nodeName, serverName, "genericJvmArguments", "-DHUDSON_HOME=" + hudsonHome + " -Duser.timezone=Australia/Sydney")

    # Now save the configuration
    print "Saving Changes..."
    saveAndSync()

    print "------------------------------------------------------------------------"
    print "createHudsonServer.py - Finished - SUCCESSFULLY"
    print "------------------------------------------------------------------------"

except:
    print "------------------------------------------------------------------------"
    print "createHudsonServer.py - Finished - UNSUCCESSFULLY!!!"
    print "------------------------------------------------------------------------"
    successful = 0

if successful == 0:
    raise RuntimeError
