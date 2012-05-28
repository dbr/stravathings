from common import geturl


def convert_seconds(seconds):
    """Converts integer seconds into human-readable MM:SS format."""
    minutes = seconds // 60
    seconds %= 60
    return '%02i:%02i' % (minutes, seconds)


allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=316985", cache=False)

by_ratio = []
for r in allrides['rides']:
    rid = r['id']
    info = geturl("http://www.strava.com/api/v1/rides/%s" % rid)

    ride = info['ride']

    ele = ride['elevationGain']
    dist = ride['distance']

    thing = (ele**2*dist)
    if thing == 0:
        print 'flat/downhill', ride['name']
    else:
        by_ratio.append((thing, dist, ele, ride['name']))

for r in reversed(sorted(by_ratio)):
    thing, dist, ele, name = r
    print "%.01f km dist, %.02f up, %s (%s)" % (dist/1000, ele, name, thing)
