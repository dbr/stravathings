"""Takes a .gpx file, shows things like distance, speed and so on
"""

import os
import optparse

import untangle
import dateutil.parser

from unum.units import km as _km, h as _hour, s as _sec


from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    http://stackoverflow.com/questions/4913349
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c * _km
    return km


def iter_pairs(iterable):
    for i, val in enumerate(iterable):
        try:
            yield val, iterable[i+1]
        except IndexError:
            pass


def term_size():
    rows, cols = map(int, os.popen('stty size', 'r').read().split())
    return (rows, cols)


def get_points(fname):
    ta = untangle.parse(fname)

    print ta.gpx.trk.trkseg.trkpt[0]
    points = [{'lat': float(item['lat']),
               'lon': float(item['lon']),
               'when': dateutil.parser.parse(item.time.cdata),
               'ele': float(item.ele.cdata)}
              for item in ta.gpx.trk.trkseg.trkpt]

    return points


def dostuff(fname):
    points = get_points(fname)
    ttl_dist = 0 * _km
    ttl_time = 0 * _sec

    deltas = []
    for first, second in iter_pairs(points):
        dist = haversine(
            lon1 = first['lon'], lat1 = first['lat'],
            lon2 = second['lon'], lat2 = second['lat'])
        timediff = second['when'] - first['when']
        timediff = timediff.seconds * _sec

        deltas.append({'dist': dist, 'time': timediff})

    for d in deltas:
        # Can't sum() Unum's
        ttl_dist += d['dist']
        ttl_time += d['time']

    _, cols = term_size()
    text_size = cols /4
    cols = cols - text_size
    largest = max(x['dist'] for x in deltas)
    normalised = [x['dist'] / largest for x in deltas]
    for n, info in zip(normalised, deltas):
        bar = "*" * int(round(n.asNumber() * cols))
        padding = " " * int(round((1 - n.asNumber()) * cols))
        try:
            as_kmh = ((info['dist']/info['time']).asUnit(_km/_hour)).asNumber()
        except ZeroDivisionError:
            as_kmh = 0
        text = " %.02fkm (%s) %.02fkm/h" % (
            info['dist'].asNumber(), info['time'],
            as_kmh)
        text.rjust(text_size)
        print bar + padding + text
    print "total %s" % ttl_dist
    print "in %s" % ttl_time.asUnit(_hour)
    print (ttl_dist / ttl_time).asUnit(_km/_hour)



if __name__ == '__main__':
    opter = optparse.OptionParser()
    opts, args = opter.parse_args()

    for fname in args:
        try:
            dostuff(fname = fname)
        except Exception:
            import traceback
            traceback.print_exc()
            print fname, "errored"
