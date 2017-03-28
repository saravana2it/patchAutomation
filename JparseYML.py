import yaml
from itertools import izip


class JparseYML:


    def __init__(self):
        with open("PatchConfig.yml", 'r') as stream:
            try:
                self.patchconfig = yaml.load(stream)
                # print self.patchconfig
            except yaml.YAMLError as exc:
                print(exc)

    def getJdeploy(self,jbinary):
        return self.patchconfig['java'][jbinary]['deploy']

    def getJpreaction(self, jbinary):
        return self.patchconfig['java'][jbinary]['pre-action']

    def getJdependency(self, jbinary):
        # dependlist = []
        return self.patchconfig['java'][jbinary]['dependency']

    def getJpostaction(self, jbinary):
        return self.patchconfig['java'][jbinary]['post-action']

    def getJfileformat(self, jbinary):
        return self.patchconfig['java'][jbinary]['fileformat']

    def getJsource(self,jbinary):
        return self.patchconfig['java'][jbinary]['source']

    def getJPatchlife(self,):
        return self.patchconfig['java']['patchconfig']['filelife']

    def getJPatchLoc(self,):
        return self.patchconfig['java']['patchconfig']['patchlocation']

    def getJLaft(self):
        return self.patchconfig['java']['patchconfig']['laft']

# obj = JparseYML()
# value = obj.getJfileformat("nms8770-client")
# if isinstance(value, list):
#     for depitem in value:
#         print depitem
# else:
# print value




