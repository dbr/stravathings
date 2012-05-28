"""Given an athleteId, will plot all routes on a Google Map, with timeline
"""

import json
import random


template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>All strava routes</title>
    <script src="http://maps.google.com/maps/api/js?sensor=false" type="text/javascript"></script>
    <script type="text/javascript" src="lib/jquery-1.4.4.min.js"></script>
    <script src="http://static.simile.mit.edu/timeline/api/timeline-api.js" type="text/javascript"></script>

    <script type="text/javascript" src="lib/mxn/mxn-min.js?(googlev3)"></script>
    <script type="text/javascript" src="lib/timeline-1.2.js"></script>
    <script src="lib/timemap_full.pack.js" type="text/javascript"></script>


    <style type="text/css" media="screen">
        div, p {
        font-family: Verdana, Arial, sans-serif;
        }
        
        div#timemap {
        padding: 1em;
        }
        
        div#timelinecontainer{
        width: 100%%;
        height: 300px;
        }
        
        div#timeline{
         width: 100%%;
         height: 100%%;
         font-size: 12px;
         background: #CCCCCC;
        }
        
        div#mapcontainer {
         width: 100%%;
         height: 800px;
        }
        
        div#map {
         width: 100%%;
         height: 100%%;
         background: #EEEEEE;
        }
        
        div.infotitle {
            font-size: 14px;
            font-weight: bold;
        }
        div.infodescription {
            font-size: 14px;
            font-style: italic;
        }
        
        div.custominfostyle {
            font-family: Georgia, Garamond, serif;
            font-size: 1.5em;
            font-style: italic;
            width: 20em;
        }
    </style>

    <script type="text/javascript">


var tm;
function onLoad() {

    tm = TimeMap.init({
        mapId: "map",               // Id of map div element (required)
        timelineId: "timeline",     // Id of timeline div element (required)
        options: {
            mapType: "physical",
            eventIconPath: "../images/"
        },
        datasets: [
            {
                type: "basic",
                options: {
                    items: %(itemjson)s
                }
            }
        ],
        bandIntervals: "day"
    });

    // Enable scrolling on map
    var map = tm.getNativeMap(); 
    map.setOptions({scrollwheel:true}); 

};

    </script>
  </head>
  <body onLoad="onLoad()" onunload="GUnload();">
    <div id="timelinecontainer">
      <div id="timeline"></div>
    </div>
    <div id="mapcontainer">
      <div id="map"></div>
    </div>
  </body>
</html>
"""


import dateutil.parser

from common import geturl


def randomcolour(h = None, s = None, v = None):
    import random
    import colorsys

    if h is None:
        h = random.uniform(0.0, 1.0)
    if s is None:
        s = random.uniform(0.5, 1.0)
    if v is None:
        v = random.uniform(0.7, 1.0)

    rgb = colorsys.hsv_to_rgb(h, s, v)

    return tuple(int(x*255) for x in rgb)


overlay_js = """
var allcords = [
    [new google.maps.LatLng(-85, 0.0),        new google.maps.LatLng(85, 0.0),        new google.maps.LatLng(85, 90),  new google.maps.LatLng(-85, 90)],
    [new google.maps.LatLng(-85, 90),         new google.maps.LatLng(85, 90),         new google.maps.LatLng(85, 180), new google.maps.LatLng(-85, 180)],
    [new google.maps.LatLng(-85, 180.000001), new google.maps.LatLng(85, 180.000001), new google.maps.LatLng(85, 270), new google.maps.LatLng(-85, 270)],
    [new google.maps.LatLng(-85, 270),        new google.maps.LatLng(85, 270),        new google.maps.LatLng(85, 360), new google.maps.LatLng(-85, 360)],
];

for(var i in allcords)
{
      bgpoly = new google.maps.Polygon({
        paths: allcords[i],
        strokeColor: "#FFF",
        strokeOpacity: 0.9,
        strokeWeight: 1.0,
        fillColor: "#000",
        fillOpacity: 0.5,
        zIndex: -999999
      });
      bgpoly.setMap(map)
}



"""


def convert_seconds(seconds):
    """Converts integer seconds into human-readable MM:SS format."""

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    return '%02ih %02im' % (h, m)


def make_descr(d):
    d = d.copy()

    when = dateutil.parser.parse(d['startDate'])

    d['when'] = when.strftime("%a %b %d, %Y")

    d['resting'] = convert_seconds(d['elapsedTime'] - d['movingTime'])
    d['movingTime'] = convert_seconds(d['movingTime'])

    d['distance'] = "%.02f km" % (d['distance'] / 1000)

    return """%(distance)s<br>
%(when)s<br>
%(movingTime)s moving (%(resting)s resting)<br>
""" % d

import optparse
opter = optparse.OptionParser()
opter.add_option("-a", "--athlete", dest="athlete", type="int")
opter.add_option("-d", "--downsample", dest="downsample", type="int", default="50")
opts, args = opter.parse_args()

if opts.athlete is None:
    import common
    aid = common.myid()
else:
    aid = opts.athlete


allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=%s" % aid, cache=False)

rideitems = []

center = (0.0, 0.0)
for r in allrides['rides']:
    print "Processing %s" % r['name']
    rid = r['id']

    meta = geturl("http://app.strava.com/api/v1/rides/%s" % rid)

    when = dateutil.parser.parse(meta['ride']['startDate'])

    info = geturl("http://app.strava.com/api/v1/streams/%s" % rid)

    path = info['latlng'][opts.downsample::opts.downsample]

    date = "%04d-%02d-%02d" % (when.year, when.month, when.day)
    item = {
        'start': date,
        'title': r['name'],
        'polyline': [{'lat': p[0], 'lon': p[1]} for p in path],
        'options': {
            'description': make_descr(meta['ride']),
            'theme': random.choice(['blue', 'green', 'ltblue', 'orange', 'pink', 'purple', 'red', 'yellow']),
            }
        }

    rideitems.append(item)


html = template % {'itemjson': json.dumps(rideitems, sort_keys=True, indent=4)}
open("mymap.html", "w").write(html)
