#!/usr/bin/env python
from pynagios import Plugin, Response, make_option, CRITICAL, UNKNOWN, OK, \
    WARNING
import xmlrpclib
import socket


class SupervisordXmlRpcCheck(Plugin):
    port = make_option('-p', '--port', type='int', default=9080,
                       help='Use the following port for XML-RPC connection')
    username = make_option('-u', '--user', type='str', default=None,
                           help='Username for XML-RPC connection')
    password = make_option('-P', '--password', type='str', default=None,
                           help='Password for XML-RPC connection')

    def check(self):
        hostname = self.options.hostname
        port = self.options.port
        username = self.options.username
        password = self.options.password
        timeout = self.options.timeout if self.options.timeout > 0 else 10

        if not hostname:
            return Response(UNKNOWN, 'Hostname is missing!')

        if username and password:
            auth = '%s:%s@' % (username, password)
        else:
            auth = ''

        procs = None
        try:
            url = "http://%s%s:%s" % (auth, hostname, port)
            socket.setdefaulttimeout(timeout)
            s = xmlrpclib.ServerProxy(url)
            procs = s.supervisor.getAllProcessInfo()
        except xmlrpclib.Fault, e:
            return Response(UNKNOWN, "getAllProcessInfo: %s" % e.faultString)
        except (socket.gaierror, socket.timeout, socket.error), e:
            return Response(CRITICAL, "%s: %s" % (hostname, e))

        processes = {'STOPPED': [], 'STARTING': [], 'RUNNING': [],
                     'BACKOFF': [], 'STOPPING': [], 'EXITED': [],
                     'FATAL': [], 'UNKNOWN': []}
        for proc in procs:
            processes[proc['statename']].append(proc['name'])

        ret = OK
        for state in ('STOPPING', 'STARTING'):
            if len(processes[state]):
                ret = WARNING

        if len(processes['UNKNOWN']):
            ret = UNKNOWN

        for state in ('EXITED', 'BACKOFF', 'FATAL'):
            if len(processes[state]):
                ret = CRITICAL

        result = Response(ret, processes)

        msg = []
        for k, v in processes.items():
            if v:
                msg.append('%s: %s' % (k, ', '.join(v)))
            result.set_perf_data(k, len(v))

        result.message = ' '.join(msg)
        return result

if __name__ == '__main__':
    SupervisordXmlRpcCheck().check().exit()
