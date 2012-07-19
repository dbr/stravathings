import json
import urllib

from common import geturl


def page(page=1):
    assert page>0
    d = json.loads(
        urllib.urlopen("http://app.strava.com/challenges/48/details?paging_type=overall&per_page=50&overall_page=1").read())

    return d


def get_rides(aid):
    aurl = "http://www.strava.com/api/v1/rides?athleteId=%s" % aid
    info = geturl(aurl)

    rides = {'wed': [], 'all': []}

    for r in info['rides']:
        rideinfo = geturl("http://app.strava.com/api/v1/rides/%s" % r['id'])

        when = rideinfo['ride']['startDate']
        if map(int, when.split("T")[0].split("-")) < [2012, 07, 15]:
            return rides
        else:
            if map(int, when.split("T")[0].split("-")) == [2012, 07, 18]:
                rides['wed'].append(rideinfo)
            rides['all'].append(rideinfo)

    return rides


from pprint import pprint as pp
x = page(1)

everyone = []
for aid, athlete in x['athletes'].items():
    print aid, athlete
    rider_info = get_rides(aid)


    who = "%s %s/%s" % (athlete['name'], "http://app.strava.com/athletes", athlete['id'])
    elev_gain = sum(x['ride']['elevationGain'] for x in rider_info['wed'])

    everyone.append((elev_gain, who))

for x in list(reversed(sorted(everyone)))[:10]:
    print x[0], x[1]
