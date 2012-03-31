import random
import time
import subprocess
import sys

class Transaction(object):

    listtocall = []
    def init (self):
        self.listtocall=[sys.executable, './myTest.py']
        fileArg = 2
        if sys.argv[fileArg]:
            data = open(sys.argv[fileArg])
            self.listtocall += data.read().split('\n\n')[:-1]

            if 'save' in self.listtocall[-1]:
                self.listtocall.pop()
                self.listtocall.append('quit')
            else:
                self.listtocall.append('quit')
    

        else:
            print "Provide the TestScript to run the tests on. Exiting."
            exit(0)


    def run(self):


        self.init()
        # start the timer
        start_timer = time.time()

        subprocess.call(self.listtocall)

        # stop the timer
        latency = time.time() - start_timer

        # store the custom timer
        self.custom_timers['User Registration'] = latency




if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
