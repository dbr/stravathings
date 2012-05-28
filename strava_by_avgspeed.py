from common import geturl


def convert_seconds(seconds):
    """Converts integer seconds into human-readable MM:SS format."""
    minutes = seconds // 60
    seconds %= 60
    return '%02i:%02i' % (minutes, seconds)


allrides = geturl("http://www.strava.com/api/v1/rides?athleteId=316985", cache=False)

efforts_times_by_segment_id = {}



rides = []
for r in allrides['rides']:
    rid = r['id']
    info = geturl("http://www.strava.com/api/v1/rides/%s" % rid)

    from unum.units import m as _m, km as _km, h as _hour, s as _sec

    avg_speed = info['ride']['averageSpeed'] * (_m/_sec)

    rides.append(
        (avg_speed, info['ride']['name']))

for avg_speed, name in sorted(rides):
    print "%30s: %.02f km/h" % (
        name[:30],
        avg_speed.asUnit(_km/_hour).asNumber())
