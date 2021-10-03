import urllib
import logging
from BeautifulSoup import BeautifulSoup as BS

log = logging.getLogger(__name__)

class NoSuchChallenge(Exception):
    pass


URL = "http://app.strava.com/challenges/{id}"


def check_challenge(id):
    u = URL.format(id = id)
    resp = urllib.urlopen(u)
    if resp.getcode() == 404:
        raise NoSuchChallenge("Challenge {id} does not exist".format(id=id))

    html = resp.read()
    soup = BS(html)
    return (u, soup.title.text)


def main(start = 1, end = None):
    if end is None:
        # End after 1000 requests, instead of an infinite loop
        end = start + 1000

    # How many errors to ensuffer before accepting there are no more
    # challenges. Can't bail out of first one, as there are batches of
    # deleted challenges (e.g numbers 78-86 are gone)
    max_errors = 20

    # Keeps count of current chunk of errors, resets when a challenge
    # is found
    error_run = 0

    for cid in range(start, start+1000):
        try:
            url, title = check_challenge(id = cid)

        except NoSuchChallenge, e:
            error_run += 1
            log.debug("%s" % (e))

        except Exception, e:
            error_run += 1
            log.error(
                "Unhandled exception while checking challenge %d: %s" % (cid, e),
                exc_info = True)

        else:
            error_run = 0 # Reset
            log.info("Found challenge %s, %s (%s)" % (cid, url, title))
    
        if error_run >= max_errors:
            return


if __name__ == '__main__':
    logging.basicConfig()
    log.setLevel(logging.DEBUG)
    main()
