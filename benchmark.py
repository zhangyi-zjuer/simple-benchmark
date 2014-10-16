# coding:utf-8

import sys
import time
import urllib2
import re
import threading
import threadpool


class Benchmark(object):
    lock = threading.Lock()
    request_info = []

    def __init__(self, url_file, c=10, n=1000, request_timeout=60, verbose=True, host='127.0.0.1'):
        self.url_file = url_file
        self.c = c
        self.n = n
        self.request_timeout = request_timeout
        self.verbose = verbose
        self.host = host

    def get_url(self, line):
        if not self.host:
            return line
        return re.sub(r'^http://.*?/', 'http://%s/' % self.host, line)

    def load_query(self):
        queries = []
        current_n = 0

        with open(self.url_file, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) < 10:
                    continue
                queries.append(self.get_url(line))
                current_n += 1
                if current_n >= self.n:
                    break

        return queries

    def send_request(self, url):
        request_start = time.time()
        response = None
        request_success = False
        try:
            request = urllib2.urlopen(url, timeout=self.request_timeout)
            response = request.read()
            request_success = True
        except:
            pass
        request_end = time.time()
        request_use = request_end - request_start

        self.lock.acquire()

        self.request_info.append((request_success, url, request_start, request_end, request_use ))

        # show request vervose
        if self.verbose:
            print '%d\ttake:%dms\t%s' % (len(self.request_info), (request_end - request_start) * 1000, url)

        if len(self.request_info) % 100 == 0:
            print "Process reqeusts: %d" % len(self.request_info)

        self.lock.release()
        return response

    def post_all_requests(self):
        print "Benchmarking start (be patient) ..."
        queries = self.load_query()
        pool = threadpool.ThreadPool(self.c)
        reqs = threadpool.makeRequests(self.send_request, queries)
        [pool.putRequest(req) for req in reqs]
        pool.wait()

    def get_all_request_info(self):
        return self.request_info

    def get_benchmark_result(self):
        total_request = len(self.request_info)
        if total_request < 1:
            return 'No request send!'

        begin = sys.float_info.max
        end = sys.float_info.min
        fail = []
        total_request_time = 0.0

        for ele in self.request_info:
            is_success, url, t0, t1, t = ele

            if t0 < begin:
                begin = t0

            if t1 > end:
                end = t1

            total_request_time += t

            if not is_success:
                fail.append(url)

        concurrency_level = self.c
        time_taken_for_test = end - begin
        failed_request = len(fail)
        requests_per_seconds = total_request / time_taken_for_test
        time_per_request = total_request_time / total_request
        time_per_request_across_all = time_taken_for_test / total_request

        result = """
            Concurrency Level:      %d
            Time taken for tests:   %.3f second
            Total requests:         %d
            Failed requests:        %d
            Requests per second:    %.2f [#/sec] (mean)
            Time per request:       %.3f [ms] (mean)
            Time per request:       %.3f [ms] (mean, across all concurrent requests)
        """.strip()

        return '\n' + re.sub(r'(?m)^\s+', '', result) % (concurrency_level, time_taken_for_test, total_request,
                                                         failed_request, requests_per_seconds, time_per_request * 1000,
                                                         time_per_request_across_all * 1000)