"""Script to export all an Strava user's rides as TCX files, which
contain the calculated wattage as actual wattage.
"""


prefix="""<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
 xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
 xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
 xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
 xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
 xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">
"""

actvitiy_and_lap_def = """
<Activities>
<Activity Sport="Other">
<Id>{name}</Id>
<Lap StartTime="{startDate}">
<AverageHeartRateBpm><Value>{heartrateAvg}</Value></AverageHeartRateBpm>
<MaximumHeartRateBpm><Value>{heartrateMax}</Value></MaximumHeartRateBpm>
<Cadence>{cadenceAvgNonZero}</Cadence>
<TotalTimeSeconds>{elapsedTime}</TotalTimeSeconds>
<DistanceMeters>{distance}</DistanceMeters>
<Intensity>Active</Intensity>
<TriggerMethod>Manual</TriggerMethod>
<Track>
"""

trackpoint = """<Trackpoint>
<Time>{time}</Time>
<Position><LatitudeDegrees>{lat}</LatitudeDegrees><LongitudeDegrees>{lng}</LongitudeDegrees></Position>
<AltitudeMeters>{altitude}</AltitudeMeters>
<DistanceMeters>{distance}</DistanceMeters>{cadence}{power}{hr}
</Trackpoint>"""

end = """</Track>
</Lap>
</Activity>
</Activities>
</TrainingCenterDatabase>
"""

import time
import datetime
from common import geturl, myid

def dict_of_list_to_list_of_dicts(src):
    allthings = []
    for i, item in enumerate(src[src.keys()[0]]):
        cur = {}
        for key in src:
            cur[key] = src[key][i]
        allthings.append(cur)

    return allthings


class NoMoreResults(Exception):
    pass


def _get_ride_infos(aid, offset = 0):
    allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=%s&offset=%d" % (aid, offset), cache=False)

    for r in allrides['rides']:
        rid = r['id']
        info = geturl("http://www.strava.com/api/v1/rides/%s" % rid)
        stream = geturl("http://app.strava.com/api/v1/streams/%s" % rid)


        theride = {}

        theride['id'] = rid
        theride['name'] = info['ride']['name']
        theride['startDate'] = info['ride']['startDate']
        when = datetime.datetime.strptime(info['ride']['startDate'].partition("Z")[0], '%Y-%m-%dT%H:%M:%S')
        epoch = time.mktime(when.timetuple())
        theride['startEpoch'] = epoch
        theride['elapsedTime'] = info['ride']['elapsedTime']
        theride['distance'] = info['ride']['distance']

        if 'heartrate' in stream:
            theride['heartrateMin'] = min(stream['heartrate'])
            theride['heartrateAvg'] = sum(stream['heartrate']) / float(len(stream['heartrate']))
            theride['heartrateMax'] = max(stream['heartrate'])
        else:
            theride['heartrateMin'] = -1
            theride['heartrateAvg'] = -1
            theride['heartrateMax'] = -1

        if 'cadence' in stream:
            theride['cadenceAvg'] = sum(stream['cadence']) / float(len(stream['cadence']))
            nonzero = [x for x in stream['cadence'] if x > 0]
            theride['cadenceAvgNonZero'] = sum(nonzero) / float(len(nonzero))
        else:
            theride['cadenceAvg'] = -1
            theride['cadenceAvgNonZero'] = -1

        theride['points'] = dict_of_list_to_list_of_dicts(stream)

        yield theride

    if len(allrides['rides']) < 50:
        raise NoMoreResults("Only %d on this page" % (len(allrides['rides'])))


def get_ride_infos(aid):
    for x in range(50):
        curpage = _get_ride_infos(offset = x*50, aid = aid)
        try:
            for c in curpage:
                yield c
        except NoMoreResults:
            return


def tcx_date(epoch):
    dt = datetime.datetime.fromtimestamp(epoch)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


for ride in get_ride_infos(myid()):
    fname = "/Users/dbr/Desktop/tcx/ride_%d.tcx" % ride['id']
    print "Writing %s" % fname
    f = open(fname, "w+")

    f.write(prefix.format())
    f.write(actvitiy_and_lap_def.format(**ride))
    for i, point in enumerate(ride['points']):
        point['time'] = tcx_date(epoch = ride['startEpoch'] + point['time'])
        point['lat'], point['lng'] = point['latlng']

        if 'cadence' in point:
            point['cadence'] = "<Cadence>%d</Cadence>" % (point['cadence'])
        else:
            point['cadence'] = ""

        if 'watts_calc' in point:
            point['power'] = "<Extensions><ns3:TPX><ns3:Watts>%s</ns3:Watts></ns3:TPX></Extensions>" % (
                point['watts_calc'])
        else:
            point['power'] = ""

        if 'heartrate' in point:
            point['hr'] = '<HeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t"><Value>%d</Value></HeartRateBpm>' % (
                point['heartrate']
                )
        else:
            point['hr'] = ''

        f.write(trackpoint.format(**point))

    f.write(end)
