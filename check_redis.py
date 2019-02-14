#!/usr/bin/env python3

"""
check_redis.py: Nagios plugin for checking a redis server.

Author: Steffen Zieger <me@saz.sh>
License: GPL
Version: 1.0
"""

from optparse import OptionParser
import sys
import redis

# Constants
EXIT_OK = 0
EXIT_WARN = 1
EXIT_CRIT = 2
EXIT_UNKNOWN = 3


class RedisCheck(object):
    def __init__(self, host, port=6379, password=None, clientsWarn=None,
                 clientsCrit=None, memWarn=None, memCrit=None, upWarn=None,
                 upCrit=None, slavesWarn=None, slavesCrit=None):
        self.status = False
        self.message = False
        self.host = host
        self.port = port
        self.password = password
        self.clientsWarn = clientsWarn
        self.clientsCrit = clientsCrit
        self.slavesWarn = slavesWarn
        self.slavesCrit = slavesCrit
        self.memWarn = float(memWarn)
        self.memCrit = float(memCrit)
        self.upWarn = upWarn
        self.upCrit = upCrit
        self._fetchInfo()

    def _setStatus(self, status):
        """ Set the status only, if new status is not lower than current status"""
        if not self.status == EXIT_CRIT or not self.status == EXIT_WARN:
            self.status = status

    def _setMessage(self, message):
        if self.message:
            self.message += ", "
            self.message += message
        else:
            self.message = message

    def _exit(self):
        if hasattr(self, 'info'):
            print (self.message + self._getPerfData())
        else:
            print (self.message)
        sys.exit(self.status)

    def _fetchInfo(self):
        try:
            self.info = redis.Redis(host=self.host, port=self.port,
                                    password=self.password).info()
        except redis.ConnectionError:
            self._setStatus(EXIT_CRIT)
            self._setMessage("Can't connect to %s:%s" % (self.host, self.port))
            self._exit()

    def getStatus(self):
        return self.status

    def _getPerfData(self):
        "Returns various perf data values for graphs in Nagios"
        return "|uptime=%ss;%s;%s,connectedClients=%s;%s;%s," \
                "connectedSlaves=%s;%s;%s,usedMemory=%sMB;%s;%s" % \
                (self.getUptime()['s'], self.upWarn, self.upCrit,
                 self.getConnectedClients(), self.clientsWarn,
                 self.clientsCrit, self.getConnectedSlaves(),
                 self.slavesWarn, self.slavesCrit,
                 self.getUsedMem(), self.memWarn, self.memCrit)

    def getUptime(self):
        uptime = int(self.info['uptime_in_seconds'])

        ret = {}
        ret['d'] = uptime / 86400
        ret['h'] = (uptime % 86400) / 3600
        ret['m'] = (uptime % 3600) / 60
        ret['s'] = uptime

        return ret

    def getConnectedClients(self):
        return self.info['connected_clients']

    def getConnectedSlaves(self):
        return self.info['connected_slaves']

    def getUsedMem(self):
        return "%.2f" % float(self.info['used_memory'] / 1024.0 / 1024.0)

    def getLastSave(self):
        return self.info['last_save_time']

    def checkUptime(self):
        uptime = self.getUptime()

        if uptime['s'] < self.upCrit:
            self._setMessage("Uptime is %s seconds" % (uptime['s']))
            self._setStatus(EXIT_CRIT)
        elif uptime['s'] < self.upWarn:
            self._setMessage("Uptime is %s minutes" % (uptime['m']))
            self._setStatus(EXIT_WARN)
        else:
            days = 'days'
            if uptime['d'] == 1:
                days = 'day'
            self._setMessage("Uptime is %s %s, %s:%s h" % (uptime['d'], days,
                                                            uptime['h'],
                                                            uptime['m']))
            self._setStatus(EXIT_OK)

    def checkMemory(self):
        mem = self.getUsedMem()

        if float(mem) < self.memCrit:
            ret = EXIT_CRIT
        elif float(mem) < self.memWarn:
            ret = EXIT_WARN
        else:
            ret = EXIT_OK

        self._setStatus(ret)
        self._setMessage("Used Memory: %s MB" % (mem))

    def checkConnectedClients(self):
        clients = self.getConnectedClients()

        if clients > self.clientsCrit:
            ret = EXIT_CRIT
        elif clients > self.clientsWarn:
            ret = EXIT_WARN
        else:
            ret = EXIT_OK

        self._setStatus(ret)
        self._setMessage("Connected Clients: %s" % (clients))

    def checkConnectedSlaves(self):
        slaves = self.getConnectedSlaves()

        if slaves < self.slavesCrit:
            ret = EXIT_CRIT
        elif slaves < self.slavesWarn:
            ret = EXIT_WARN
        else:
            ret = EXIT_OK

        self._setStatus(ret)
        self._setMessage("Connected Slaves: %s" % (slaves))

    def runChecks(self):
        self.checkUptime()
        self.checkMemory()
        self.checkConnectedClients()
        self.checkConnectedSlaves()

    def check(self):
        self.runChecks()
        self._exit()
        



def main():
    redisCheck = RedisCheck('localhost', memWarn=10, memCrit=20, upWarn=900,
                            upCrit=60, clientsWarn=1, clientsCrit=2,
                            slavesWarn=0, slavesCrit=0)

    redisCheck.check()

if __name__ == '__main__':
    main()
