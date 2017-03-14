
from Jstruct import JStruct
import sys, re

class AutoPatch:

    def __init__(self):
        self.jstruct = JStruct()
        self.version = self.cmdbin = self.pname = ""

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
                ver = re.search(r'8770.(\d{1}.\d{1}.\d{2}.\d{2})', self.version)
                if not ver:
                    print "\n[ERROR]: Invalid Argument, expecting -v8770.X.X.XX.XX"
            elif each.startswith("-p"):
                self.pname = each.lstrip("-p")
                if len(self.pname) == 0:
                    print "[ERROR]: Invalid Argument -p<8770version> -> [info]: Can not be empty"
            elif each.startswith("-a"):
                binary = each.lstrip("-a")
                if len(binary) == 0:
                    print "[ERROR]: Invalid Argument -a<artifacts> -> [info]: Can not be empty"
                self.cmdbin = binary.split(",")
            elif each.startswith("-b"):
                branch = each.lstrip("-b")
                if len(branch) == 0:
                    print "[ERROR]: Invalid Argument -b<branchname> -> [info]: Can not be empty"
            else:
                print "\n*****************************************"
                print "\n----------AUTO-PATCH-SCRIPT--------------"
                print "\n*****************************************"
                print "\nThis AutoPatch script is to create the formatted patch directory with required \nbinary.\n"
                print "EXECUTION:\t AutoPatch -v [-p] [-a] \n\n"
                print ' -v \t Patch version   (example: -v8770.3.2.07.02)\n'
                print ' -p \t Patch name   (example: -pPATCH_320702B_JAR_V1)\n'
                print ' -a \t Binary names   (example: -a"nms8770-client.jar, axis2.war")\n'
                print "[ERROR]: Unknown argument ",cmd

        try:
            md1 = cmd.index("-v")
            md2 = cmd.index("-b")
        except:
            print "\n[INFO]: -v -> Mandatory argument missing"
            print "\n[INFO]: -b -> Mandatory argument missing"
            exit()




obj = AutoPatch()
obj.checkArg()
