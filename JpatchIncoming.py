import hglib
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

    def filechanges(self,label):
        tagChange = JpatchIncoming.client.tags()
        tags,revno,chgset,st = zip(*tagChange)
        # for tag in tags:
            # if str(tag).startswith("BL"):
                # print tag

        modfile = JpatchIncoming.client.status(change=label)
        stat,modfile = zip(*modfile)
        return list(modfile)

    def findArtifact(self, pomLoc):
        tree = ET.parse(pomLoc)
        root = tree.getroot()
        i = 0
        for each in root:
            pom = str(root[i].tag)
            if re.search(r'artifactID', pom, re.IGNORECASE):
                artifactID = root[i].text
            if re.search(r'version', pom, re.IGNORECASE):
                version = root[i].text
            if re.search(r'packaging', pom, re.IGNORECASE):
                packaging = root[i].text
            i += 1
        return artifactID, version, packaging

obj = JpatchIncoming()
print obj.filechanges("CI_BUILD")
print obj.findArtifact("D:\\Sandbox\\8770_java\\8770-appl\\tools\\pom.xml")


