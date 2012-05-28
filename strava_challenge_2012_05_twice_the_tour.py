import sys
from common import geturl, myid
from unum.units import m as _m, km as _km, mile as _miles, s as _sec, h as _hour, d as _day

import unum
unum.Unum.VALUE_FORMAT = "%.01f"


if len(sys.argv) > 1:
    aid = sys.argv[1]
    print "Using %s from argument" % aid
else:
    aid = myid()
    print "Using my athlete ID, %s" % aid

allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=%s" % aid, cache=False)


# Collect ride info, calculate total distance (since sum() dislikes unum objects)
total_dist = 0*_km

for r in allrides['rides']:
    rid = r['id']
    info = geturl("http://www.strava.com/api/v1/rides/%s" % rid)


    if not info['ride']['startDate'].startswith("2012-05-"):
        # Only consider rides in May
        continue

    dist = info['ride']['distance'] * (_m)
    total_dist += dist


# Progress of distance
print "Stage 1 (%s): %.02f%%" % (370,           (total_dist/ ((370)             *_miles))*100)
print "Stage 2 (%s): %.02f%%" % (370*2,         (total_dist/ ((370+370)         *_miles))*100)
print "Stage 3 (%s): %.02f%%" % (370*2+410,     (total_dist/ ((370+370+410)     *_miles))*100)
print "Stage 4 (%s): %.02f%%" % (370*2+410+329, (total_dist/ ((370+370+410+329) *_miles))*100)

stage = {}
stage[1] = 370*_miles
stage[2] = (370+370)*_miles
stage[3] = (370+370+410)*_miles
stage[4] = (370+370+410+329)*_miles


# Time left in month
import datetime
time_left = (datetime.datetime(2012, 6, 1) - datetime.datetime.now())

print "%s left" % time_left

print
print "# Remaining for each stage"

for stage_num, stage_dist in sorted(stage.items()):
    done_of_stage = total_dist / stage_dist
    print "Stage %d: %.02f%% of %s" % (
        stage_num,
        100*done_of_stage,
        stage_dist,
        )

    remaining = (1 - done_of_stage) * stage_dist
    if remaining < 0*_miles:
        print "Complete"
    else:
        print "%s remaining of stage %s" % (
            remaining,
            stage_num,
            )

        per_day_required = remaining / ((time_left.seconds*_sec) + (time_left.days * _day))
        print "%s per day to complete" % per_day_required.asUnit(_km/_day)

    print "*"*10 + "\n"
