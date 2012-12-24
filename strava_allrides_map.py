"""Given an athleteId, will plot all routes on a Google Map
"""

import pygmaps

from common import geturl, StravaError


def randomcolour(h = None, s = None, v = None):
    import random
    import colorsys

    if h is None:
        h = random.uniform(0.0, 1.0)
    if s is None:
        s = random.uniform(0.9, 1.0)
    if v is None:
        v = random.uniform(0.8, 1.0)

    rgb = colorsys.hsv_to_rgb(h, s, v)

    return tuple(int(x*255) for x in rgb)



import optparse
opter = optparse.OptionParser()
opter.add_option("-a", "--athlete", dest="athlete", type="int")
opter.add_option("-d", "--downsample", dest="downsample", type="int", default=50)
opter.add_option("-o", "--out", dest="out", default="mymap.html")
opter.add_option("-l", "--limit", dest="pagelimit", default=4,
help = "Each page contains 50 rides. -l 4 will download at most 200 rides (starting with the most recent)")

opts, args = opter.parse_args()

if opts.athlete is None:
    import common
    aid = common.myid()
else:
    aid = opts.athlete


def get_ride_info(offset=0):
    allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=%s&offset=%s" % (aid, offset), cache=False)

    rideinfo = []


    for r in allrides['rides']:
        print "Processing %s" % r['name']
        rid = r['id']

        #meta = geturl("http://app.strava.com/api/v1/rides/%s" % rid)

        try:
            info = geturl("http://app.strava.com/api/v1/streams/%s" % rid)
        except StravaError, e:
            print "Error: %s" % e
            continue

        if 'latlng' not in info:
            print "Skipping trainer ride %s" % r['name']
            continue

        latlng = [x for x in info['latlng'] if x != [0.0, 0.0]]

        rideinfo.append(
            {'latlng': latlng,
             'name': r['name'],
             'other': r,
             })

    return rideinfo


rideinfo = []
for offset in range(opts.pagelimit):
    offset = offset * 50
    newrides = get_ride_info(offset)
    rideinfo.extend(newrides)

    if len(newrides) < 50:
        print "No more rides at offset %s" % offset
        break
    else:
        print "Found rides at offset %s" % offset


map = pygmaps.maps(0.0, 0.0, 12)
center = (0.0, 0.0)

for info in rideinfo:

    import curve_simplify

    if True:
        # Handle threshold in more sane manner than in lat/long degrees
        # TODO: I'd be surprised if this calculation is correct, but seems to work..
        accuracy_m = 10.0 # TODO: Make this an argument

        earth_circum_m = 40075 * 1000
        metre_per_deg = earth_circum_m / 360.0
        threshold = accuracy_m / metre_per_deg

        import time
        start = time.time()
        path = curve_simplify.simplify(info['latlng'], threshold)
        print "New: %.02fms" % ((time.time() - start)*1000)

        print "%.02f%% polyline simplification (from %d points to %d)" % (100-float(len(path))/len(info['latlng']) * 100, len(info['latlng']), len(path))

    else:
        path = info['latlng'][opts.downsample::opts.downsample]

    if [0.0, 0.0] in path:
        print info['name']
        print info['other']

    cur_centre = (
        sum(a[0] for a in info['latlng']) / float(len(info['latlng'])),
        sum(a[1] for a in info['latlng']) / float(len(info['latlng'])))

    center = (
        (center[0] + cur_centre[0]) / 2.0,
        (center[1] + cur_centre[1]) / 2.0)

    map.addpath(path, "rgb(%s, %s, %s)" % randomcolour())


map.center = center
map.draw(opts.out)
