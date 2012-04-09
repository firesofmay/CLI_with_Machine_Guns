"""
Still needs a lot of work to be done
Problem
some links are unique in parts like
'GET /teach/teachers/drewc/bio.html',
'GET /teach/teachers/pmurali/bio.html

or

/myesp/cancelrecover/?code=BdRQVx8lDYzVdrUPAJqUGEuK36xdyP'
/myesp/recoveremail/?code=rfXFyXwdIWeYFMC9cuxRm1N9KccLkF'

need to do something about it to make them Generalize such that we get proper count
"""

import networkx as nx
logs.clear()
logs = nx.DiGraph()

#copy this file or import or something
alog = ApacheAccessLogParser()
f = open("/media/New Volume/work/GSoC2012/stanford_last_100k_filt.log")
for aline in f.readlines():
    alog.parse(aline)
    if alog.referer[:12] == r'http://www.':
        newlink = alog.referer[13:]
    if alog.referer[:8] == r'http://':
        newlink = alog.referer[8:]
    else:
        newlink = alog.referer    
    logs.add_edge(newlink, alog.request[:-9])
