from common import geturl


def convert_seconds(seconds):
    """Converts integer seconds into human-readable MM:SS format."""
    minutes = seconds // 60
    seconds %= 60
    return '%02i:%02i' % (minutes, seconds)


allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=316985", cache=False)

efforts_times_by_segment_id = {}

for r in allrides['rides']:
    rid = r['id']
    efforts = geturl("http://www.strava.com/api/v1/rides/%s/efforts" % rid)
    for ef in reversed(sorted(efforts['efforts'], key = lambda k: k['id'])):
        key = (ef['segment']['id'], ef['segment']['name'])
        efforts_times_by_segment_id.setdefault(key, []).append(ef['elapsed_time'])


for _sid_sname, times in sorted(efforts_times_by_segment_id.items(), key = lambda k: len(k[1])):
    sid, sname = _sid_sname
    if len(times) == 1:
        continue

    print "%s (%s times)" % (sname, len(times))
    print "    %s" % ", ".join([convert_seconds(x) for x in times])
