import os
import optparse

import untangle
import simplekml
import dateutil.parser


opter = optparse.OptionParser()
opts, args = opter.parse_args()
for fname in args:

    kml = simplekml.Kml()

    ta = untangle.parse(fname)
    print "Track name", ta.gpx.trk.name.cdata

    print dir(kml)
    track = kml.newgxtrack()

    for item in ta.gpx.trk.trkseg.trkpt:
        lat, lon = item['lat'], item['lon']
        when = dateutil.parser.parse(item.time.cdata)

        print when, lat, lon

        track.newdata(when = when, gxcoord = [(float(lon), float(lat))])

    print kml.save("%s.kml" % fname)
