import shutil
import re,os, dircache
from datetime import datetime
from string import ascii_uppercase
import datetime


from JparseYML import JparseYML


class JStruct:

    rootDir = "[InstallDir]"

    def __init__(self):
        self.parse = JparseYML()

    def copyBinary(self, binaryList):
        for binary in binaryList:
            jroot = os.path.abspath(".").rstrip('workspace_path')
            fpatter = self.parse.getJfileformat(binary)
            source = jroot + self.parse.getJsource(binary)
            patchLoc = self.parse.getJPatchLoc()
            folderStruc = self.parse.getJdeploy(binary)
            folderStruc = str(folderStruc).replace("nmc_home", "[InstallDir]")
            dest = patchLoc + "Patch_name" + "\\" + folderStruc
            # + datetime.datetime.now().strftime("%d-%m-%Y-%H_%M")
            if not os.path.exists(dest):
                os.makedirs(dest)
            ls = dircache.listdir(source)
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


    def nextPatch(self):
        patchLoc = self.parse.getJLaft()
        patchList = dircache.listdir(patchLoc)
        if len(patchList) > 1:
            outList = list(filter(lambda x: not str(x).endswith(".zip"), patchList))
            lastPatch = str(outList[len(outList) - 2]).split("_")
            print lastPatch
            out = re.sub('\d','',lastPatch[1])
            if len(out) == 1:
                if ord(out) == 90:
                    print "ZA"
                print ord(out)
                newLetter = chr(ord(out) + 1)
            elif len(out) == 2:
                if ord(out[1]) == 90:
                    raise "---- Patch naming supports till patch ZZ. Disable patch naming and run ----"
                print ord(out[1])
                newLetter = out[0] + chr(ord(out[1]) + 1)
            version = re.sub('\D','',lastPatch[1])
            newPatch = lastPatch[0] + "_" + version + newLetter
            print "[INFO]: New generated patch Letter: ",newPatch
        else:
            raise "---- No Patch found on PatchLocation, Missing argument -V <8770Version> ----"








        #if isinstance(deploy, list):
        #     deploy = list(map(lambda x: jroot + x, deploy))
        #else:




obj = JStruct()
# obj.copyBinary(["nms8770-client", "axis2.war"])
# print obj.ftimestamp("D:\\Sandbox\\8770_java\\8770-appl\\common\\target\\axis2.war")
# obj.nextPatch()