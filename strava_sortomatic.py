"""Lists all rides sorted by specific attributes like averageSpeed, or
averageWatts etc
"""

import sys
import optparse
import time
import datetime
from common import geturl, myid
from unum.units import m as _m, km as _km, h as _hour, s as _sec, W as _watt


def convert_seconds(seconds):
    """Converts integer seconds into human-readable MM:SS format."""
    minutes = seconds // 60
    seconds %= 60
    return '%02i:%02i' % (minutes, seconds)


def _get_ride_infos(offset = 0):
    allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=%s&offset=%d" % (myid(), offset), cache=False)


    rides = []
    for r in allrides['rides']:
        rid = r['id']
        info = geturl("http://www.strava.com/api/v1/rides/%s" % rid)

        sortables = {}

        when = datetime.datetime.strptime(info['ride']['startDate'].partition("Z")[0], '%Y-%m-%dT%H:%M:%S')

        sortables['startDate'] = when
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

        stream = geturl("http://app.strava.com/api/v1/streams/%s" % rid)

        if 'heartrate' in stream:
            sortables['heartrateMin'] = min(stream['heartrate'])
            sortables['heartrateMax'] = max(stream['heartrate'])
        else:
            sortables['heartrateMin'] = -1
            sortables['heartrateMax'] = -1

        if 'temp' in stream:
            sortables['temperatureMin'] = min(stream['temp'])
            sortables['temperatureMax'] = max(stream['temp'])
            sortables['temperatureAvg'] = float(sum(stream['temp']))/len(stream['temp'])
        else:
            sortables['temperatureMin'] = -1
            sortables['temperatureMax'] = -1
            sortables['temperatureAvg'] = -1
            
    return rides


def get_ride_infos():
    found = []
    for x in range(10):
        curpage = _get_ride_infos(offset = x*50)
        if len(curpage) < 50:
            return found + curpage
        else:
            found.extend(curpage)
    else:
        print >> sys.stderr, "Too many results, stoppng"
        return found


def show_ride(info):
    return "# %s (%s)\n%.02f km (%.02f hours moving)\n%.02f km/h avg (%.02f km/h max)\n%.02fm climbed\n%.00fw average power\n%dbpm (HR min)\n%dbpm (HR max)\n%d*c min (%d*c avg) %d*c max" % (
        info['name'],
        info['startDate'],
        info['distance'].asUnit(_km).asNumber(),
        info['movingTime'].asUnit(_hour).asNumber(),
        info['averageSpeed'].asUnit(_km/_hour).asNumber(),
        info['maximumSpeed'].asUnit(_km/_hour).asNumber(),
        info['elevationGain'].asNumber(),
        info['averageWatts'].asNumber(),
        info['heartrateMin'],
        info['heartrateMax'],
        info['temperatureMin'],
        info['temperatureAvg'],
        info['temperatureMax'],
        )


def show_csv_heading():
    return "startDate, name, distance, movingTime, averageSpeed, maximumSpeed, elevationGain, averageWatts, heartrateMin, heartrateMax, temperatureMin, temperatureAvg, temperatureMax"


def show_csv(info):
    return "%s, %s,%.02f, %.02f, %.02f, %.02f, %.02f, %.00f, %d, %d, %d, %d, %d" % (
        time.mktime(info['startDate'].timetuple()),
        info['name'].replace(",", ""),
        info['distance'].asUnit(_km).asNumber(),
        info['movingTime'].asUnit(_hour).asNumber(),
        info['averageSpeed'].asUnit(_km/_hour).asNumber(),
        info['maximumSpeed'].asUnit(_km/_hour).asNumber(),
        info['elevationGain'].asNumber(),
        info['averageWatts'].asNumber(),
        info['heartrateMin'],
        info['heartrateMax'],
        info['temperatureMin'],
        info['temperatureAvg'],
        info['temperatureMax'],
        )


def main():
    opter = optparse.OptionParser()
    opter.add_option("--csv", action="store_true", default = False)
    opts, args = opter.parse_args()

    if len(args) != 1:
        options = ['name', 'averageSpeed', 'maximumSpeed', 'distance', 'movingTime', 'averageWatts', 'elevationGain']

        opter.error("First argument must be one of %s" % (
                ", ".join(options)))

    rides = get_ride_infos()


    if opts.csv:
        headings = sorted(rides[0].keys())

        out = []
        out.append(show_csv_heading())
        for r in rides:
            out.append(show_csv(r))
        #open("to_r.csv", "w+").write("\n".join(out))
        print "\n".join(out)

    else:
        s = sorted(rides, key = lambda k: k[args[0]])
        print "\n\n".join(show_ride(r) for r in s)


if __name__ == '__main__':
    main()
