#!/usr/bin/env python

import sys

for l in sys.stdin:
    fields = l.split(',')
    print('%s,%s,%s' % (fields[1],fields[4],1))
