# -*- coding: utf-8 -*-

import scorelib
import sys

if len(sys.argv) < 2:
    exit("Too less arguments calling script")

fileName = sys.argv[1]

prints = scorelib.load(fileName)
for print_obj in prints:
    print_obj.format()
    print()

