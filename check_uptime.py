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


def getUptime():
    """ Returns the uptime in seconds and split in
    days, hours and minutes.
    """
    MINUTE = 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24

    uptime = float(open("/proc/uptime").read().split()[0])
    days = int(uptime / DAY)
    hours = int((uptime % DAY) / HOUR)
    minutes = int((uptime % HOUR) / MINUTE)

    return uptime, days, hours, minutes


def checkUptime(warn, crit):
    """ Checks the uptime against WARN and CRIT values and
    returns an exit state and a message.
    """
    uptime, days, hours, minutes = getUptime()

    # Convert WARN and CRIT from minutes to seconds
    warn = warn * 60
    crit = crit * 60
    
    if uptime < crit:
        ret = EXIT_CRIT
    elif uptime < warn:
        ret = EXIT_WARN
    else:
        ret = EXIT_OK

    msg = "Uptime is %s days, %s:%s|uptime=%ss;%s;%s" % (days, hours,
                                                        minutes,
                                                        int(uptime),
                                                        warn, crit)

    return ret, msg


def main():
    # Validate arguments
    usage = "Usage: %prog -w WARN -c CRIT"
    description = "Checks uptime if lower than CRIT or WARN"
    parser = OptionParser(usage, description=description)
    parser.add_option("-w", "--warn", dest="warn", type="int", 
                help="Time in minutes that triggers a warning state.")
    parser.add_option("-c", "--crit", dest="crit", type="int",
                help="Time in minutes that triggers a critical state.")

    (options, args) = parser.parse_args()

    if options.warn and options.crit:
        (ret, msg) = checkUptime(options.warn, options.crit)
        print msg
        sys.exit(ret)
    else:
        parser.error("Insufficient arguments")


if __name__ == '__main__':
    main()
