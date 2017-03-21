import os

import hglib
import datetime
import sys
import re
import xml.etree.ElementTree as ET

class JpatchIncoming:

    repo = '..\\'
    if len(sys.argv) > 1:
        repo = sys.argv[1]
    client = hglib.open(repo)

    def updateForce (self):
        pullList = JpatchIncoming.client.incoming(revrange="default")
        if len(pullList) > 0:
            print "[INFO]: CURRENT CHANGESET \n {0}\n".format(JpatchIncoming.client.summary()['parent'])
            print "[INFO]: Pulling latest from public repository..."
            JpatchIncoming.client.pull(rev="default")
            try:
                JpatchIncoming.client.update(rev="default", check=True)
            except hglib.error.CommandError, a:
                print "[WARN]: FOUND UNCOMMITED CHANGES : {0} \n".format(a)
                JpatchIncoming.revert()
                JpatchIncoming.client.update(rev="default", check=True)
                print "[INFO]: UPDATED TO LATEST \n {0}".format(JpatchIncoming.client.summary()['parent'])
        else:
            print "[INFO]: CURRENT CHANGESET \n {0}\n".format(JpatchIncoming.client.summary()['parent'])
            try:
                JpatchIncoming.client.update(rev="default", check=True)
            except hglib.error.CommandError, a:
                print "[WARN]: FOUND UNCOMMITED CHANGES : {0} \n".format(a)
                JpatchIncoming.revert(self)
                JpatchIncoming.client.update(rev="default", check=True)
                print "[INFO]: UPDATED TO LATEST \n {0}".format(JpatchIncoming.client.summary()['parent'])

    def revert(self):
        filestatus = JpatchIncoming.client.status(added=True, removed=True, deleted=True, modified=True)
        print "[INFO]: Reverting the uncommited changes ...\n"
        print filestatus
        status, files = zip(*filestatus)
        print "[INFO]: REVERTED FILES (check *.orig for backup)   \n {0} \n".format(filestatus)
        JpatchIncoming.client.revert(files=list(files))


# obj = Incoming()
# obj.updateForce()

    def filechanges(self):
        target = []
        mfile = []
        print "---filechanges---"
        tagChange = JpatchIncoming.client.tags()
        tags,revno,chgset,st = zip(*tagChange)
        for tag in tags:
            if str(tag).startswith("Patch") and str(tag).count(str(datetime.date.today())):
                target.append(tag)
        for t in target:
            modfile = JpatchIncoming.client.status(change=t,modified=True,added=True,removed=True,deleted=True)
            stat,modfile = zip(*modfile)
            # print "[INFO]: Fetching TAG :", t
            for f in list(modfile):
                mfile.append(f)
                # print "[INFO]: Modified files:", f
        print "[INFO]: Detected TAGS: ",target
        print "[INFO]: Modified files: ",mfile
        print "---filechanges---"
        return mfile

    def findArtifact(self, mfiles):
        modfiles = []
        # print "[INFO]: Modified files:", mfiles
        currentPath = os.path.abspath('..\\')
        modfiles = list(map(lambda x: currentPath + "\\" + x, mfiles))
        locatePOM = list(map(lambda x: x[0:str(x).index("src")], modfiles))
        pomLocation = list(map(lambda x: x + "pom.xml", locatePOM))
        print "[INFO]: POM files:", pomLocation
        return pomLocation
        # for each in pomLocation:
        #     self.parsePom(each)

        # if os.path.exists(locatePOM + "\\pom.xml"):
        #     tree = ET.parse(pomLoc)
        #     root = tree.getroot()
        #     i = 0
        #     for each in root:
        #          pom = str(root[i].tag)
        #          if re.search(r'artifactID', pom, re.IGNORECASE):
        #              artifactID = root[i].text
        #          if re.search(r'version', pom, re.IGNORECASE):
        #              version = root[i].text
        #          if re.search(r'packaging', pom, re.IGNORECASE):
        #              packaging = root[i].text
        #          i += 1
        # return artifactID, version, packaging


    def parsePom(self, pomLoc):
        print "--Parsing--POM---"
        artifact = ""
        # pomLoc = str(pomLoc).replace("\\","\\\\")
        tree = ET.parse(pomLoc)
        root = tree.getroot()
        parentinfo = root.findall('{http://maven.apache.org/POM/4.0.0}parent')
        print "[INFO]: Processing POM:", pomLoc
        i = 0
        for each in root:
            pom = str(root[i].tag)
            if re.search(r'\bartifactID$', pom, re.IGNORECASE):
                artifactID = root[i].text
                # print "[INFO]: Current ArtifactID: " + artifactID
            if re.search(r'\bversion$', pom, re.IGNORECASE):
                version = root[i].text
                # print "[INFO]: Current Version: " + version
            if re.search(r'\bpackaging$', pom, re.IGNORECASE):
                packaging = root[i].text
                # print "[INFO]: Current packaging: " + packaging
            i += 1
        basedir = pomLoc.replace('pom.xml', 'target')
        if not os.path.exists(basedir) or packaging == "pom" or packaging is None:
            print "[WARN]: Packaging or Target dir not found. Redirecting to the parent pom information ........."
            # pgroupID = parentinfo[0].find('{http://maven.apache.org/POM/4.0.0}groupId')
            partifactID = parentinfo[0].find('{http://maven.apache.org/POM/4.0.0}artifactId')
            # pversion = parentinfo[0].find('{http://maven.apache.org/POM/4.0.0}version')
            # print "[INFO]: Parent groupID: {0} \n \t\t parent artifactID: {1} \n \t\t parent version: {2}".format(pgroupID.text, partifactID.text, pversion.text)
            parentPom = pomLoc.partition(partifactID.text)[0] + partifactID.text
            if os.path.exists(parentPom + "\\pom.xml"):
                self.parsePom(parentPom + "\\pom.xml")
        else:
            artifact = basedir + "\\"+ artifactID + "-" + version + "." + packaging
            print "--End-of-parsePom---"
            print "[INFO]: RETURN: ",artifact
        return "ok"



        # if len(artifactID,version,packaging) > 0:
        #     return artifactID, version, packaging


obj = JpatchIncoming()
fileset = obj.filechanges()
poms = obj.findArtifact(fileset)
art = []
for o in poms:
    art.append(obj.parsePom(o))
print art
# print obj.findArtifact("D:\\Sandbox\\8770_java\\8770-appl\\tools\\pom.xml")


