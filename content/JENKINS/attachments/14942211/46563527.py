##############################################################
# Install the hudson web application into the hudson server.
#
# This script needs to be passed one parameter, the path
# to the hudson.war to be installed.
#
# It then reads the version information from the war file, and
# uses that information to construct a meaningful name that
# is then displayed in the WAS Admin Console. Rather than just
# a generic 'hudson', I prefer to have the version information
# in there as well. So the application name will be similar to
# 'hudson-1_345_war'. Interestingly enough, that is what
# Hudson Issue 7403 addresses, but was not with consequence.
# Due to Hudson Issue 7403, the web module name has changed,
# it now has the version number embedded in it.
# For details see: http://issues.hudson-ci.org/browse/HUDSON-7304
# For Hudson versions <1.374, the web module name was always 'Hudson'.
# For Hudson versions >= 1.374, it is now 'Hudson v1.xxx'.
# The actual value needs to be used to allow us to map the hudson
# web module to the app server (-MapModulesToServers) and virtual
# host (-MapWebModToVH).
# This script now reads the web.xml file, loads it into DOM,
# and then extracts the value.
# This script will also delete any applications that start with
# 'hudson' before it installs the new war file.
#
# Assumptions:
#       1. An application server called 'hudson' has been created.
#          This can be done using the createHudsonServer.py script.
#       2. There is a webserver defined to the WAS stack.
#          It is called 'webserver'
#       3. There is a virtual host called 'hudson'.
#          This can be done using the createHudsonServer.py script.
#
# Most of these values can be edited below, to relect your settings.
#
# This has been tested under WAS 6.1.0.19 on AIX.
#
# Author: Chris Graham - chrisgwarp@gmail.com
#
##############################################################

print "------------------------------------------------------------------------"
print "installHudson.py - Started"

execfile('wsadminlib.py')

#enableDebugMessages()

def setClassloaderToParentLastOnly(appname):
    deployments = AdminConfig.getid("/Deployment:%s/" % (appname) )
    deploymentObject = AdminConfig.showAttribute(deployments, "deployedObject")
    #AdminConfig.modify(deploymentObject, [['warClassLoaderPolicy', 'SINGLE']])
    classloader = AdminConfig.showAttribute(deploymentObject, "classloader")
    AdminConfig.modify(classloader, [['mode', 'PARENT_LAST']])
    modules = AdminConfig.showAttribute(deploymentObject, "modules")
    arrayModules = modules[1:len(modules)-1].split(" ")
    for module in arrayModules:
        if module.find('WebModuleDeployment') != -1:
            AdminConfig.modify(module, [['classloaderMode', 'PARENT_LAST']])

def getImplentationVersion(zipFile):
    """Use the JarFile class (avoids ZipFile issues with signing) to extract the Implentation-Version information from the MANIFEST.MF file."""

    print "------------------------------------------------------------------------"
    print "getImplentationVersion:"
    print "    zipFile          = %s" % zipFile

    implementationVersion = None

    jarFile = java.util.jar.JarFile(zipFile)
    manifest = jarFile.getManifest()
    implementationVersion = manifest.getMainAttributes().getValue("Implementation-Version")
    jarFile.close()

    print "    Version          = %s" % repr(implementationVersion)

    return implementationVersion

def getWebAppDisplayName(zipFile):
    """Use the JarFile class (avoids ZipFile issues with signing) to get an InputStream that allows us to read WEB-INF/web.xml to get the 'display-name' XML value."""

    from javax.xml.parsers import DocumentBuilderFactory

    print "------------------------------------------------------------------------"
    print "getWebAppDisplayName:"
    print "    zipFile          = %s" % zipFile

    displayName = None

    jarFile = java.util.jar.JarFile(zipFile)
    webEntry = jarFile.getJarEntry("WEB-INF/web.xml")
    if webEntry == None:
        print "Unable to load web.xml."
    else:
        # Load the web.xml file.
        factory = DocumentBuilderFactory.newInstance()
        builder = factory.newDocumentBuilder()
        # load and parse it.
        doc = builder.parse(jarFile.getInputStream(webEntry))
        # get all of the 'display-name' elements, there should only be one.
        nodeList = doc.getElementsByTagName("display-name")
        if nodeList.getLength() == 1:
            # get the node itself
            node = nodeList.item(0)
            # and it's children, in typical DOM style
            nodeList = node.getChildNodes()
            # and again, there should only be done.
            if nodeList.getLength() == 1:
            	# get the value.
                displayName = nodeList.item(0).getNodeValue()
            else:
                print "Unable to get display-name child node value."
        else:
            print "Unable to get display-name node."

    jarFile.close();

    print "    Display Name     = %s" % repr(displayName)

    return displayName

##############################################################
# Program Entry Point
##############################################################

