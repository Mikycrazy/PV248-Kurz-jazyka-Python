# -*- coding: utf-8 -*-

import scorelib
import sys
import codecs

if len(sys.argv) < 2:
    exit("Too less arguments calling script")

fileName = sys.argv[1]

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

prints = scorelib.load(fileName)
for print_obj in prints:
    print_obj.format()
    print()

