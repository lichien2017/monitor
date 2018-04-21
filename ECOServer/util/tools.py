import hashlib
import os
class Secret:
    @classmethod
    def md5(cls,text):
        m = hashlib.md5()
        m.update(text.encode("utf-8"))
        # print(m.hexdigest())
        return m.hexdigest()

class Tools:
    @classmethod
    def check_dir(self,dir):
        if not os.path.exists(dir):
            os.makedirs(dir)