if (len(sys.argv) == 1):
    # Get the command line parameters.
    hudsonWarFileName = sys.argv[0]

    successful = 1

    try:
        # Specify the node and server names to be used.
        cellName        = getCellName()         # Determined by the DMgr connected to
        nodeName        = "localhostNode01"     # The node (of the cell) to install on
        serverName      = "hudson"              # The server name
        contextRoot     = "hudson"              # The context root for the hudson web application
        webServerName   = "webserver"           # The web server name, used in module mapping to servers
        virtualHostName = "hudson"              # The virtual host name, used in module mapping to virtual hosts

        # Read the "Implementation-Version" value from the MANIFEST.MF file.        
        hudsonVersion = getImplentationVersion(hudsonWarFileName)
        if hudsonVersion == None:
            print "Version information was not able to be extracted from the MANIFEST.MF file, aborting."
            raise RuntimeError("FAILED")

        # Retweak some values, based upon the version number
        hudsonVersion = hudsonVersion.replace(".", "_")                 # convert 1.381 to 1_381
        consoleName = "hudson-" + hudsonVersion + "_war"                # the name of application, as seen in the WAS Admin console, eg: hudson-1_381_war

        # Just get the base file name, eg /hudson/hudson.war returns hudson.war
        baseFileName = os.path.basename(hudsonWarFileName)

        # Get 'display-name' value from the web.xml file.
        webAppDisplayName = getWebAppDisplayName(hudsonWarFileName)
        if webAppDisplayName == None:
            print "XML value display-name could not be read from web.xml, aborting."
            raise RuntimeError("FAILED")
        # Quote it to be safe - needed when there are spaces in display name of the web module.
        # Hudson < 1.374 was fixed at 'Hudson'.
        # Hudson >= 1.374 is 'Hudson v1.xxx'
        # For details, see:
        # http://issues.hudson-ci.org/browse/HUDSON-7304
        webAppDisplayName = "'" + webAppDisplayName + "'"

        print "------------------------------------------------------------------------"
        print "Installation Details:"
        print "    Hudson War File         = %s" % hudsonWarFileName
        print "    cellName                = %s" % cellName
        print "    nodeName                = %s" % nodeName
        print "    serverName              = %s" % serverName
        print "    contextRoot             = %s" % contextRoot
        print "    Virtual Host Name       = %s" % virtualHostName
        print "    Console Display Name    = %s" % consoleName
        print "    Web Module Display Name = %s" % webAppDisplayName

        print "------------------------------------------------------------------------"
        print "Stopping Server: %s on %s" % (serverName, nodeName)
        stopServer( nodeName, serverName )

        # Firstly, remove any old Hudson installations. Anything that starts with "hudson"
        print "------------------------------------------------------------------------"
        print "Removing all Hudson installations, if they exist."
        applications = listApplications()
        for application in applications:
            print "    Installed Application Name: %s" % (application) 
            if application.startswith("hudson"):
                print "    >> Deleting Application   : %s" % (application)
                deleteApplicationByName(application)

        print "------------------------------------------------------------------------"
        print "Finished removing previous Hudson installations, if they existed."

        # Now, install the new version of Hudson
        # Note: This installation script also maps the installation of Hudson to a defined webserver called 'webserver',
        #       so you may need to edit the string below accordingly.
        #
        # Could also use:
        #       -MapEnvEntryForWebMod [[ Hudson hudson-1_363.war,WEB-INF/web.xml HUDSON_HOME String "" /hudson/hudson ]]
        #
        # instead of using -DHUDSON_HOME in the server VM definition...
        #
        print "------------------------------------------------------------------------"
        print "Installing new version of Hudson."
        print "Installing using options : " + '[ -contextroot ' + contextRoot + ' -nopreCompileJSPs -distributeApp -nouseMetaDataFromBinary -nodeployejb -appname ' + consoleName + ' -createMBeansForResources -noreloadEnabled -nodeployws -validateinstall warn -noprocessEmbeddedConfig -filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755 -noallowDispatchRemoteInclude -noallowServiceRemoteInclude -MapModulesToServers [[ ' + webAppDisplayName + ' ' + baseFileName + ',WEB-INF/web.xml WebSphere:cell=' +cellName + ',node=' + nodeName + ',server=' + webServerName + '+WebSphere:cell=' + cellName + ',node=' + nodeName + ',server=' + serverName + ' ]] -MapWebModToVH [[ ' + webAppDisplayName + ' ' + baseFileName + ',WEB-INF/web.xml ' + virtualHostName + ' ]]]'
        AdminApp.install(hudsonWarFileName, '[ -contextroot ' + contextRoot + ' -nopreCompileJSPs -distributeApp -nouseMetaDataFromBinary -nodeployejb -appname ' + consoleName + ' -createMBeansForResources -noreloadEnabled -nodeployws -validateinstall warn -noprocessEmbeddedConfig -filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755 -noallowDispatchRemoteInclude -noallowServiceRemoteInclude -MapModulesToServers [[ ' + webAppDisplayName + ' ' + baseFileName + ',WEB-INF/web.xml WebSphere:cell=' +cellName + ',node=' + nodeName + ',server=' + webServerName + '+WebSphere:cell=' + cellName + ',node=' + nodeName + ',server=' + serverName + ' ]] -MapWebModToVH [[ ' + webAppDisplayName + ' ' + baseFileName + ',WEB-INF/web.xml ' + virtualHostName + ' ]]]' )
        print "------------------------------------------------------------------------"
        print "Hudson successfully installed."
        print "------------------------------------------------------------------------"
        print "Setting Web Module Class Loader Policy to PARENT_LAST."
        setClassloaderToParentLastOnly(consoleName)

        # Now save the configuration
        print "Saving Changes..."
        saveAndSync()

        print "------------------------------------------------------------------------"
        print "installHudson.py - Finished - Successful"
        print "------------------------------------------------------------------------"

    except:
        ( exception, params, traceback ) = sys.exc_info()
        print "------------------------------------------------------------------------"
        print "Failed!\nException:\n%s\nParams:\n%s\nTraceback:\n%s\n" % (str(exception), str(params), str(traceback))
        print "------------------------------------------------------------------------"
        print "installHudson.py - Finished - FAILED!!!"
        print "------------------------------------------------------------------------"
        successful = 0

    if successful == 0:
        raise RuntimeError("FAILED")

else:
    print ""
    print "Usage:"
    print "installHudson.py <hudsonWarFileName>"
    raise RuntimeError("FAILED")
