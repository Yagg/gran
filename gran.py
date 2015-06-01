# -*- coding: utf_8 -*-
__author__ = 'Yagg'

import sys
import report

from os import listdir
from os.path import isfile, join
from fnmatch import fnmatch
from analyzer import Analyzer

def main(path):
    files = [join(path, f) for f in listdir(path) if isfile(join(path, f)) and fnmatch(f, '*.zip')]
    reports = []
    for filename in files:
        print >> sys.stderr, "Processing report %s" % filename
        rep = report.Report(filename)
        reports.append(rep)
    an = Analyzer(reports)
    an.run()

if __name__ == '__main__':
    main(sys.argv[1])
