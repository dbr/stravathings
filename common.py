import sys
import time
import json
import urllib

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
                print >>sys.stderr, "Caching miss for %r" % key
    else:
        import warning
        warning.warn("redis not found, no caching will be used")

    start = time.time()
    req = urllib.urlopen(url)
    end = time.time()
    content = req.read()
    print >>sys.stderr, "Request took %.02f seconds" % (end-start)

    if req.getcode() >= 400:
        raise StravaError("%r responded with status was %s" % (url, req.getcode()))

    if have_redis and cache:
        r.set(key, content)

    return json.loads(content)
