import shutil
import re,os, dircache
from datetime import datetime
import datetime
from encodings.punycode import selective_find

from JparseYML import JparseYML


class JStruct:

    rootDir = "[InstallDir]"

    def __init__(self, pname=""):
        self.parse = JparseYML()
        self.patchName = pname

    def copyBinary(self,release, binaryList):
        for binary in binaryList:
            jroot = os.path.abspath(".").rstrip('workspace_path')
            fpatter = self.parse.getJfileformat(binary)
            source = jroot + self.parse.getJsource(binary)
            patchLoc = self.parse.getJPatchLoc()
            folderStruc = self.parse.getJdeploy(binary)
            folderStruc = str(folderStruc).replace("nmc_home", "[InstallDir]")
            dest = patchLoc + self.nextPatch(release) + "\\" + folderStruc
            # + datetime.datetime.now().strftime("%d-%m-%Y-%H_%M")
            if not os.path.exists(dest):
                os.makedirs(dest)
            ls = os.listdir(source)
            for each in ls:
                fileMatch = re.match(fpatter, each)
                if fileMatch:
                    if len(fileMatch.groups()) > 2:
                        print "[INFO]: Binary ----- " + binary + "-- Copied file version: " + fileMatch.group(2)
                        source = source + "\\" + fileMatch.group()
                        if self.checkDate(source):
                            shutil.copyfile(source, dest + fileMatch.group(1) + fileMatch.group(3))
                        else:
                            raise "------Artifact creation date is older !! ------"
                    else:
                        print "[INFO]: Binary ----- " + binary + "-- Copied file : " + fileMatch.group()
                        source = source + "\\" + fileMatch.group()
                        if self.checkDate(source):
                            shutil.copyfile(source, dest + fileMatch.group())
                        else:
                            raise "------Artifact creation date is older !! ------"



    def checkDate(self, binary):
        createTime = datetime.datetime.fromtimestamp(os.path.getctime(binary))
        currentTime = datetime.datetime.now()
        if self.parse.getJPatchlife():
            if createTime.date() == currentTime.date():
                return True
            else:
                return False
        else:
            return True

    def nextPatch(self, release, pname=""):
        if len(self.patchName) > 0:
            pname = self.patchName
        print "[INFO]: ---nextPatch---"
        patchLoc = self.parse.getJLaft()
        patchLoc += release + "\\PATCHES\\Mandatory\\"
        print "[INFO]: Next Patch name generation based on location", patchLoc
        patchList = os.listdir(patchLoc)
        if len(patchList) > 1:
            outList = list(filter(lambda x: not str(x).endswith(".zip") and not str(x).endswith(".txt") and str(x).count("Patch"), patchList))
            patchL = list(map(lambda x: str(x).split("_"), outList))
            alpha = list(map(lambda x: re.sub('\d','', x[1]),patchL))
            alpha = sorted(alpha)
            out = alpha[len(alpha) - 1]
            if len(out) == 1 and ord(out) == 90:
                newLetter = out + "A"
            elif len(out) == 1:
                # print ord(out)
                newLetter = chr(ord(out) + 1)
            elif len(out) == 2:
                if ord(out[1]) == 90:
                    raise "---- Patch naming supports till patch ZZ. Disable patch naming and run ----"
                newLetter = out[0] + chr(ord(out[1]) + 1)
            version = re.sub('\D','',patchL[0][1])
            newPatch = patchL[0][0] + "_" + version + newLetter
            print "[INFO]: Proposing new generated patch Letter: ",newPatch
        else:
            raise "---- No Patch found on PatchLocation, Missing argument -V <8770Version> ----"
        if pname == "":
            print "[INFO]: Returing the Patch name", newPatch
            return newPatch
        else:
            print "[INFO]: Overriding patch name with cmd line args(-p) \n[INFO]: Return patch name: ", pname
            return pname


        #if isinstance(deploy, list):
        #     deploy = list(map(lambda x: jroot + x, deploy))
        #else:


# obj = JStruct()
# obj.copyBinary("8770.3.2.07.00.a", ["nms8770-client", "axis2.war"])
# print obj.ftimestamp("D:\\Sandbox\\8770_java\\8770-appl\\common\\target\\axis2.war")
# obj.nextPatch("8770.3.2.07.00.a", pname="Patch_320700M_JAR")