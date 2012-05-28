def bearing_between(lon1, lat1, lon2, lat2):
    """
    tc1=mod(atan2(sin(lon2-lon1)*cos(lat2),
                  cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1)),
            2*pi)
    """

    from math import sin, cos, atan2, pi, degrees, radians

    lon1 = radians(lon1)
    lon2 = radians(lon2)

    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = atan2(
               sin(lon2-lon1)*cos(lat2),
               cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1)
        ) % (2*pi)

    return degrees(a)


def getimg(lat, lon, heading):
    url = "http://maps.googleapis.com/maps/api/streetview?size=400x400&location={lat},%20{lon}&fov=90&heading={heading}&pitch=0&sensor=false".format(lat = lat, lon = lon, heading = heading)
    return url

from parse_gpx import get_points


import optparse
opter = optparse.OptionParser()
opts, args = opter.parse_args()

for fname in args:
    p = get_points(fname = fname)
    #trimmed = p[::len(p)/100]
    trimmed = p[:10:2]
    for i, t in enumerate(trimmed):
        try:
            n = trimmed[i+1]
        except IndexError:
            pass # use last value.. ew.
        else:
            bear = bearing_between(lon1 = t['lon'], lat1 = t['lat'], lon2 = n['lon'], lat2 = n['lat'])

        url = getimg(lat = t['lat'], lon = t['lon'], heading = bear)

        print url

        import urllib
        urllib.urlretrieve(url, "thing_%04d.jpg" % (i))
