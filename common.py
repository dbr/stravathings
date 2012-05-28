import time
import json
import httplib2

try:
    import redis
except ImportError:
    have_redis = False
else:
    have_redis = True


class StravaError(Exception):
    pass


def myid():
    """Returns my Strava athlete ID.
    """
    return 316985


def geturl(url, cache = True):
    """Retrives a URL, optionally caching the response into redis
    """

    key = "strava_cache:%s" % url

    if have_redis:
        # If redis is available, use it to cache API return values
        r = redis.Redis()
        if cache:
            cv = r.get(key)
            if cv is not None:
                return json.loads(cv)
            else:
                print "Caching miss for %r" % key
    else:
        import warning
        warning.warn("redis not found, only httplib2 caching will be used")

    http = httplib2.Http(".cache")

    start = time.time()
    resp, content = http.request(url)
    end = time.time()
    print "%.02f seconds" % (end-start)

    if int(resp['status']) >= 400:
        raise StravaError("%r responded with status was %s" % (url, resp['status']))

    if have_redis and cache:
        r.set(key, content)

    return json.loads(content)
