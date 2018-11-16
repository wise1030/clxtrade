

class  clx_file:

    def _init_(self):
        pass

    def readcsv(self):
        pass

    def readtxt(self,file_path):
        f = open("test.txt", "r")
        while True:
            line = f.readline()
            if line:
                pass  # do something here
                line = line.strip()

                p = line.rfind('.')

                filename = line[0:p]
                print "create %s" % line
            else:
                break

        f.close()






