import urllib
import time
import json


def get_challenge_page(page = 1, only_complete = True, cache = False):
    assert page > 0, "Pages start at 1"

    url = "http://app.strava.com/challenges/5/details?per_page=100&overall_page=%d" % (page)

    if cache:
        from common import geturl
        results = geturl(url)
    else:
        start = time.time()
        content = urllib.urlopen(url).read()
        end = time.time()
        print "%.02f seconds" % (end-start)

        results = json.loads(content)

    #goal_type = results['dimension'] # e.g elavation_gain
    goal_value = results['goal']

    ret = []

    for user in results['overall']:
        userinfo = results['athletes'][str(user['id'])]

        percentage = (userinfo['total_dimension'] / goal_value) * 100

        if only_complete and percentage < 100:
            return ret
        else:
            ret.append({
                    'percentage': percentage,
                    'name': userinfo['name'],
                    'location': userinfo['location'],
                    'rank': user['rank']})
    return ret

def show_user(u):
    print "%(rank)d. %(name)s (%(percentage)d%%)\n%(location)s" % u

if __name__ == '__main__':
    all_results = []
    for x in range(10):
        page = get_challenge_page(page=x+1, cache = True)
        if len(page) == 0:
            print "Done at page %d" % (x+1)
            break
        all_results.extend(page)

    counter = 0
    for u in all_results:
        if 'SA, Australia'.lower() in u['location'].lower():
            show_user(u)
            counter += 1
    print "%d completed" % counter
