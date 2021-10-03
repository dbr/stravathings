import sys
from common import geturl, myid
from unum.units import s as _sec, h as _hour, d as _day

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
total_moving_time = 0*_sec

for r in allrides['rides']:
    rid = r['id']
    info = geturl("http://www.strava.com/api/v1/rides/%s" % rid)


    if "2012-10-20" < info['ride']['startDate'] < "2012-11-10":
        moving_time = info['ride']['movingTime'] * (_sec)
        total_moving_time += moving_time


stage = {}
stage[1] = 20*_hour
stage[2] = 40*_hour
stage[3] = 60*_hour


# Time left in month
import datetime
time_left = (datetime.datetime(2012, 11, 10) - datetime.datetime.now())

print "%s left" % time_left

print
print "# Remaining for each stage"

for stage_num, stage_time in sorted(stage.items()):
    total_moving_time / stage_time
    done_of_stage = total_moving_time / stage_time
    print "Stage %d: %.02f%% of %s" % (
        stage_num,
        100*done_of_stage,
        stage_time,
        )

    remaining = (1 - done_of_stage) * stage_time
    if remaining < 0*_hour:
        print "Complete"
    else:
        print "%s remaining of stage %s (%s)" % (
            remaining.asUnit(_hour),
            stage_num,
            stage_time,
            )

        per_day_required = remaining / ((time_left.seconds*_sec) + (time_left.days * _day))
        print "%s per day to complete" % per_day_required.asUnit(_hour/_day)

    print "*"*10 + "\n"
