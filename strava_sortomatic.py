"""Lists all rides sorted by specific attributes like averageSpeed, or
averageWatts etc
"""

import sys
import optparse
from common import geturl, myid
from unum.units import m as _m, km as _km, h as _hour, s as _sec, W as _watt


def convert_seconds(seconds):
    """Converts integer seconds into human-readable MM:SS format."""
    minutes = seconds // 60
    seconds %= 60
    return '%02i:%02i' % (minutes, seconds)


def get_ride_infos():
    allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=%s" % myid(), cache=False)


    rides = []
    for r in allrides['rides']:
        rid = r['id']
        info = geturl("http://www.strava.com/api/v1/rides/%s" % rid)


        sortables = {}

        sortables['name'] = info['ride']['name']
        sortables['averageSpeed'] = info['ride']['averageSpeed'] * (_m/_sec)
        sortables['maximumSpeed'] = info['ride']['maximumSpeed'] * (_m/_hour)
        sortables['distance'] = info['ride']['distance'] * _m
        sortables['movingTime'] = (info['ride']['movingTime'] * _sec).asUnit(_hour)
        if info['ride']['averageWatts'] is None:
            sortables['averageWatts'] = -1 * _watt
        else:
            sortables['averageWatts'] = info['ride']['averageWatts'] * _watt
        sortables['elevationGain'] = info['ride']['elevationGain'] * _m

        rides.append(
            sortables)

    return rides


def show_ride(info):
    return "# %s\n%.02f km (%.02f hours moving)\n%.02f km/h avg (%.02f km/h max)\n%.02fm climbed\n%.00fw average power" % (
        info['name'],
        info['distance'].asUnit(_km).asNumber(),
        info['movingTime'].asUnit(_hour).asNumber(),
        info['averageSpeed'].asUnit(_km/_hour).asNumber(),
        info['maximumSpeed'].asUnit(_km/_hour).asNumber(),
        info['elevationGain'].asNumber(),
        info['averageWatts'].asNumber(),
        )


def main():
    opter = optparse.OptionParser()
    opts, args = opter.parse_args()

    if len(args) != 1:
        options = ['name', 'averageSpeed', 'maximumSpeed', 'distance', 'movingTime', 'averageWatts', 'elevationGain']

        opter.error("First argument must be one of %s" % (
                ", ".join(options)))


    rides = get_ride_infos()
    s = sorted(rides, key = lambda k: k[args[0]])
    print "\n\n".join(show_ride(r) for r in s)


if __name__ == '__main__':
    main()
