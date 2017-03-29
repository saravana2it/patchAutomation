import sys, re

from Jstruct import JStruct
from JpatchIncoming import JpatchIncoming

class AutoPatch:

    def __init__(self):
        self.jstruct = JStruct()
        self.version = self.cmdbin = self.pname = self.branch = ""

    def checkArg(self):
        args = sys.argv
        args.pop(0)
        # print args
        cmd = list(map(lambda x: str(x)[0:2],args))
        if (len(cmd) > len(set(cmd))):
            print cmd
            raise "---- Duplicate argument detected ----"

        for each in args:
            each = str(each)
            if each.startswith("-v"):
                self.version = each.lstrip("-v")
                ver = re.search(r'8770.(\d{1}.\d{1}.\d{2}.\d{2}.[a-z])', self.version)
                if not ver:
                    print "\n[ERROR]: Invalid Argument, expecting -v8770.X.X.XX.XX.x"
            elif each.startswith("-p"):
                self.pname = each.lstrip("-p")
                if len(self.pname) == 0:
                    print "[ERROR]: Invalid Argument -p<patchName> -> [info]: Can not be empty"
            elif each.startswith("-a"):
                binary = each.lstrip("-a")
                if len(binary) == 0:
                    print "[ERROR]: Invalid Argument -a<artifact1,arti2,..> -> [info]: Can not be empty"
                self.cmdbin = binary.split(",")
            elif each.startswith("-b"):
                self.branch = each.lstrip("-b")
                if len(self.branch) == 0:
                    print "[ERROR]: Invalid Argument -b<branchname> -> [info]: Can not be empty"
            else:
                print "\n*****************************************"
                print "\n----------AUTO-PATCH-SCRIPT--------------"
                print "\n*****************************************"
                print "\nThe AutoPatch script is to detect and produce the patch fix solutions\nwith required binary.\n"
                print "EXECUTION:\t AutoPatch -v -b [-p] [-a] \n\n"
                print ' -v \t Patch version   (example: -v8770.3.2.07.02.a)\n'
                print ' -b \t Patch branch   (example: -bPatch3.2pqa)\n'
                print ' -p \t Patch name   (example: -pPATCH_320702B_JAR_V1)\n'
                print ' -a \t Binary names   (example: -a"nms8770-client.jar, axis2.war")\n'
                if not each.count("-h") > 0:
                    print "[ERROR]: Unknown argument ",cmd

        try:
            md1 = cmd.index("-v")
            md2 = cmd.index("-b")
        except:
            print "\n[INFO]: (-v) (-b) - Mandatory"
            exit()




main = AutoPatch()
main.checkArg()
# print "ver", obj.version
# print "pname", obj.pname
# print "binary", obj.cmdbin
# print "branch", obj.branch



# --------------------------------------
# C++ repository patch processing
# --------------------------------------
cobj = JpatchIncoming(repo="..//..//8770_c", branch="dev1.3")
cobj.updateForce()
cfileset = cobj.filechanges()
cfiles = []
for cf in cfileset:
    if str(cf).endswith(".cpp") or str(cf).endswith(".h") or str(cf).endswith(".vcproj"):
        cfiles.append(cf)
    else:
        print "[WARN]: Non cpp file found: ",cf
cbin = []
vc = cobj.findVCproj(cfiles)
cbinary = cobj.findCbinary(set(vc))

# ----------------------------------------
# JAVA repository patch processing
# ----------------------------------------
jobj = JpatchIncoming(branch="default")
jobj.updateForce()
jfileset = jobj.filechanges()
jfiles = []
for mf in jfileset:
    if str(mf).endswith(".java") or str(mf).endswith(".xdct") or str(mf).endswith(".xml"):
        jfiles.append(mf)
    else:
        print "[WARN]: Non java file found: ",mf
poms = jobj.findPom(jfiles)
art = []
for o in poms:
    art.append(jobj.parsePom(o))

# ------------------------------------------------------
# Patch structure
# ------------------------------------------------------

struct = JStruct(pname=main.pname)
struct.copyBinary(main.version, cbinary)
struct.copyBinary(main.version, art)
# print obj.ftimestamp("D:\\Sandbox\\8770_java\\8770-appl\\common\\target\\axis2.war")
# obj.nextPatch("8770.3.2.07.00.a", pname="Patch_320700M_JAR")

