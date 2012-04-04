#This code is still in works and has a lot of hardcoded parts to it.

import re
from collections import defaultdict

log = open('/media/New Volume/work/GSoC2012/stanford_last_100k_filt.log')

parsedlog = ()
templist = []
for line in log.readlines()[:10]:
    #print line
    templist.append(re.findall('\((\d*.\d*.\d*.\d*)\).*\[(.*)\] "([^"]*)" (\d*) (\d*) "([^"]*)" "([^"]*)"', line).pop())
    
#data = [(2010, 2), (2009, 4), (1989, 8), (2009, 7)]
d = defaultdict(list)
for IP in templist:
    d[IP[0]].append(IP[1:])

for key,value in d.iteritems():
    print "IP Address : " + key
    for timestamp, HTTP, Status, ContentLen, Referer, UA in value:
        print "\n"
        print " Timestamp : " + timestamp + "\n URL : " + HTTP,  "\n Status : " + Status + "\n Content Length : " + ContentLen, "\n Referer : " +  Referer, "\n User Agent : " + UA, "\n"        
    print "-" * 30
