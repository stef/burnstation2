#!/usr/bin/env python

import subprocess
import sys

try:
    pipe = subprocess.Popen("bzr log", shell=True, stdout=subprocess.PIPE)
    logfile = pipe.communicate()[0]
except ValueError:
    print("Error with my Pipe")
    sys.exit(-1)

revisions = logfile.split("------------------------------------------------------------")
revisions.reverse()
revisions = revisions[:-1]


class REVISION:
    def __init__(self, rev):
        self.revision=None
        self.comitter=None
        self.branch=None    
        self.timestamp=None
        self.message=None

        lines = rev.split("\n")[1:]
        self.revision = lines[0].strip().replace("revno: ", "")
        self.comitter = lines[1]
        self.branch = lines[2]
        self.timestamp = lines[3]
        self.message="\n".join(lines[4:]).strip()

    def __str__(self):
        ret = """revision: %s
committer: %s
branch: %s
timestamp: %s
message: %s
        """ % (self.revision, self.comitter, self.branch, self.timestamp, self.message)
        return ret

revlist = []
for rev in revisions:
    r = REVISION(rev)
    revlist.append(r)

def get_revision(rev):
    return revisions[rev-1]

def get_revisions(fromrev, torev):
    return revisions[fromrev-1: torev]


#while 1:
#    print(60*"*")
#    print("Got %i revisions" % len(revlist))
#    print("Lates revision: %s" % revlist[len(revlist)-1].revision)
#    print("")
#    print("What do you want to do?")
#    print("""NUM = Show that revision
#RANGE (1-10) = Print those revisions
#EXIT = Exit
#    """)
#    ret = raw_input("Your Choice: ")
#    print(60*"*")

#    if "-" in ret:
#        try:
#            fr, to = ret.split("-")
#            for r in revlist:
#                if (r.revision) >= (fr) and (r.revision) <= (to):
#                    print r
#        except OSError:
#            print("That was no valid range")
#    elif ret.lower() == "exit":
#        sys.exit()
#    elif ret.isdigit():
#        print 30*"="
#        found = False
#        for rev in revlist:
#            if rev.revision == str(ret):
#                found = True
#                print rev
#        if not found:
#            print("The revision %s was not found" % ret)
#        print 30*"="
