#!/usr/bin/env python
from pynagios import Plugin, Response, make_option, CRITICAL, UNKNOWN, OK
import urllib2
import json


class FacedetectCheck(Plugin):
    port = make_option('-p', '--port', type='int', default=4000,
                       help='Use the following port')
    use_ssl = make_option('-S', '--use-ssl', action='store_false',
                          default=False, help="Use HTTPS instead of HTTP")
    expected = make_option('-e', '--expected', type='str', default=None,
                           help="Expect the following string in response")

    def check(self):
        hostname = self.options.hostname
        port = self.options.port
        use_ssl = self.options.use_ssl
        expected = self.options.expected
        timeout = self.options.timeout if self.options.timeout > 0 else 10

        if not hostname:
            return Response(UNKNOWN, 'Hostname is missing')

        url = "http%s://%s:%s/status" % ('s'[:use_ssl], hostname, port)
        try:
            f = urllib2.urlopen(url, timeout=timeout)
            response = json.load(f)
        except urllib2.URLError, e:
            return Response(CRITICAL, e.reason[1])

        if not response:
            return Response(CRITICAL, 'No data received')

        status = response.pop('status')
        ret = OK
        if expected and expected not in status:
            ret = CRITICAL

        result = Response(ret, status)

        for k, v in response.items():
            result.set_perf_data(k, int(v))

        return result


if __name__ == "__main__":
    FacedetectCheck().check().exit()
