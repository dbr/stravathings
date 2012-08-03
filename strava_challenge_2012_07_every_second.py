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


    when = tuple([int(x) for x in info['ride']['startDate'].partition("T")[0].split("-")])

    if when > (2012, 7, 23) and when < (2012, 8, 22):
        dist = info['ride']['distance'] * (_m)
        total_dist += dist


stage = {}
stage[1] = 1788*_km * 0.25
stage[2] = 1788*_km * 0.5
stage[3] = 1788*_km * 0.75
stage[4] = 1788*_km


# Time left in month
import datetime
time_left = (datetime.datetime(2012, 8, 22) - datetime.datetime.now())

print "%s done" % total_dist
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
        print "%s (%s) remaining of stage %s" % (
            remaining,
            remaining.asUnit(_km),
            stage_num,
            )

        per_day_required = remaining / ((time_left.seconds*_sec) + (time_left.days * _day))
        print "%s per day to complete" % per_day_required.asUnit(_km/_day)

    print "*"*10 + "\n"
