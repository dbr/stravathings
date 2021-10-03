import json
import urllib
import httplib2


BASE_URL = "https://www.strava.com/api/v1"


class StravaError(Exception):
    pass


def parse_response(resp, content):
    r = json.loads(content)
    if 'error' in r:
        raise StravaError(r['error'])

    if resp.status > 500:
        raise StravaError("Server error code %s: %s" % (resp.status, resp.reason))

    return r


class Ride(object):
    def __init__(self, id, name):
        self._id = id
        self._name = name

    def __repr__(self):
        return "<Ride id: {id} '{name}'>".format(
            id = self._id,
            name = self._name)

    @property
    def name(self):
        return self._name


MAX_RIDES_PER_RESPONSE = 50
class Athlete(object):
    def __init__(self, id, _http = None):
        self.id = id

        if _http is not None:
            self._http = _http
        else:
            self._http = httplib2.Http(".cache")


    def rides(self, extended = False, _offset = 0):
        """Yields a list of rides, most recent first

        If extended is True, returns more than 50 results
        """
        url = "http://www.strava.com/api/v1/rides?athleteId={id}&offset={offset}".format(
            id = self.id,
            offset = _offset)
        resp, content = self._http.request(url)
        r = parse_response(resp, content)

        for r in r['rides']:
            yield Ride(id = r['id'], name = r['name'])

        if extended and len(r['rides']) == MAX_RIDES_PER_RESPONSE:
            self.rides(extended = extended, offset = offset + MAX_RIDES_PER_RESPONSE)


class Strava(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password

        self._http = httplib2.Http(".cache")

    def login(self):
        data = {"email": self.email, "password": self.password}
        body = urllib.urlencode(data)

        resp, content = self._http.request(
            "https://www.strava.com/api/v2/authentication/login",
            method="POST",
            body=body)

        r = parse_response(resp, content)

        self.token = r['token']

        self._me = Athlete(
            id = r['athlete']['id'])

    @property
    def me(self):
        return self._me


if __name__ == '__main__':
    u, p = open(".strava_auth").read().strip().splitlines()
    s = Strava(email = u, password = p)
    s.login()
    print s.me()
    for r in s.me.rides():
        print r
