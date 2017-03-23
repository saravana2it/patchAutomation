import os
import hglib
import datetime
import sys
import re
import xml.etree.ElementTree as ET


class JpatchIncoming:

    def __init__(self, branch, repo="..\\"):
        # if len(sys.argv) > 1:
        #     repo = sys.argv[1]
        self.client = hglib.open(repo)
        self.branch = branch

    def updateForce (self):
        pullList = self.client.incoming(revrange="tip", branch=self.branch)
        if len(pullList) > 0:
            print "[INFO]: CURRENT CHANGESET: {0}".format(self.client.summary()['parent'])
            print "[INFO]: Pulling latest from public repository..."
            self.client.pull(rev="default")
            try:
                ptags = self.patchTags()
                if len(ptags) == 0:
                    print "[ERROR]: NO PATCH TAG FOUND"
                    exit()
                self.client.update(rev=ptags[0], check=True)
            except hglib.error.CommandError, a:
                print "[WARN]: FOUND UNCOMMITED CHANGES : {0}".format(a)
                JpatchIncoming.revert()
                self.client.update(rev=ptags[0], check=True)
                print "[INFO]: UPDATED TO : {0}".format(self.client.summary()['parent'])
        else:
            ptags = self.patchTags()
            if len(ptags) == 0:
                print "[ERROR]: NO PATCH TAG FOUND"
                exit()
            print "[INFO]: CURRENT CHANGESET: {0}".format(self.client.summary()['parent'])
            try:
                self.client.update(rev=ptags[0], check=True)
                print "[INFO]: UPDATED TO : {0}".format(self.client.summary()['parent'])
            except hglib.error.CommandError, a:
                print "[WARN]: FOUND UNCOMMITED CHANGES : {0}".format(a)
                JpatchIncoming.revert(self)
                self.client.update(rev=ptags[0], check=True)
                print "[INFO]: UPDATED TO : {0}".format(self.client.summary()['parent'])

    def revert(self):
        filestatus = self.client.status(added=True, removed=True, deleted=True, modified=True)
        print "[INFO]: Reverting the uncommited changes ..."
        print filestatus
        status, files = zip(*filestatus)
        print "[INFO]: REVERTED FILES (check *.orig for backup)   \n {0} \n".format(filestatus)
        self.client.revert(files=list(files))


# obj = Incoming()
# obj.updateForce()

    def patchTags(self):
        ptag = []
        tagChange = self.client.tags()
        tags, revno, chgset, st = zip(*tagChange)
        for tag in tags:
            if str(tag).startswith("Patch") and \
                    str(tag).count(str(datetime.date.today())) and len(self.client.log(branch=self.branch, revrange=tag)):
                ptag.append(tag)
        # for tag in ptag:
        #     if len(self.client.log(branch=self.branch, revrange=tag)) <= 0:
        #         ptag.remove(tag)
        return ptag

    def filechanges(self):
        mfile = []
        print "---filechanges---"
        curtag = self.patchTags()
        for t in curtag:
            modfile = self.client.status(change=t,modified=True,added=True,removed=True,deleted=True)
            stat,modfile = zip(*modfile)
            # print "[INFO]: Fetching TAG :", t
            for f in list(modfile):
                mfile.append(f)
                # print "[INFO]: Modified files:", f

        print "[INFO]: Detected TAGS: ",curtag
        print "[INFO]: Modified files: \n",mfile
        print "---filechanges---"
        return mfile

    def findPom(self, mfiles):
        modfiles = []
        # print "[INFO]: Modified files:", mfiles
        currentPath = os.path.abspath('..\\')
        modfiles = list(map(lambda x: currentPath + "\\" + x, mfiles))
        locatePOM = list(map(lambda x: x[0:str(x).index("src")], modfiles))
        pomLocation = list(map(lambda x: x + "pom.xml", locatePOM))
        print "[INFO]: POM files:", set(pomLocation)
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
        artifactID = ""
        packaging = ""
        version = ""
        artifact = ""
        # pomLoc = str(pomLoc).replace("\\","\\\\")
        while artifact is "":
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
                    # if str(version).endswith("SNAPSHOT"):
                    #     raise "[ERROR]:----POM-files-are-with-SNAPSHOT-version----"
                    # print "[INFO]: Current Version: " + version
                if re.search(r'\bpackaging$', pom, re.IGNORECASE):
                    packaging = root[i].text
                    # print "[INFO]: Current packaging: " + packaging
                i += 1
            builddir = pomLoc.replace('pom.xml', 'target')
            if not os.path.exists(builddir) or packaging == "pom" or packaging is None:
                print "[WARN]: Packaging (or) Target directory not found. Redirecting to the parent pom information ..."
                # pgroupID = parentinfo[0].find('{http://maven.apache.org/POM/4.0.0}groupId')
                partifactID = parentinfo[0].find('{http://maven.apache.org/POM/4.0.0}artifactId')
                # pversion = parentinfo[0].find('{http://maven.apache.org/POM/4.0.0}version')
                # print "[INFO]: Parent groupID: {0} \n \t\t parent artifactID: {1} \n \t\t parent version: {2}".format(pgroupID.text, partifactID.text, pversion.text)
                parentPom = pomLoc.partition(partifactID.text)[0] + partifactID.text
                if os.path.exists(parentPom + "\\pom.xml"):
                    pomLoc = parentPom + "\\pom.xml"
            else:
                artifact = builddir + "\\" + artifactID + "-" + version + "." + packaging
                print "--End-of-parsePom---"
                print "[INFO]: Artifact : ", artifact
        return artifact



        # if len(artifactID,version,packaging) > 0:
        #     return artifactID, version, packaging


obj = JpatchIncoming(branch="default")
obj.updateForce()
fileset = obj.filechanges()
jfiles = []
for mf in fileset:
    if str(mf).endswith(".java") or str(mf).endswith(".xdct"):
        jfiles.append(mf)
    else:
        print "[WARN]: Non java file found: ",mf
poms = obj.findPom(jfiles)
art = []
for o in poms:
    art.append(obj.parsePom(o))
# print art, len(art)
print set(art)
# print obj.findArtifact("D:\\Sandbox\\8770_java\\8770-appl\\tools\\pom.xml")


