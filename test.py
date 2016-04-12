#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pylab import *
import numpy as np
import pygrib
from datetime import datetime, timedelta
from glob import glob
from h5py import File as h5

Mlg_lon = 360. - 69.3
Mlg_lat = -35.3
dlon, dlat = 5.1, 5.1
year_ini, year_end = 2006, 2013 #2006 #2013
time_ini = datetime(year_ini, 1, 1)
LEVELS = (50, 100, 200, 300, 700, 850) #100 #700 # [mbar] isobaric surfaces
#dir_fig = './figs/lev_%04d' % LEVEL
#dir_inp = '../%04d' % year
dir_inp_root = '/media/Elements/data_gdas'
fname_out = './test.h5'
h, t = {}, {}
"""
for level in LEVELS:
    name = 'level_%04d' % level
    t[name], h[name] = {}, {}
"""

for year in range(year_ini, year_end+1):
    dir_inp = '%s/%04d' % (dir_inp_root, year)
    for level in LEVELS:
        name = 'level_%04d' % level
        t[name], h[name] = {}, {}

    for month in range(1, 12+1):
        fname_inp = '%s/A*-%04d%02d.pgb.f00' % (dir_inp, year, month)
        fname_inp = glob(fname_inp)[0] # there's only one, take the first
        print "\n ---> NEXT: " + fname_inp
        g = pygrib.open(fname_inp)
        dname = '%04d-%02d' % (year, month)
        for level in LEVELS:
            name = 'level_%04d' % level
            t[name][dname], h[name][dname] = [], []
        #print " --> date: ", year, month, 

        gg = g.readline()       # read 1st line
        while gg!=None:  # iterate over levels and days
            pname = gg['parameterName']
            sname = gg['shortName']
            yyyy, mm, dd = gg['year'], gg['month'], gg['day']
            HH, MM = gg['hour'], gg['minute']
            level = gg['level']
            time = datetime(yyyy, mm, dd, HH, MM)
            rtime = (time - time_ini).total_seconds()/86400./365. # [years] relative time
            if sname=='gh' and (level in LEVELS):
                if level==LEVELS[0]:
                    print " --> date: ", year, month, "; t: %4.4f" % rtime

                lat, lon = gg.latlons()
                cc  =  (lat<(Mlg_lat+dlat/2.)) & (lat>(Mlg_lat-dlat/2.))
                cc  &= (lon<(Mlg_lon+dlon/2.)) & (lon>(Mlg_lon-dlon/2.))
                val = gg['values']
                name = 'level_%04d' % level
                h[name][dname]   += [ val[cc].mean() ]
                t[name][dname]   += [ rtime ]

            gg = g.readline() # read next line

    fname_out = './test_%04d.h5' % yyyy
    print " -----> guardando: " + fname_out
    f5 = h5(fname_out, 'w')
    for level in LEVELS:
        lname = 'level_%04d' % level
        for dname in h[lname].keys():
            h[lname][dname] = np.array(h[lname][dname])
            t[lname][dname] = np.array(t[lname][dname])
            path = '%s/%s' % (lname, dname)
            f5['%s/t'%path] = t[lname][dname]
            f5['%s/h'%path] = h[lname][dname]

    f5.close()

"""
fig = figure(1, figsize=(6,4))
ax  = fig.add_subplot(111)

ax.contourf(lon, lat, val)
ax.scatter(Mlg_lon, Mlg_lat, marker='o', color='black', s=300, alpha=0.5)

TITLE= '%02d/%02d/%04d %02d:%02d' % (dd, mm, yyyy, HH, MM)
TITLE+= '\nlevel: %g' % level
ax.set_title(TITLE)

fname_fig = '%s/tt_%04d.png' % (dir_fig, i)
print " --> " + fname_fig, "; level: ", "; pname:"+pname, level, "; etc: ", gg
savefig(fname_fig, dpi=75, bbox_inches='tight') 
close()
i+=1
"""
