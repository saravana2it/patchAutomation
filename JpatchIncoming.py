import os, glob
import hglib
import datetime
import re
import xml.etree.ElementTree as ET


class JpatchIncoming:

    def __init__(self, branch, repo="..\\"):
        # if len(sys.argv) > 1:
        #     repo = sys.argv[1]
        self.repo = repo
        self.client = hglib.open(repo)
        self.branch = branch

    def updateForce (self):
        pullList = self.client.incoming(branch=self.branch)
        print "\n--updateForce-- Repo: {0} | Branch: {1} ".format(os.path.abspath(self.repo), self.branch)
        if len(pullList) > 0:
            print "[INFO]: CURRENT CHANGESET: {0}".format(self.client.summary()['parent'])
            print "[INFO]: Pulling latest from public repository..."
            self.client.pull(rev="default")
            try:
                ptags = self.patchTags()
                if len(ptags) == 0:
                    print "[WARN]: NO PATCH TAG FOUND TO UPDATE"
                    return
                self.client.update(rev=ptags[0], check=True)
            except hglib.error.CommandError, a:
                print "[WARN]: FOUND UNCOMMITED CHANGES : {0}".format(a)
                JpatchIncoming.revert()
                self.client.update(rev=ptags[0], check=True)
                print "[INFO]: UPDATED TO : {0}".format(self.client.summary()['parent'])
        else:
            ptags = self.patchTags()
            if len(ptags) == 0:
                print "[WARN]: NO PATCH TAG FOUND TO UPDATE"
                return
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

    def patchTags(self):
        ptag = []
        tagChange = self.client.tags()
        tags, revno, chgset, st = zip(*tagChange)
        for tag in tags:
            if str(tag).startswith("Patch") and \
                    str(tag).count(str(datetime.date.today())) and len(self.client.log(branch=self.branch, revrange=tag)):
                ptag.append(tag)
        return ptag

    def filechanges(self):
        mfile = []
        print "---filechanges---"
        curtag = self.patchTags()
        for t in curtag:
            modfile = self.client.status(change=t,modified=True,added=True,removed=True,deleted=True)
            stat,modfile = zip(*modfile)
            for f in list(modfile):
                mfile.append(f)

        print "[INFO]: Detected TAGS: ",curtag
        print "[INFO]: Modified files: \n",mfile
        return mfile

    def findPom(self, mfiles):
        currentPath = os.path.abspath('..\\')
        modfiles = list(map(lambda x: currentPath + "\\" + x, mfiles))
        locatePOM = list(map(lambda x: x[0:str(x).index("src")], modfiles))
        pomLocation = list(map(lambda x: x + "pom.xml", locatePOM))
        print "[INFO]: POM files:", set(pomLocation)
        return set(pomLocation)

    def parsePom(self, pomLoc):
        print "--Parsing--POM---"
        artifactID = ""
        packaging = ""
        version = ""
        artifact = ""
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

    def findVCproj(self, cfiles):
        vcFiles = []
        headFiles = []
        owd = os.getcwd()
        print ("[INFO]: findVCproj method for CPP files")
        print "---findVCproj---"
        path = os.path.abspath(self.repo)
        try:
            for loc in cfiles:
                locVC = path + "\\" + loc[0:str(loc).rindex("\\")]
                rawfile = loc[str(loc).rindex("\\") + 1:len(loc)]
                file = rawfile
                os.chdir(locVC)
                if len(glob.glob("*.vcproj")) == 0:
                    if str(loc).startswith("include"):
                        print "[INFO]: Adding Include file",loc
                        headFiles.append(loc)
                    else:
                        locVC = locVC[0:locVC.rindex("\\")]
                        os.chdir(locVC)
                for f in glob.glob("*.vcproj"):
                    if file in open(f).read():
                        vcF = os.path.join(locVC, f)
                        vcFiles.append(vcF)
        finally:
            os.chdir(owd)
        return vcFiles

    def findCbinary(self, vcFileSet):
        binaryname = []
        for vcF in vcFileSet:
            tree = ET.parse(vcF)
            root = tree.getroot()
            configs = root.findall("Configurations")
            conf = configs[0].findall("Configuration")
            print "[INFO]: Processing VCproject:", vcF
            for j in range(0, len(conf)):
                if conf[j].attrib["Name"] == "Release|Win32":
                    tool = conf[j].findall("Tool")
                    for i in range(0, len(tool)):
                        if tool[i].attrib["Name"] == "VCLinkerTool":
                            Toolname = tool[i].attrib["Name"]
                            cbin = tool[i].attrib["OutputFile"]
                            binloc = os.path.abspath(cbin)
                            print '[INFO]: Binary location: ', binloc
                            binaryname.append(binloc)
        return binaryname




# # --------------------------------------
# # C++ repository patch processing
# # --------------------------------------
# cobj = JpatchIncoming(repo="..//..//8770_c", branch="dev1.3")
# cobj.updateForce()
# fileset = cobj.filechanges()
# cfiles = []
# for cf in fileset:
#     if str(cf).endswith(".cpp") or str(cf).endswith(".h") or str(cf).endswith(".vcproj"):
#         cfiles.append(cf)
#     else:
#         print "[WARN]: Non cpp file found: ",cf
# cbin = []
# vc = cobj.findVCproj(cfiles)
# cbinary = cobj.findCbinary(set(vc))
#
# # ----------------------------------------
# # JAVA repository patch processing
# # ----------------------------------------
# jobj = JpatchIncoming(branch="default")
# jobj.updateForce()
# fileset = jobj.filechanges()
# jfiles = []
# for mf in fileset:
#     if str(mf).endswith(".java") or str(mf).endswith(".xdct") or str(mf).endswith(".xml"):
#         jfiles.append(mf)
#     else:
#         print "[WARN]: Non java file found: ",mf
# poms = jobj.findPom(jfiles)
# art = []
# for o in poms:
#     art.append(jobj.parsePom(o))
#
