#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

VERSION = raw_input().strip()

def replace(filename):
    fh = open(filename, "r")
    content = fh.read()
    content = content.replace("_VERSION_", VERSION)
    fh.close()

    fh = open(filename.replace("_draft", ""), "w")
    fh.write(content)
    fh.close()

def replace_line(filename):
    line_to_search_for = "#!!Version line "
    rep = False

    fh = open(filename, "r")
    content = fh.read()
    fh.close()

    output = ""
    for line in content.split("\n"):
        if line_to_search_for in line:
            rep = True
            line = "VERSION=\"%s\" %s" % (VERSION, line_to_search_for)
#            print "replaced"
        output += line + "\n"

#    if not rep:
#        print "Did not replace any line"
    

    fh = open(filename, "w")
    fh.write(output[0:-1])
    fh.close()

replace("about.glade_draft")
replace("control_draft")

replace_line("modules/functions.py")

print VERSION
