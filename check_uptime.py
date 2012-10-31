#!/usr/bin/env python

"""
check_uptime.py: Nagios plugin for uptime check on Linux systems.

Author: Steffen Zieger <me@saz.sh>
License: GPL
Version: 1.0
"""

from optparse import OptionParser
import sys

# Constants
EXIT_OK = 0
EXIT_WARN = 1
EXIT_CRIT = 2
EXIT_UNKNOWN = 3


def getUptime(use_stdin=False):
    """ Returns the uptime in seconds and split in
    days, hours and minutes.
    """
    MINUTE = 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24

    if use_stdin:
        input = sys.stdin.read()
    else:
        with open('/proc/uptime', 'r') as f:
            input = f.read()

    d = {}
    d['uptime'] = float(input.split()[0])
    d['days'] = int(d['uptime'] / DAY)
    d['hours'] = int((d['uptime'] % DAY) / HOUR)
    d['minutes'] = int((d['uptime'] % HOUR) / MINUTE)

    return d


def checkUptime(warn, crit, uptime):
    """ Checks the uptime against WARN and CRIT values and
    returns an exit state and a message.
    """
    # Convert WARN and CRIT from minutes to seconds
    uptime['warn'] = warn * 60
    uptime['crit'] = crit * 60

    if uptime['uptime'] < uptime['crit']:
        ret = EXIT_CRIT
    elif uptime['uptime'] < uptime['warn']:
        ret = EXIT_WARN
    else:
        ret = EXIT_OK

    msg = "Uptime is %(days)dd %(hours)dh %(minutes)dm|uptime=%(uptime)ds;%(warn)d;%(crit)d" % uptime

    return ret, msg


def main():
    # Validate arguments
    usage = "Usage: %prog -w WARN -c CRIT"
    description = "Checks uptime if lower than CRIT or WARN"
    parser = OptionParser(usage, description=description)
    parser.add_option("-w", "--warn", dest="warn", type="int", default=300,
                      help="Time in minutes that triggers a warning state.")
    parser.add_option("-c", "--crit", dest="crit", type="int", default=60,
                      help="Time in minutes that triggers a critical state.")
    parser.add_option("-s", "--stdin", dest="use_stdin", action="store_true",
                      help="Read uptime data from stdin")

    (options, args) = parser.parse_args()

    if options.warn and options.crit:
        uptime_data = getUptime(options.use_stdin)
        (ret, msg) = checkUptime(options.warn, options.crit, uptime_data)
        print msg
        sys.exit(ret)
    else:
        parser.error("Insufficient arguments")


if __name__ == '__main__':
    main()
