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


def _get_ride_infos(aid, offset = 0):
    allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=%s&offset=%d" % (aid, offset), cache=False)


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
            sortables['heartrateAvg'] = sum(stream['heartrate']) / float(len(stream['heartrate']))
            sortables['heartrateMax'] = max(stream['heartrate'])
        else:
            sortables['heartrateMin'] = -1
            sortables['heartrateAvg'] = -1
            sortables['heartrateMax'] = -1

        if 'temp' in stream:
            temp = [x for x in stream['temp'] if x is not None]
            sortables['temperatureMin'] = min(temp)
            sortables['temperatureMax'] = max(temp)
            
            sortables['temperatureAvg'] = sum(temp) / float(len(temp))

        else:
            sortables['temperatureMin'] = -1
            sortables['temperatureMax'] = -1
            sortables['temperatureAvg'] = -1

        if 'cadence' in stream:
            sortables['cadenceAvg'] = sum(stream['cadence']) / float(len(stream['cadence']))
            nonzero = [x for x in stream['cadence'] if x > 0]
            sortables['cadenceAvgNonZero'] = sum(nonzero) / float(len(nonzero))
        else:
            sortables['cadenceAvg'] = -1
            sortables['cadenceAvgNonZero'] = -1
            
    return rides


def get_ride_infos(aid):
    found = []
    for x in range(10):
        curpage = _get_ride_infos(offset = x*50, aid = aid)
        if len(curpage) < 50:
            return found + curpage
        else:
            found.extend(curpage)
    else:
        print >> sys.stderr, "Too many results, stoppng"
        return found


def show_ride(info):
    return "# %s (%s)\n%.02f km (%.02f hours moving)\n%.02f km/h avg (%.02f km/h max)\n%.02fm climbed\n%.00fw average power\n%dbpm (HR min)\n%dbpm (HR avg)\n%dbpm (HR max)\n%d*c min (%d*c avg) %d*c max\n%s cadence avg (%d non-zero avg)" % (
        info['name'],
        info['startDate'],
        info['distance'].asUnit(_km).asNumber(),
        info['movingTime'].asUnit(_hour).asNumber(),
        info['averageSpeed'].asUnit(_km/_hour).asNumber(),
        info['maximumSpeed'].asUnit(_km/_hour).asNumber(),
        info['elevationGain'].asNumber(),
        info['averageWatts'].asNumber(),
        info['heartrateMin'],
        info['heartrateAvg'],
        info['heartrateMax'],
        info['temperatureMin'],
        info['temperatureAvg'],
        info['temperatureMax'],
        info['cadenceAvg'],
        info['cadenceAvgNonZero'],
        )


def show_csv_heading():
    return "startDate, name, distance, movingTime, averageSpeed, maximumSpeed, elevationGain, averageWatts, heartrateMin, heartrateAvg, heartrateMax, temperatureMin, temperatureAvg, temperatureMax, cadenceAvg, cadenceAvgNonZero"


def show_csv(info):
    return "%s, %s,%.02f, %.02f, %.02f, %.02f, %.02f, %.00f, %d, %d, %d, %d, %d, %d, %d, %d" % (
        time.mktime(info['startDate'].timetuple()),
        info['name'].replace(",", ""),
        info['distance'].asUnit(_km).asNumber(),
        info['movingTime'].asUnit(_hour).asNumber(),
        info['averageSpeed'].asUnit(_km/_hour).asNumber(),
        info['maximumSpeed'].asUnit(_km/_hour).asNumber(),
        info['elevationGain'].asNumber(),
        info['averageWatts'].asNumber(),
        info['heartrateMin'],
        info['heartrateAvg'],
        info['heartrateMax'],
        info['temperatureMin'],
        info['temperatureAvg'],
        info['temperatureMax'],
        info['cadenceAvg'],
        info['cadenceAvgNonZero'],
        )


def main():
    opter = optparse.OptionParser()
    opter.add_option("--csv", action="store_true", default = False)
    opter.add_option("-a", "--athlete", dest="athlete", type="int")

    opts, args = opter.parse_args()

    if opts.athlete is None:
        aid = myid()
    else:
        aid = opts.athlete

    if len(args) == 0:
        sort_key = 'startDate'
    elif len(args) > 1:
        opter.error("Sort argument must be ...") # FIXME: populate this
    else:
        sort_key = args[0]

    rides = get_ride_infos(aid = aid)


    if opts.csv:
        headings = sorted(rides[0].keys())

        out = []
        out.append(show_csv_heading())
        for r in rides:
            out.append(show_csv(r))
        #open("to_r.csv", "w+").write("\n".join(out))
        print "\n".join(out)

    else:
        s = sorted(rides, key = lambda k: k[sort_key])
        print "\n\n".join(show_ride(r) for r in s)


if __name__ == '__main__':
    main()
