A reasonably random collection of scripts relating to [Strava](http://strava.com)

# Notes

## Requirements

I'm using Python 2.7 (2.6 will might work also)

- [unum](http://pypi.python.org/pypi/Unum/4.1.0) is used to prevent
silly unit-conversion related errors
- [redis](http://pypi.python.org/pypi/redis) is used for caching,
  although as discussed in the caching section, this requirement could
  be removed quite easily.

There is a `requirements.txt` file containing the specific versions
(so you can `pip install -r requirements.txt`)

## Athlete ID

Most scripts default to [my Strava athlete-id](http://app.strava.com/athletes/316985)

You probably want to modify the `myid` function in `common.py` to your ID (found by going to your profile page, and looking at the number in the URL, e.g given `http://app.strava.com/athletes/316985` the ID is `316985`

Most scripts should take an argument to change this (usually `-a 1234`),
although changing the `myid` function saves from always having to type this

## Caching

Since a lot of these scripts make a lot of requests to the Strava API
(usually one or two per ride, on each run), there is some basic
caching in place.

The caching is currently based on [redis](http://redis.io), because it
was easy to implement.. For it to work, you need to be running a redis
server, and have the `redis` Python module installed. On OS X with
[homebrew](http://mxcl.github.com/homebrew/) installed:

    $ brew install redis
    $ pip install redis

All URL-retrival is done via `geturl` in `common.py`, so implementing
a file-based cache would be easy..

# Scripts

## allrides_map

For a given athlete, creates a self-contained HTML file, with all
routes cycled overlaid on a single map.

    $ python strava_allrides_map.py

By default this grabs the last 4 pages of rides (which means 200 rides). You can change this limit with `-l 10` which will download 500 etc.

## strava_sortomatic.py

Prints your last 50 rides, ordered by a specific attribute like averageSpeed

    $ python strava_sortomatic.py averageWatts | tail -11
    # Crafers
    18.36 km (0.77 hours moving)
    24.00 km/h avg (57.08 km/h max)
    503.27m climbed
    199w average power

    # Last cycle before back to Scotland for a while
    62.74 km (2.76 hours moving)
    22.73 km/h avg (50.66 km/h max)
    305.00m climbed
    227w average power

## strava_multisegment.py

Based on your last 50 rides, shows all segments you've done more than
once, along with your times for each.

The most recent time should be on the right, although I wouldn't rely
on the ordering...

## strava_dist_vs_elevation.py

Tries to sort the last 50 rides based on distance and amount of
climbing.

I'm sure there's better ways to order them, but elevationgain squared,
multiplied by distance seemed to work quite well

For example:

    $ python strava_dist_vs_elevation.py 
    164.4 km dist, 2433.48 up, Murray Bridge and back
    93.2 km dist, 1360.78 up, Lofty, Corkscrew, Gorge and beach w/Scott
    56.6 km dist, 1716.41 up, Mt Lofty figure of... 9
    135.7 km dist, 1092.08 up, Around The Forth (NCN route 76'ish)

So the long ride with lots of climbing was first. The shorter ride
with a relatively large amount of climibing is third, and a longer
with not much climbing was 4th.

## Strava challenge-specific scripts

There's a couple of scripts to track my progress on a few of
[Strava's challenges]http://app.strava.com/challenges), which are
pretty useless now, but could be modified for future things

## Misc'ery

### `parse_gpx.py`

This parses a GPX file and prints some basic, crudely
formatted info like distance and so on.

None of this has been used, as the Strava API provides all the
necessary numbers, so calculating speed from GPS data-points hasn't
been necessary.

This uses [`Untangle`](https://github.com/stchris/untangle) for XML
parsing, along with
[`python-dateutil`](http://labix.org/python-dateutil) to parse the
timestamps. Also `unum` to prevent stupid errors when converting the
metres/sec to more readable units and such..

### `streetview.py`

An incomplete experiment to take a GPS track and create a video of the
route using Google Streetview images.

You need frames quite often along the route to maintain any
consistency, and there is a limit of 1000 requests/hour for the
Streetview API. Doable, just need to tweak the interval at which is
grabs images, and there might be something wonky with the
heading-calculation

### `ridetrim/ridetrim.html`

A crude and incomplete web/Javascript application, for removing a bad
section in the middle of a GPX file (say if you don't pause the GPS
recording while in a car, or go in a building and the GPS position jumps
around due to the weak signal)

You paste the contents of a GPX file into the first textarea, click
"Load" button.

It shows the route on a map. You adjust the sliders to select a region
of the track.

Then click "trim", and in the right-hand textarea, the new trimmed GPX
file contents is displayed.

This means you could export a GPX from Strava, remove a noisy section
of the ride, and create a clean GPX file. Then delete the original
ride and reupload

Note that the tool will currently drop additional data like
heart-rate, power and cadence.

Ideally this functionality would be incorporated into Strava's crop
tool someday.
