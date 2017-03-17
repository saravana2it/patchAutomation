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
        tagChange = JpatchIncoming.client.tags()
        tags,revno,chgset,st = zip(*tagChange)
        for tag in tags:
            # print datetime.date.today()
            if str(tag).startswith("Patch") and str(tag).count(str(datetime.date.today())):
                target = tag

        modfile = JpatchIncoming.client.status(change=target)
        stat,modfile = zip(*modfile)
        return list(modfile)

    def findArtifact(self, mfiles):
        modfiles = []
        currentPath = os.path.abspath('..\\')
        modfiles = list(map(lambda x: currentPath + "\\" + x, mfiles))
        locatePOM = list(map(lambda x: x[0:str(x).index("src")], modfiles))
        pomLocation = list(map(lambda x: x + "pom.xml", locatePOM))
        for each in pomLocation:
            self.parsePom(each)

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
        pomLoc = str(pomLoc).replace("\\","\\\\")
        tree = ET.parse(pomLoc)
        root = tree.getroot()
        parentinfo = root.findall('{http://maven.apache.org/POM/4.0.0}parent')
        # print len(parentinfo)

        i = 0
        for each in root:
            pom = str(root[i].tag)
            if re.search(r'\bartifactID$', pom, re.IGNORECASE):
                artifactID = root[i].text
                print artifactID
            if re.search(r'\bversion$', pom, re.IGNORECASE):
                version = root[i].text
                print version
            if re.search(r'\bpackaging$', pom, re.IGNORECASE):
                packaging = root[i].text
                print packaging
            i += 1

        if not os.path.exists(pomLoc.replace('pom.xml','target')):
            print parentinfo
            i = 0
            for each in parentinfo:
                pinfo = str(parentinfo[i].tag)
                print pinfo



        # if len(artifactID,version,packaging) > 0:
        #     return artifactID, version, packaging


obj = JpatchIncoming()
fileset = obj.filechanges()
# print fileset
obj.findArtifact(fileset)
# print obj.findArtifact("D:\\Sandbox\\8770_java\\8770-appl\\tools\\pom.xml")


